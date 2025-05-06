"""
serverless_bloom_prompt_validation_mixin.py
-------------------------------------------
Version 1.0, updated on 2025-01-25

"""

from pprint import pprint
from typing import Dict

from pandas import DataFrame

from src.data_structures.history import History
from src.sentiment_analysis.retrieval.custom_exceptions import (
    PromptInvalidException
)
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.query_processor import QueryProcessor
from src.utils.data_utils import is_none_or_empty
from type_aliases import PromptsDictType


class ServerlessBloomPromptValidationMixin(LoggingMixin):
    """
    ServerlessBloomPromptValidationMixin class.

    A mixin class that provides validation methods for processing and
    validating prompts in a serverless Bloom-based application.

    This mixin includes properties and methods that support the validation of
    sentiment analysis prompts. It handles setting prompts and
    validation flags, as well as processing data batches with the appropriate
    language configurations.

    Attributes
    ----------
    prompts : PromptsDictType
        The prompts used for generating query-specific prompts.

    Methods
    -------
    process_query(payload: Dict[str, str]) -> str | int:
        Processes a single query by sending it to the 'QueryProcessor'.

    validate_prompt(language: str = 'en', prompts: PromptsDictType = None)
            -> None:
        Validates a prompt.

    """

    # region --- Properties

    @property
    def prompts(self) \
            -> PromptsDictType:
        """
        Gets the prompts used for generating query-specific prompts.

        Returns
        -------
        PromptsDictType
            A dictionary containing prompts for prompt generation.

        """

        return getattr(self, '_prompts', None)

    @prompts.setter
    def prompts(self, prompts: PromptsDictType) \
            -> None:
        """
        Sets the prompts used for generating query-specific prompts.

        Parameters
        ----------
        prompts : PromptsDictType
            A dictionary of prompts to generate prompts.

        """

        setattr(self, '_prompts', prompts)

    @property
    def invalid_prompts(self) \
            -> History:
        if is_none_or_empty(getattr(self, '_invalid_prompts', None)):
            self._initialize_invalid_prompts_history()

        return getattr(self, '_invalid_prompts', History())

    def _initialize_invalid_prompts_history(self) \
            -> None:

        invalid_prompts_history = History(
            name = f'{self.name}_'
                 f'invalid_prompts_v_'
                 f'{self.config.get('version')}'
        )

        setattr(self, '_invalid_prompts', invalid_prompts_history)


    # endregion --- Properties

    # region --- Public Methods

    def validate_prompt(
            self,
            language: str = 'en',
            prompt: Dict[str, str] = None
    ) -> bool:
        """
        Validates a single prompt.

        Validates a prompt by setting language and prompts, iterating
        through data batches, and processing sentiment analysis.

        Parameters
        ----------
        language : str
           The language for prompt validation (default is 'en').

        prompt : Dict[str, str]
           Prompt consisting of different parts whose names constitute the
           keys in the dictionary and whose values are the values of the
           dictionary's entries.

        Returns
        -------
        bool
            True if the prompt was validated, False otherwise.

        """

        # Save the parameters as properties so that they can be used from
        # the different methods.

        self.language = language

        # Wrap the prompt in the expected prompts dictionary
        self.prompts = {"1": prompt}

        # The number of batches to process for each query variant
        # The configuration is a property of the ServerlessBloom class this
        # mixin is mixed into.
        self.target_n_batches = self.config.get("n_batches")

        print(f"Language: {language}")

        # Iterate through the subsets to find the subset for the current
        # language
        for subset_name in self.suite.subset_names:
            if f"_{language}_" in subset_name:
                # Once a subset with the specified language is found,
                # it can be processed:

                samples = self.samples_manager.get_samples(language)

                self.data = samples.df

                # Add the queries of the chunks
                self._add_query_col()

                if not self._retrieve_sentiment_for_validation():
                    # Collect invalid prompts in special file
                    self.invalid_prompts.add(prompt)
                    return False

                msg = "Prompt is valid!"
                self._log(msg, 'info')

                # The subset having been processed, the subset_names loop
                # can be quit:
                break

        return True

    def process_query(
            self,
            payload: Dict[str, str],
            expected_answer: str
    ) -> str | int:
        """
        Processes a single query by sending it to the 'QueryProcessor'.

        Parameters
        ----------
        payload : Dict[str, str]
            A dictionary containing the query inputs.

        expected_answer : str
            The expected answer for the query.

        Returns
        -------
        str | int
            The processed answer or error code.

        """

        query_processor = QueryProcessor(payload)
        answer = query_processor.process_query()
        if answer != expected_answer:
            msg = "Wrong answer: '%s' instead of '%s'" % (
                answer, expected_answer
            )

            raise PromptInvalidException(msg)

        return answer

    # endregion --- Public Methods

    # region --- Protected Methods
    def _add_query_col(self) \
            -> None:
        """
        Composes the queries and inserts them in a column of the DataFrame.

        Composes the prompts from their ingredients and inserts the
        corresponding prompts for each sample in a separate column
        corresponding to the respective query variant.

        """

        df = self.data.copy()

        for _, val in self.prompts.items():
            df.loc[:, 'query_1'] = df.apply(
                lambda row: (
                    f"{val.get('before_sentence')}"
                    f"'{row['sentence_normalized']}'"
                    f"{val.get('before_mention')}"
                    f"{row['mention']}\n"
                    f"{val.get('scale')}"
                    f"{val.get('question')}"
                    f"{val.get('answer_before_mention')}"
                    f"{row['mention']}"
                    f"{val.get('answer_start')}"
                ),
                axis=1
            )

        self.data = df

    def _retrieve_sentiment_for_validation(self) \
            -> bool:
        """
        Retrieves the sentiment predictions for the data.

        This method simulates the retrieval of the sentiment predictions for
        the samples in the data DataFrame.

        Returns
        -------
        bool
            Whether the query was successfully processed and returned the
            correct answers.

        """

        return self._process_query_for_validation()

    def _process_query_for_validation(self) \
            -> bool:
        """
        Processes a query for validation purposes.

        Processes a query in a single batch, sending the prompt of each row
        to the API, collecting and reporting failed answers and returning the
        result for further validation.

        Returns
        -------
        bool
            Whether the query was successfully processed and returned the
            correct answers.

        """

        self.failed_answers = []

        # Extract random batch from DataFrame
        batch_df = self._get_batch_df()

        msg = "Validating prompt"
        self._log(msg, "info", "Validating prompt")

        # Apply the query function to each row in the batch
        try:
            batch_df['answer_1'] = batch_df.apply(
                lambda row: (
                    self.process_query({"inputs": row["query_1"]},
                                       expected_answer=row["polarity"])
                ),
                axis=1
            )

        except PromptInvalidException:
            return False

        self._report_failed_answer()
        return True

    def _get_batch_df(self) \
            -> DataFrame:
        """
        Selects a random batch of data. based on the batch size specified in
        the configuration.

        Selects a random batch of data based on the batch size specified in
        the configuration.

        - For a batch size of 1, a single random row from 'self.data' is
          selected.
        - For a batch size of 3, random samples with three distinct
          polarities are selected from the dataset.

        Returns
        -------
        DataFrame
            A DataFrame containing the selected batch of data, filtered based
            on the specified batch size and polarity criteria.

        """

        # Set default return value
        batch_df = self.data.copy()

        match self.config.get('batch_size'):
            case 1:
                # Select a random sample
                batch_df = self.data.sample(n=1)
            case 3:
                # Select 3 random samples with 3 different polarities
                batch_df = self.data.groupby("polarity").apply(
                    lambda x: x.sample(1)
                ).droplevel(0)

        return batch_df

    def _report_failed_answer(
            self
    ) -> None:
        """
        Reports an answer that failed to be of the expected type.

        Reports answers that failed to meet expected response types by
        logging the count and details of failed queries.

        """

        n_failed = len(self.failed_answers)

        if n_failed > 0:
            print(f"{n_failed} unexpected answer to query:")
            pprint(self.failed_answers)

    # endregion --- Protected Methods
