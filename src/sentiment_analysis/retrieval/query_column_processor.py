"""
query_column_processor.py
-------------------------
Version 1.0, updated on 2024-12-25

"""

import re
from math import floor
from pprint import pprint
from time import sleep
from typing import Dict

from pandas import DataFrame

from logger import Logger
from src.checkpoint_mixin import CheckpointMixin
from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.decorators.data_check_decorators import parameters_not_empty
from src.decorators.type_check_decorators import enforce_input_types
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    ChunkFinishedException,
    PromptInvalidException
)
from src.sentiment_analysis.retrieval.query_processor import QueryProcessor
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.utils.user_interaction_utils import (
    ask_continue_without_saving,
    ask_save_and_continue
)


class QueryColumnProcessor(LoggingMixin, CheckpointMixin):
    """
    QueryColumnProcessor class.

    This class handles query columns in batches, managing checkpoints,
    validating prompts, and saving results. It supports robust handling
    of interruptions and allows users to control how to proceed in case of
    errors or invalid query results.

    Attributes
    ----------
    answers_collection : set
        A set to collect unique answers from processed queries, used to
        validate prompts.

    can_save : bool
        Indicates whether the current results can be saved.

    checkpoint : Checkpoint
        The checkpoint.

    chunk_size : int
        The size of the chunk (i.e. the number of query columns), according to
        the sentiment analysis configuration.

    chunk_start_at_query_col_nr : int
        The query column number with which to start a chunk.

    config : SentimentAnalysisConfig
        Configuration settings for the sentiment analysis.

    language : str
        The language code corresponding to the language of the samples to
        process.

    query_counter : int
        Class-level counter to track the number of queries processed
        across all instances.

    samples : MyDataFrame
        A MyDataFrame with the samples whose query columns to process.


    Methods
    -------
    load_samples() -> None:
        Loads the samples if they are not already loaded.

    process_query(payload: Dict[str, str]) -> str | int:
        No description available.

    process_query_column(query_col_nr: int) -> None:
        Processes the specified query column.

    process_query_columns() -> None:
        Processes the different query types in a chunk.

    """

    """
    Query counter (class variable).

    Use as "QueryColumnProcessor.query_counter" to keep it alive across
    different instances of this class. This enables the user to see how many
    queries in a row are sent to the LLM's API.
    """
    query_counter: int = 0

    # Used to keep track of the number of queries processed in a given query
    # column.
    prompt_specific_query_counter: int = 0

    @parameters_not_empty()
    @enforce_input_types
    def __init__(
            self,
            language: str,
            samples: MyDataFrame,
            chunk_start_at_query_col_nr: int = 1,
    ):
        """
        Initializes the QueryColumnProcessor with the specified parameters.

        Parameters
        ----------
        language : str
           Language code.

        samples : MyDataFrame
            The MyDataFrame with the samples whose query columns to process.

        chunk_start_at_query_col_nr : int
            Defines the query column number with which to start a chunk.
            This number is needed to set the corresponding checkpoint and to
            calculate the end of the range needed to iterate through the query
            columns in the process_query_columns method.

        """

        # Initialize checkpoint with start query column number:
        self.chunk_start_at_query_col_nr: int = chunk_start_at_query_col_nr

        CheckpointMixin.__init__(
            self,
            element_type="batch",
            checkpoint_name=f"{samples.name}_query_col_checkpoint"
        )
        self._set_checkpoint(chunk_start_at_query_col_nr)

        self._samples: MyDataFrame | None = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.language = language
        self.samples = samples

        # Configs used in this class
        self.config = SentimentAnalysisConfig()
        self.chunk_size = self.config.get('chunk_size')

        """
        Set to collect the different types of answers. 

        The number of collected items in this set enables to check the validity
        of the prompt in the query column. The number of different 
        answers should be 3 ('positive', 'negative' and 'neutral'). If this is
        not the case after a sufficient amount of rows has been treated, 
        the prompt is rejected as invalid.  

        """
        self.answers_collection = set()

        self._current_chunk_nr: int = 0
        self.can_save: bool = False

    # region --- Properties

    @property
    def samples(self) \
            -> MyDataFrame:
        """
        Gets the samples to process in batches.
        """

        if self._samples is None:
            return MyDataFrameFactory.create()

        return self._samples

    @samples.setter
    def samples(self, samples: MyDataFrame) \
            -> None:
        """
        Sets the samples to process in batches.
        """

        self._samples = samples

    # endregion --- Properties

    # region --- Public Methods

    def process_query_columns(self) \
            -> None:
        """
        Processes the different query types in a chunk.

        Creates a checkpoint at the end of each processed query type so that
        the program can resume after an interruption where it left off.

        """

        for query_col_nr in range(
                self._get_start_query_col_nr(),
                self.chunk_start_at_query_col_nr + self.chunk_size
        ):
            try:
                self.can_save = False

                self._reset_answers_collection()

                self.process_query_column(query_col_nr)

                # After the current query type has been processed and
                # saved successfully, the next query type number to start with
                # is written into the checkpoint file.
                self._set_checkpoint(query_col_nr + 1)

            except ChunkFinishedException as err:
                msg = "Going to proceed with chunk %d ..." % (
                        self._current_chunk_nr + 1
                )
                self._log(msg, 'info')
                raise ChunkFinishedException(msg) from err

            except Exception as err:
                # Log and handle unexpected errors
                msg = "Error processing query column %d: %s" % (
                    query_col_nr, str(err)
                )
                self._log(msg, 'error')
                raise

    def process_query_column(self, query_col_nr: int) \
            -> None:
        """
        Processes the specified query column.

        Processes the specified query column by applying the query logic
        to each row.

        Parameters
        ----------
        query_col_nr : int
            The number of the query column.

        Raises
        ------
        PromptInvalidException
            If the prompt in the column is deemed invalid.

        ChunkFinishedException
            If the "try" block raises a KeyError because all rows in the chunk
            have been processed.

        KeyError
            If the specified column does not exist in the DataFrame.

        """

        df = self.samples.df
        nr = query_col_nr

        msg = "Processing query column %d" % nr
        self._log(msg, 'info')

        try:
            # Apply the query method to each row in the DataFrame
            df[f'answer_{nr}'] = df.apply(
                lambda row: (
                    self.process_query({"inputs": row[f'query_{nr}']})
                ),
                axis=1
            )

            self._report_failed_answers(query_col_nr)
            self._save_col_result(df, query_col_nr)

        except PromptInvalidException:
            msg = ("Processing stopped for query column %d due to invalid "
                   "prompt." % query_col_nr)
            self._log(msg, 'info')

        except KeyError as err:
            self._set_current_chunk_nr(nr)
            msg = ("All prompts of chunk %d processed!" %
                   self._current_chunk_nr)
            self._log(msg, "info")
            raise ChunkFinishedException(msg) from err

        except Exception as err:
            msg = ("Unexpected error occured while processing the queries: "
                   "%s.") % str(err)
            self._log(msg, "error")
            raise

    def process_query(self, payload: Dict[str, str]) \
            -> str | int:
        """
        Processes a single query payload using the QueryProcessor.

        Parameters
        ----------
        payload : Dict[str, str]
            The input data for the query.

        Returns
        -------
        str | int
            The response from the QueryProcessor.

        Raises
        ------
        PromptInvalidException
            If the query is invalid when validation is performed.

        """

        query_processor = QueryProcessor(payload)
        answer = query_processor.process_query()

        # Try to add the answer to the set of answers. If it is not
        # contained in the set yet, it will be added.
        self.answers_collection.add(answer)

        self._keep_track()

        return answer

    # endregion --- Public Methods

    # region --- Protected Methods
    def _set_current_chunk_nr(self, query_col_nr: int) \
            -> None:
        """
        Updates the current chunk number based on the query column number.

        Parameters
        ----------
        query_col_nr : int
            The current query column number.

        """

        self._current_chunk_nr = floor(query_col_nr / self.chunk_size)

    def _keep_track(self) \
            -> None:
        """
        Outputs the number of the currently processed query in the console.

        If validation is required ('with_validation' parameter in
        SentimentAnalysisConfig is set to True), checks the validity of the
        prompt used in the query column and stops the execution of
        the query column processor if the prompt is revealed to be
        invalid.

        The prompt is esteemed to be invalid if, after a given amount
        of processed rows, the number of different answers in the answers
        set of the class is insufficient:
            - only one answer type after 50 rows
            - only two answer types after 100 rows

        In case the prompt is found to be invalid, its answers are
        not saved to the DataFrame.

        Raises
        ------
        PromptInvalidException
            If validation is required and the prompt is found to be
            invalid.

        Notes
        -----
        The _validate_batch_result and the _validate_half_batch methods only
        perform validation attempts if self.config.get('with_validation') is
        set to True.

        """

        batch_size = self.config.get('batch_size')

        self._update_query_counter()
        m = QueryColumnProcessor.query_counter
        n = QueryColumnProcessor.prompt_specific_query_counter

        if n > 0 and n % batch_size == 0:
            print(f"{str(n)} completed")

            try:
                self._validate_batch_result()
                QueryColumnProcessor.prompt_specific_query_counter = 0

            except PromptInvalidException as err:
                QueryColumnProcessor.prompt_specific_query_counter = 0
                raise PromptInvalidException(err) from err

        if m > 0 and m % 1000 == 0:
            print(f"{str(m / 1000)} k completed!")

        if n > 0 and n % 50 == 0:
            try:
                self._validate_half_batch()
            except PromptInvalidException as err:
                raise PromptInvalidException(err) from err

        if n > 0 and n % 10 == 0 and len(self.answers_collection) <= 1:
            print("Probably invalid query!")

    def _validate_half_batch(self):
        """
        Checks the validity of the prompt half-way through the batch.

        If validation is required, the batch results are verified in mid-batch.
        Results must have produced at least two different sentiment 
        classes. Otherwise, the prompt is discarded.

        Raises
        ------
        PromptInvalidException
            If validation is required and the prompt is found to be
            invalid.

        Notes
        -----
        The check in this method takes into account that answers may also be
        empty strings if no sentiment could be extracted from the LLM's
        response. If the answers include empty strings, the required number of
        answer categories must be increased by one

        """

        if self.config.get('with_validation'):

            threshold = 2

            # If empty strings are included in the answers: require at least
            # 3 different answers (increase the threshold by 1) 
            if "" in self.answers_collection:
                threshold += 1

            if len(self.answers_collection) < threshold:
                lst = list(self.answers_collection)
                msg = (
                    "Prompt is invalid as it only produces "
                    f"{lst} answers! "
                )
                self._log(msg, 'info')

                # Skip the rest of the rows
                QueryColumnProcessor.query_counter += 50

                raise PromptInvalidException(msg)

    def _validate_batch_result(self):
        """
        Checks the validity of the prompt at the end of the batch.

        If validation is required, the batch results are verified.
        Results must have produced all three different sentiment
        classes. Otherwise, the prompt is discarded.

        Raises
        ------
        PromptInvalidException
            If validation is required and the prompt is found to be
            invalid.

        Notes
        -----
        The check in this method takes into account that answers may also be
        empty strings if no sentiment could be extracted from the LLM's
        response. If the answers include empty strings, the required number of
        answer categories must be increased by one.

        """

        if self.config.get('with_validation'):
            threshold = 3

            # If empty strings are included in the answers: require at least
            # 4 different answers (increase the threshold by 1)
            if "" in self.answers_collection:
                threshold += 1

            if len(self.answers_collection) < threshold:
                lst = list(self.answers_collection)
                msg = (
                    "Prompt is invalid as it only produces "
                    f"{lst} answers! "
                )
                self._log(msg, 'info')
                raise PromptInvalidException(msg)

    def _update_query_counter(self) \
            -> None:
        """
        Increments the query counters by 1.

        Increments the query counters by 1 and outputs the overall
        query_counter to the console, thus monitoring the progress of the
        program.

        """

        QueryColumnProcessor.prompt_specific_query_counter += 1

        QueryColumnProcessor.query_counter += 1
        if QueryColumnProcessor.query_counter == 1:
            print(
                f"Starting at query {str(QueryColumnProcessor.query_counter)}"
            )
        else:
            print(f"{str(QueryColumnProcessor.query_counter)}")

    def _reset_answers_collection(self) \
            -> None:
        """
        Resets the answers_collection set.

        Resets the answers_collection set that collects unique answers from
        the queries.

        """

        self.answers_collection = set()

    def _report_failed_answers(self, query_nr: int) \
            -> None:
        """
        Reports any failed answers occured.

        Reports any failed answers occured during the processing of a query
        column.

        If the query column produced failed answers, the user is asked to
        decide whether to proceed and save the column result, to continue
        without saving or to stop the program altogether.

        Parameters
        ----------
        query_nr : int
            The number of the query column.

        """

        failed_answers = QueryProcessor.flush_failed_answers()

        n_failed = len(failed_answers)
        if n_failed > 0:
            msg = (f"{str(n_failed)} unexpected answers to "
                   f"query {str(query_nr)}:")
            self._log(msg, "info")

            pprint(failed_answers)

            self._ask_continue()
        else:
            self.can_save = True

    def _get_start_query_col_nr(self) \
            -> int:
        """
        Retrieves the query column number from which to start.

        Returns
        -------
        int
            The query column number.

        """

        return int(self.checkpoint.data)

    def _extract_chunk_nr_from_checkpoint_name(self) \
            -> int:
        """
        Extracts and returns the chunk number from the checkpoint's name.

        Returns
        -------
        int
            The chunk number

        """

        # Regex to find the number between underscores after "chunk"
        pattern = r'chunk_(\d+)_'
        match = re.search(pattern, self.checkpoint.name)
        chunk_nr = match.group(1)

        return int(chunk_nr)

    def _ask_continue(self) \
            -> None:
        """
        Asks the user if and how the program should continue.

        Asks the user to decide whether to proceed and save the column
        result, to continue without saving or to stop the program altogether.
        If the user decides to discard the column result, the can_save
        property of this class is set to false, otherwise to True.

        """

        if ask_save_and_continue():
            self.can_save = True
        else:
            if ask_continue_without_saving():
                self.can_save = False
            else:
                print("Please interrupt the execution of this program "
                      "manually!")
                # Wait 24 hours before continuing so that the user has the
                # opportunity to check the program status and stop its
                # execution.
                sleep(60 * 60 * 24)

    def _save_col_result(self, df: DataFrame, query_nr: int) \
            -> None:
        """
        Saves the results of the processed query column to the DataFrame.

        Parameters
        ----------
        df : DataFrame
            The DataFrame containing the results to save.

        query_nr : int
            The number of the query column.

        """

        if self.can_save:
            self.samples.df = df
            self.samples.save()

            self.can_save = False

        else:
            msg = "Result of query column %s is discarded." % str(query_nr)
            self._log(msg, 'info')

    # endregion --- Protected Methods
