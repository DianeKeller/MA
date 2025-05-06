"""
mad_tsc_subset_stats.py
-----------------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from src.data_sources.data_source_subset_stats import DataSourceSubsetStats
from type_aliases import StatsType

if TYPE_CHECKING:
    from src.data_sources.mad_tsc_strategy import MadTscStrategy
    from src.data_structures.my_data_frame import MyDataFrame


class MadTscSubsetStats(DataSourceSubsetStats):
    """
    MadTscSubsetStats class

    This class provides the statistics of a subset of the MAD_TSC data suite.
    It extends the 'DataSourceSubsetStats' class and includes additional
    methods to handle MAD-TSC-specific characteristics, such as sentiment
    analysis and mention statistics.

    Attributes
    ----------
    subset: MadTscStrategy
        The MAD-TSC subset that is to be analyzed.

    sentence_count_col_name : str
        The name of the column in the subset that contains sentence counts.

    mention_col_name : str
        The name of the column in the subset that contains mention data.

    sentence_stats : MyDataFrame
        The sentence statistics as a MyDataFrame. Computed property without
        setter.

    mention_stats : MyDataFrame
        The mention statistics as a MyDataFrame. Computed property without
        setter.

    """

    def __init__(
            self,
            subset: MadTscStrategy
    ) -> None:
        """
        Constructor.

        Initializes the MadTscSubsetStats class with a MAD-TSC subset that is
        to be analyzed.

        Parameters
        ----------
        subset : MadTscStrategy
            The MAD-TSC subset that is to be analyzed.

        """

        super().__init__(subset)

        self.sentence_count_col_name = self.subset.SENTENCE_COUNT_COLUMN_NAME
        self.mention_col_name = self.subset.MENTION_COLUMN_NAME

    # region --- Properties
    @property
    def sentence_stats(self) \
            -> MyDataFrame:
        """
        Retrieves the sentence statistics.

        Returns
        -------
        MyDataFrame
            A MyDataFrame containing the sentence statistics.

        Notes
        -----
        - This computed property has no setter.

        - Not all data sources provide text containing sentences. Therefore,
          this method has to be implemented in the concrete
          DataSourceSubsetStats classes if needed.

        Examples
        --------

                            Subset name
        min_sentences          ...
        max_sentences          ...
        mean_sentences         ...
        median_sentences       ...

        """

        return self._compute_col_stats(
            self.sentence_count_col_name,
            'sentences'
        )

    @property
    def mention_stats(self) \
            -> MyDataFrame:
        """
        Retrieves the mention statistics.

        Returns
        -------
        MyDataFrame
            A MyDataFrame containing the mention statistics.

        Notes
        -----
        - This computed property has no setter.

        - Not all data sources provide text containing mentions. Therefore,
          this method has to be implemented in the concrete
          DataSourceSubsetStats classes if needed.

    """

        return self._compute_categorical_col_stats(
            self.mention_col_name,
            'mentions'
        )

    # endregion --- Properties

    # region --- Protected Methods

    def _set_subset_specific_column_names(self) \
            -> None:
        """
        Sets subset-specific column names for the subset stats dataframe.

        Notes
        -----
        As the statistics columns may differ between data sources depending
        on the data provided by the sources, the columns have to be set in
        each concrete DataSourceSubsetStats class.

        """

        self.polarity_col_name = (
            self.subset.NUMERICAL_SENTIMENT_POLARITY_COLUMN_NAME
        )

    def _add_subset_specific_stats(self) -> None:
        """
        Adds the subset-specific statistics to the subset stats DataFrame.

        Gathers various statistics specific to the MAD-TSC subset and adds
        them to the subset stats DataFrame.

        """

        specific_stats = [
            self.sentence_stats,
            self.word_stats,
            self.sentiment_stats,
            self.mention_stats
        ]
        # Using ThreadPoolExecutor to parallelize method calls
        with ThreadPoolExecutor() as executor:
            # Map each stat to the _add_to_subset_stats function
            executor.map(self._add_to_subset_stats, specific_stats)

    def _add_sentiment_frequencies(
            self,
            freqs: Counter,
            col_stats: StatsType
    ) -> StatsType:
        """
        Adds sentiment frequencies to the subset statistics.

        This method is called from the _compute_sentiment_col_stats method to
        add counts of positive, negative, neutral, and possibly none
        sentiments to the statistics.

        Parameters
        ----------
        freqs : Counter
            A dictionary containing the frequencies of the sentiment values.

        col_stats : StatsType
            The subset statistics computed so far.

        Returns
        -------
        StatsType
            The subset statistics dictionary with sentiment frequencies added.

        """

        col_stats["n_positive"] = freqs.get(self.subset.POSITIVE, 0)
        col_stats["n_negative"] = freqs.get(self.subset.NEGATIVE, 0)
        col_stats["n_neutral"] = freqs.get(self.subset.NEUTRAL, 0)

        if self.subset.data.df[self.polarity_col_name].isna().any():
            col_stats["n_none"] = self.subset.data.df[
                self.polarity_col_name].isna().sum()

        return col_stats

    def _add_sentiment_percentages(
            self,
            freqs: Counter,
            col_stats: StatsType
    ) -> StatsType:
        """
        Adds percentages of the sentiment polarities to the subset statistics.

        This method is called from the _compute_sentiment_col_stats method to
        calculate and add the percentages of positive, negative, neutral,
        and possibly none sentiments to the statistics.

        Parameters
        ----------
        freqs : Counter
            A dictionary containing the frequencies of the sentiment values.

        col_stats : StatsType
            The subset statistics computed so far.

        Returns
        -------
        StatsType
            The subset statistics dictionary with polarity percentages added.

        """

        n_sum = sum(freqs.values())

        n_positive = freqs.get(self.subset.POSITIVE, 0)
        n_negative = freqs.get(self.subset.NEGATIVE, 0)
        n_neutral = freqs.get(self.subset.NEUTRAL, 0)

        hasna = self.subset.data.df[self.polarity_col_name].isna().any()
        if hasna:
            n_none = self.subset.data.df[
                self.polarity_col_name].isna().sum()
        else:
            n_none = 0

        percent_positive = 100 * n_positive / n_sum
        percent_negative = 100 * n_negative / n_sum
        percent_neutral = 100 * n_neutral / n_sum

        if hasna:
            percent_none = 100 * n_none / n_sum
            col_stats["%_none"] = percent_none

        col_stats["%_positive"] = percent_positive
        col_stats["%_negative"] = percent_negative
        col_stats["%_neutral"] = percent_neutral

        return col_stats

    def _initialize_subset_stats_with_subset_specific_column(
            self,
            col_name: str = ''
    ) -> None:
        """
        Initializes subset_stats with the stats for the given column.

        This method initializes the 'subset_stats' property by copying the
        statistics for the column specified by the provided column name.

        Parameters
        ----------
        col_name : str
            The name of the column for which to compute the statistics.

        """

        match col_name:
            case self.polarity_col_name:
                self.subset_stats = self.sentiment_stats.copy()

            case _:
                self.subset_stats = self.length_stats.copy()

    # endregion --- Protected Methods
