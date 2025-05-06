"""
balanced_samples_provider.py
----------------------------
Version 1.0, updated on 2025-01-11

"""

from typing import TYPE_CHECKING, Dict

from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.sentiment_analysis.samples.samples_provider import SamplesProvider
from src.utils.data_utils import is_none_or_empty

if TYPE_CHECKING:
    from src.sentiment_analysis.samples.samples_manager import SamplesManager


class BalancedSamplesProvider(SamplesProvider):
    """
    BalancedSamplesProvider class.

    This class manages the balancing of samples to ensure uniform sentiment
    distribution across samples.

    Attributes
    ----------
    balanced_samples : Dict[str, src.data_structures.my_data_frame.MyDataFrame]
        The balanced samples for all languages.

    Methods
    -------
    get_samples(self)
            -> Dict[str, src.data_structures.my_data_frame.MyDataFrame]:
        Retrieves and returns samples for sentiment analysis.

    """

    def __init__(
            self,
            samples_manager: "SamplesManager"
    ):
        """
        Constructor.

        Initializes a new BalancedSamplesProvider instance with a
        SamplesManager instance.

        Parameters
        ----------
        samples_manager : SamplesManager
            The SamplesManager instance that called the
            BalancedSamplesProvider to delegate the retrieval of balanced
            samples.

        """

        super().__init__(samples_manager)

        self._balanced_samples = None

    # region --- Properties
    @property
    def balanced_samples(self) \
            -> Dict[str, MyDataFrame]:
        """
        Returns the balanced samples for all languages.

        Returns the balanced samples for all languages that the LLM and the
        data suite have in comman.

        Returns
        -------
        Dict[str, MyDataFrame]:
            The balanced samples, where the key is the language and the
            value is a MyDataFrame object that contains a DataFrame with the
            balanced samples for the language.

        """

        if is_none_or_empty(self._balanced_samples):
            raise CriticalException(
                self.logger,
                "No balanced samples found! Cannot proceed."
            )

        return self._balanced_samples

    @balanced_samples.setter
    def balanced_samples(self, samples: Dict[str, MyDataFrame]) \
            -> None:
        """
        Sets the balanced samples for all languages.

        Sets the balanced samples for all languages that the LLM and the
        data suite have in comman..

        Parameters
        ----------
        samples : Dict[str, MyDataFrame]
            The balanced samples to set the property with, where the key is the
            language and the value is the balanced samples for the respective
            language.

        """

        self._balanced_samples = samples

    # endregion --- Properties

    # region --- Public Methods

    def get_samples(self) \
            -> Dict[str, MyDataFrame]:
        """
        Retrieves the balanced samples for all languages.

        Retrieves the balanced samples for all languages that the LLM and the
        data suite have in comman, either by loading previously saved data
        from disk or by creating balanced samples anew from the subsets of
        the active data source suite.

        Returns
        -------
        Dict[str, MyDataFrame]:
            The unbalanced samples, where the key is the language and the
            value is a MyDataFrame object that contains a DataFrame with the
            unbalanced samples for the language.

        """

        if self._load_balanced_samples():
            samples = self.balanced_samples
        else:
            samples = self._create_balanced_samples()

        return samples

    # endregion --- Public Methods

    # region --- Protected Methods
    def _load_balanced_samples(self) \
            -> bool:
        """
        Loads the balanced datasets for all languages if available.

        Loads balanced datasets that have been saved to disk previously.

        Notes
        -----
        To avoid the possibility of mixing language datasets with
        different sample ids, loading is done for all languages concerned or
        for none. If, for one language, no balanced samples can be found,
        the loading is considered to have failed altogether and all files
        will have to be re-created.

        """

        balanced_samples: Dict[str, MyDataFrame] = {}

        if is_none_or_empty(self._balanced_samples):

            for language in self.samples_manager.languages:
                samples = self._load_balanced_samples_for_language(language)
                if is_none_or_empty(samples):
                    return False
                balanced_samples[language] = samples

            self.balanced_samples = balanced_samples

        return True

    def _load_balanced_samples_for_language(self, language: str) \
            -> MyDataFrame:
        """
        Loads a balanced dataset for the specified language if available.

        Parameters
        ----------
        language : str
            The language for which the dataset should be loaded.

        Returns
        -------
        MyDataFrame
            The balanced dataset loaded from disk.

        Notes
        -----
        If no data was found on disk, the Dataframe inside the
        returned MyDataFrame object is empty. The caller should check if the
        MyDataFrame contains data.

        """

        my_df = MyDataFrameFactory.create(
            name=self._compose_dataset_name_for_language(language)
        )

        if my_df.can_load():
            my_df.load()

        return my_df

    def _compose_dataset_name_for_language(self, language: str) \
            -> str:
        """
        Returns a name for a language-specific balanced dataset.

        Returns a name for the language-specific balanced dataset that is
        beeing loaded or created.

        Composes the name from the suite's name, the language and the number
        of the balanced samples per language.

        Parameters
        ----------
        language :  str
            The language of the language-specific dataset.

        """

        man = self.samples_manager

        return f"{man.suite_name}_{language}_balanced_{man.balance}"

    def _create_balanced_samples(self) \
            -> Dict[str, MyDataFrame]:
        """
        Retrieves or creates balanced samples datasets for all languages.

        Retrieves balanced samples for the first language as the
        reference, and then computes corresponding balanced samples for other
        languages using this reference.

        Returns
        -------
        Dict[str, MyDataFrame]
            A dictionary with the balanced samples for all languages,
            where the keys are the languages and the values are MyDataFrame
            objects with the balanced samples for the corresponding languages.

        Notes
        -----
        Uses '_get_reference_samples' and '_get_other_balanced_samples' to
        create or retrieve balanced datasets.

        """

        languages = self.samples_manager.languages
        balanced_samples: Dict[str, MyDataFrame] = {}

        # For the first language, get the balanced samples as reference samples
        reference_samples = self._get_reference_samples(
            languages[0]
        )

        balanced_samples[languages[0]] = reference_samples

        # For all other languages, get the corresponding balanced samples
        for language in languages[1:]:
            other_balanced_samples = self._get_other_balanced_samples(
                reference_samples,
                language
            )
            balanced_samples[language] = other_balanced_samples

        return balanced_samples

    def _get_reference_samples(self, language: str) \
            -> MyDataFrame:
        """
        Creates a balanced sample MyDataFrame to use as reference samples.

        Creates a balanced sample MyDataFrame with the specified number of
        samples per sentiment category to use as reference samples
        for the rest of the languages.

        Parameters
        ----------
        language : str
            The language to get the reference samples from.

        Returns
        -------
        MyDataFrame
            The collection of reference samples in the given language.

        """

        man = self.samples_manager
        n_samples_per_sentiment = man.balance

        my_df = man.unbalanced_samples[language].copy()

        # Replace the numerical sentiment values by textual labels
       # my_df.df = normalize_polarities(my_df.df)

        # Create an empty list for sentiment-specific MyDataFrames
        sentiment_specific_my_dfs = []

        # Iterate through the list of different sentiment labels:
        sentiments = ['positive', 'negative', 'neutral']

        for sentiment in sentiments:
            # Get all rows with the given sentiment
            filtered = self._filter_by_sentiment(
                my_df, sentiment
            )

            # Reduce the number of rows to the target number of samples per
            # sentinment
            filtered_and_reduced = self._reduce_to_max_n_rows(
                filtered, n_samples_per_sentiment
            )

            # Add the sentiment-specific samples to the list of
            # sentiment-specific MyDataFrames
            sentiment_specific_my_dfs.append(
                filtered_and_reduced
            )

        # Join the 3 sentiment-specific MyDataFrames in one MyDataFrame
        balanced_my_df = sentiment_specific_my_dfs[0].do_with_row(
            'join',
            my_df_lst=sentiment_specific_my_dfs[1:]
        )
        # Shuffle the samples in the resulting MyDataFrame
        balanced_my_df.df = balanced_my_df.do_with_row('shuffle')
        balanced_my_df.name = self._compose_dataset_name_for_language(language)
        balanced_my_df.save()

        return balanced_my_df

    def _get_other_balanced_samples(
            self,
            reference_samples: MyDataFrame,
            language: str
    ) -> MyDataFrame:
        """
        Creates a balanced sample MyDataFrame based on an existing MyDataFrame.

        Given a reference MyDataFrame in one language, another MyDataFrame
        ist extracted from a data subset in another language, basing the
        choice of rows on the indices of the reference MyDataFrame.

        Parameters
        ----------
        reference_samples : MyDataFrame
            The reference sample MyDataFrame to base the balance on.

        Returns
        -------
        MyDataFrame
            A balanced sample DataFrame with the same distribution as the
            reference.

        """

        man = self.samples_manager

        my_df = man.unbalanced_samples[language].copy()

        my_df.df = my_df.do_with_row(
            'extract_rows_by_other_indices',
            other=reference_samples
        )

        my_df.name = self._compose_dataset_name_for_language(language)

        my_df.save()
        return my_df

    def _reduce_to_max_n_rows(self, my_df: MyDataFrame, max_n_rows: int) \
            -> MyDataFrame:
        """
        Reduces the MyDataFrame to a specified maximum number of rows.

        Reduces the DataFrame in the MyDataFrame to a specified maximum
        number of rows.

        Parameters
        ----------
        my_df : MyDataFrame
           MyDataFrame containing the DataFrame to reduce.

        max_n_rows : int
           Maximum number of rows to retain.

        Returns
        -------
        MyDataFrame
           The MyDataFrame with reduced DataFrame.

        """

        local_my_df = my_df.copy()

        local_my_df.df = local_my_df.do_with_row(
            'reduce_n_rows',
            max_n_rows=max_n_rows
        )

        return local_my_df

    def _filter_by_sentiment(self, my_df: MyDataFrame, sentiment: str) \
            -> MyDataFrame:
        """
        Extracts the rows with the given sentiment from all samples.

        Parameters
        ----------
        my_df : MyDataFrame
            A MyDataFrame with all sentiment-labeled samples.

        sentiment : str
            Sentiment by which to filter the MyDataFrame.

        Returns
        -------
        MyDataFrame
            The extracted sentiment-specific samples, in random order.

        """

        local_my_df = my_df.copy()

        local_my_df.df = local_my_df.do_with_row(
            'extract_rows_by_col_value',
            col_name='polarity',
            col_value=sentiment
        )

        return local_my_df

    def _shuffle(self, my_df: MyDataFrame) \
            -> MyDataFrame:
        """
        Randomly shuffles the rows in the DataFrame in the MyDataFrame object.

        Parameters
        ----------
        my_df : MyDataFrame
            MyDataFrame with the DataFrame to shuffle.

        Returns
        -------
        MyDataFrame
            The MyDataFrame with the shuffled DataFrame.

        """

        local_my_df = my_df.copy()

        # Order the rows randomly
        local_my_df.df = local_my_df.do_with_row('shuffle')

        return local_my_df

    # endregion --- Protected Methods
