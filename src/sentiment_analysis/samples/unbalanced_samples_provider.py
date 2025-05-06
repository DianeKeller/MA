"""
unbalanced_samples_provider.py
------------------------------
Version 1.0, updated on 2025-01-08

"""

from typing import TYPE_CHECKING, Dict, no_type_check

from pandas import DataFrame

from src.sentiment_analysis.sentiment_stats import normalize_polarities
from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.sentiment_analysis.samples.samples_provider import SamplesProvider, S
from src.utils.data_utils import is_none_or_empty

if TYPE_CHECKING:
    from src.sentiment_analysis.samples.samples_manager import SamplesManager


class UnbalancedSamplesProvider(SamplesProvider):
    """
    UnbalancedSamplesProvider class.

    This class manages and provides unbalanced samples from the subsets of the
    data suite that is set in the SamplesManager class.

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

        Initializes a new UnbalancedSamplesProvider instance with a
        SamplesManager instance.

        Parameters
        ----------
        samples_manager : SamplesManager
            The SamplesManager instance that called the
            BalancedSamplesProvider to delegate the retrieval of unbalanced
            samples.

        """

        super().__init__(samples_manager)

    # region --- Public Methods
    def get_samples(self) \
            -> Dict[str, MyDataFrame]:
        """
        Returns the unbalanced samples for all languages.

        Returns the unbalanced samples for all languages that the LLM and the
        data suite have in comman.

        Returns
        -------
        Dict[str, MyDataFrame]:
            The unbalanced samples, where the key is the language and the
            value is a MyDataFrame object that contains a DataFrame with the
            unbalanced samples for the language.

        """

        samples: Dict[str, MyDataFrame] = {}

        for language in self.samples_manager.languages:
            samples[language] \
                = self._get_unbalanced_samples_for_language(language)
            if is_none_or_empty(samples[language]):
                raise CriticalException(
                    self.logger,
                    "No unbalanced samples found for %s" % language
                )

            # Normalize the polarities column: Replace the numerical sentiment
            # values by textual labels
            samples[language].df = normalize_polarities(samples[language].df)

        return samples

    # endregion --- Public Methods

    # region --- Protected Methods
    def _get_unbalanced_samples_for_language(self, language: str) \
            -> MyDataFrame:
        """
        Retrieves unbalanced samples for the specified language.

        Retrieves unbalanced samples for the specified language from the
        corresponing subset in the data source suite that is set by the
        SamplesManager.

        Throws away unneeded rows at the beginning of the dataset and any
        unneeded columns.

        Otherwise, does not restrict the number of samples because the
        unbalanced samples serve as the basis for creating balanced datasets
        of any size.

        Parameters
        ----------
        language : str
            The language for which the unbalanced samples are to be retrieved.

        Returns
        -------
        MyDataFrame
            A MyDataFrame object containing a DataFrame with unbalanced
            samples in the given language.

        Notes
        -----
        The returned DataFrame includes all available samples without applying
        balancing logic.

        """

        man = self.samples_manager
        suite = man.suite
        suite_name = man.suite_name
        data_offset = man.data_offset
        provenience = man.provenience

        # Iterate through the subsets of the data suite to find the subset for
        # the required language:
        for subset_name in suite.subset_names:
            if f"_{language}_" in subset_name:
                # Once a subset with the specified language is found,
                # it can be processed:

                # Get the subset dataframe, throwing away columns that
                # are not needed for the sentiment analysis
                df = self._get_sentiment_df(
                    suite.get_subset(
                        subset_name
                    )
                )

                # Throw away rows before the one where the prediction will
                # start
                df = df.iloc[data_offset:]

                # Return the unbalanced samples of the language
                return MyDataFrameFactory.create(
                    df,
                    name=f"{suite_name}_"
                         f"{language}_{provenience}"
                )

    @no_type_check
    def _get_sentiment_df(self, subset: S) \
            -> DataFrame:
        """
        Returns the sentiment-relevant columns from the given subset.

        Returns a DataFrame containing the sentiment-relevant columns from the
        given subset of the MAD-TSC suite.

        Parameters
        ----------
        subset : MadTscStrategy
            A language subset of the MAD-TSC suite.

        Returns
        -------
        DataFrame
            A pandas DataFrame containing the columns 'sentence_normalized',
            'mention', and 'polarity' from the given subset.

        """

        # Extract relevant columns
        cols = self.samples_manager.cols

        if not is_none_or_empty(subset.data):
            df = subset.data.do_with_column(
                "extract_columns", col_names=cols
            )

            return df

        return DataFrame()

    # endregion --- Protected Methods
