"""
data_source_subset_stats.py
---------------------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from typing import no_type_check, TypeVar, TYPE_CHECKING

from logger import Logger
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.data_structures.num_series import NumSeries
from src.data_structures.str_series import StrSeries
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty
from type_aliases import StatsType

T = TypeVar('T', bound='DataSourceStrategy')

if TYPE_CHECKING:
    from src.data_structures.my_data_frame import MyDataFrame


class DataSourceSubsetStats(ABC, LoggingMixin):
    """
    DataSourceSubsetStats class.

    This is an abstract base class for computing subset statistics. It provides
    a framework for calculating various statistics (such as length,
    word count, sentiment, etc.) on a subset of data. Concrete
    implementations should define subset-specific statistics.

    Attributes
    ----------
    subset: SubsetStrategy
        The data subset to be analyzed.

    subset_stats : MyDataFrame
        The collected statistics of the current subset.

    word_stats : MyDataFrame
        The word statistics. Computed property without setter.

    length_stats : MyDataFrame
        The length statistics. Computed property without setter.

    sentiment_stats : MyDataFrame
        The sentiment statistics. Computed property without setter.

    polarity_col_name : str
        The name of the polarity column.

    word_count_col_name : str
        The name of the word count column.

    length_col_name : str
        The name of the text length column.


    Methods
    -------
    compute_col_stats(col_name: str) -> None:
        Computes and stores the statistics for the specified column of the
        subset.

    compute_all_subset_stats() -> None:
        Computes and stores the statistics for all columns of the subset.

    """

    def __init__(self, subset: T) \
            -> None:
        """
        Constructor.

        Initializes the DataSourceSubsetStats class with a subset that is to
        be analyzed.

        Parameters
        ----------
        subset : T
            Subset that is to be analyzed.

        """

        self._length_col_name: str = ''
        self._word_count_col_name: str = ''
        self._polarity_col_name: str = ''
        self.subset = subset
        self._subset_stats: MyDataFrame | None = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        # Define the DataFrame to analyze if data is present
        if subset.has_data():
            self.subset_df = subset.data.df

        self._set_column_names()

    # region --- Properties

    @property
    def subset(self):
        """
        Returns the data subset.
        """

        return self._subset

    @subset.setter
    def subset(
            self,
            subset: T
    ) -> None:
        """
        Sets the data subset.
        """

        self._subset = subset

    @property
    def subset_stats(self) \
            -> MyDataFrame:
        """
        Collects all statistics of the current subset.

        The 'subset_stats' DataFrame corresponds to a table with multiple
        rows, one index column and one data column.

        The fields in the index column contain the data labels (e.g.,
        'min_length', ...). The data column is labeled with the subset's
        name, e.g., 'Olympia_dataset_1' and contains the different statistical
        values corresponding to the rows' labels.

        Examples
        --------

                        Subset_name
        n_elements          ...
        min_length          ...
        max_length          ...
        mean_length         ...
        median_length       ...

        """

        if not self._subset_stats:
            self._initialize_subset_stats(self.length_col_name)

        # Check if the subset_stats property has been initialized
        if is_none_or_empty(self._subset_stats):
            raise CriticalException(
                self.logger,
                "The 'subset_stats' DataFrame could not be initialized. "
            )

        return self._subset_stats  # type: ignore

    @subset_stats.setter
    def subset_stats(self, stats: MyDataFrame) \
            -> None:
        self._subset_stats = stats

    @property
    def word_stats(self) \
            -> MyDataFrame:
        """
        Returns the calculated the word statistics.

        Returns
        -------
        MyDataFrame
            A MyDataFrame containing the word statistics.

        Notes
        -----
        This computed property has no setter.

        Examples
        --------

                            Olympia_dataset_1
        min_words              ...
        max_words              ...
        mean_words             ...
        median_words           ...

        """

        return self._compute_col_stats(self.word_count_col_name, 'words')

    @property
    def length_stats(self) \
            -> MyDataFrame:
        """
        Returns the calculated length statistics.

        Returns
        -------
        MyDataFrame
            A MyDataFrame containing the length statistics.

        Notes
        -----
        This computed property has no setter.

        Examples
        --------

                            Olympia_dataset_1
        n_elements             ...
        min_length             ...
        max_length             ...
        mean_length            ...
        median_length          ...

        """

        return self._compute_col_stats(self.length_col_name, 'length')

    @property
    def sentiment_stats(self) \
            -> MyDataFrame:
        """
        Returns the calculated sentiment statistics.

        Returns
        -------
        MyDataFrame
            A MyDataFrame containing the sentiment statistics.

        Notes
        -----
        This computed property has no setter.

        Examples
        --------

                            Olympia_dataset_1
        min_polarity            ...
        max_polarity          ...
        mean_polarity         ...
        median_polarity       ...

        """

        return self._compute_sentiment_col_stats(
            self.polarity_col_name,
            'polarity'
        )

    @property
    def polarity_col_name(self) \
            -> str:
        """
        Gets the name of the polarity column.
        """

        return self._polarity_col_name

    @polarity_col_name.setter
    def polarity_col_name(self, col_name: str) \
            -> None:
        """
        Sets the name of the polarity column.
        """

        self._polarity_col_name = col_name

    @property
    def word_count_col_name(self) \
            -> str:
        """
        Gets the name of the word count column.
        """

        return self._word_count_col_name

    @word_count_col_name.setter
    def word_count_col_name(self, col_name: str) \
            -> None:
        """
        Sets the name of the word count column.
        """

        self._word_count_col_name = col_name

    @property
    def length_col_name(self) \
            -> str:
        """
        Gets the name of the text length column.
        """

        return self._length_col_name

    @length_col_name.setter
    def length_col_name(self, col_name: str) \
            -> None:
        """
        Sets the name of the text length column.
        """

        self._length_col_name = col_name

    # endregion --- Properties

    # region --- Public Methods

    def compute_col_stats(self, col_name: str = '') \
            -> None:
        """
        Computes and stores the statistics for the given column of the subset.

        Computes the statistics for the given column and stores them in the
        subset_stats property.

        Parameters
        ----------
        col_name : str
            The name of the column for which to compute the statistics.

        """

        if is_none_or_empty(col_name):
            self.compute_all_subset_stats()
        else:
            self._initialize_subset_stats(col_name)

    def compute_all_subset_stats(self) \
            -> None:
        """
        Computes and stores the statistics for all columns of the subset.

        Computes the statistics of the Olympia subset and stores them in the
        subset_stats property.

        Notes
        -----
        The 'subset_stats' property is initialized with the length stats.
        The other computed statistics are gradually added to the
        initialized subset_stats.

        """

        self._initialize_subset_stats(self.length_col_name)
        self._add_subset_specific_stats()

    # endregion --- Public Methods

    # region --- Protected Methods

    @no_type_check
    def _add_to_subset_stats(self, other_stats: MyDataFrame) \
            -> None:
        """
        Expands the subset_stats by the given stats.

        Merges the additional stats DataFrame with the subset_stats DataFrame.

        Notes
        -----
        Using the 'merge' method, the columns of the second DataFrame are
        added behind the columns of the first DataFrame.

        """

        if self.subset_stats.has_data() and other_stats.has_data():
            self.subset_stats.do_with_column(
                'merge', other=other_stats
            )

    def _compute_col_stats(
            self,
            col_name: str,
            label: str
    ) -> MyDataFrame:
        """
        Computes statistics for a given column.

        This method is called from the stats getters (e.g. word_stats,
        confidence_stats).

        Parameters
        ----------
        col_name : str
            The name of the column for which to compute the statistics.

        label : str
            The label to use for the statistics in the resulting MyDataFrame.

        Returns
        -------
        MyDataFrame
            A MyDataFrame containing the computed column statistics.

        """

        col_values = NumSeries(
            self.subset_df[col_name],
            label
        )

        col_stats = col_values.stats

        col_stats = self._remove_double_n_elements(col_stats)

        subset_col_stats = {self.subset.name: col_stats}

        return MyDataFrameFactory.create(
            subset_col_stats,
            name=f'{self.subset.name}_{label}_stats'
        )

    def _compute_categorical_col_stats(
            self,
            col_name: str,
            label: str
    ) -> MyDataFrame:
        """
        Computes statistics for a given column with categorical values.

        This method is called from the stats getters (e.g. word_stats,
        confidence_stats).

        Parameters
        ----------
        col_name : str
            The name of the column for which to compute the statistics.

        label : str
            The label to use for the statistics in the resulting MyDataFrame.

        Returns
        -------
        MyDataFrame
            A MyDataFrame containing the computed column statistics.

        """

        col_values = StrSeries(
            self.subset_df[col_name],
            label
        )

        col_stats = col_values.stats

        col_stats = self._remove_double_n_elements(col_stats)

        subset_col_stats = {self.subset.name: col_stats}

        return MyDataFrameFactory.create(
            subset_col_stats,
            name=f'{self.subset.name}_{label}_stats'
        )

    def _compute_sentiment_col_stats(self, col_name: str, label: str) \
            -> MyDataFrame:
        """
        Computes statistics for the sentiment column.

        This method is called from the sentiment_stats getter.

        Parameters
        ----------
        col_name : str
            The name of the column for which to compute the statistics.

        label : str
            The label to use for the statistics in the resulting MyDataFrame.

        Returns
        -------
        MyDataFrame
            A MyDataFrame containing the computed column statistics.

        """

        col_values = NumSeries(
            self.subset_df[col_name],
            label
        )

        col_stats = col_values.stats

        col_stats[f"unique_{label}"] = col_values.distinct_elements

        # Make sure the polarity constants exist in the MmsStrategy class
        if hasattr(self.subset, 'POSITIVE'):
            freqs = col_values.frequencies
            col_stats = self._add_sentiment_frequencies(freqs, col_stats)
            col_stats = self._add_sentiment_percentages(freqs, col_stats)

        col_stats = self._remove_double_n_elements(col_stats)

        subset_col_stats = {self.subset.name: col_stats}

        return MyDataFrameFactory.create(
            subset_col_stats,
            name=f'{self.subset.name}_{label}_stats'
        )

    def _get_stats_field(self, row_name: str, col_name: str) \
            -> int | float:
        """
        Returns the value of a given field in the subset_stats DataFrame.

        Parameters
        ----------
        row_name : str
            The name of the row in the subset_stats DataFrame.

        col_name : str
            The name of the column in the subset_stats DataFrame.

        Returns
        -------
        int | float
            The value of the field in the subset_stats DataFrame.

        Raises
        ------
        CriticalException
            If the subset_stats property has not been initialized.

        """

        # Check the private variable so that the subset_stats getter will not
        # initialize the property if it still is None:
        if self._subset_stats is None:
            raise CriticalException(
                self.logger,
                "The subset_stats property has not been initialized."
            )

        return self._subset_stats.do_with_field(
            'get_field_value',
            row_identifier=row_name,
            col_identifier=col_name
        )

    def _initialize_subset_stats(self, col_name: str = '') \
            -> None:
        """
        Initializes subset_stats with the stats for the given column.

        Uses the 'subset_stats' setter to initialize the 'subset_stats'
        property with a copy of the stats for the given column.

        Parameters
        ----------
        col_name : str
            The name of the column for which to compute the statistics.

        """

        if not col_name:
            raise CriticalException(
                self.logger,
                "No column name given! Cannot initialize subset stats."
            )

        match col_name:
            case self.length_col_name:
                self.subset_stats = self.length_stats.copy()

            case self.word_count_col_name:
                self.subset_stats = self.word_stats.copy()

            case _:
                self._initialize_subset_stats_with_subset_specific_column(
                    col_name
                )

    def _remove_double_n_elements(self, stats_dict: StatsType) \
            -> StatsType:
        """
        Removes double 'n_elements' from the stats dictionary.

        Removes the double 'n_elements' key-value pair from the stats
        dictionary.

        Checks whether the 'n_elements' value is the same in the current stats
        dictionary as in the length stats DataFrame. If it is, the 'n_elements'
        key-value pair is removed from the dictionary.

        This method is used to ensure the element count is not included
        more than once in the final statistics if it is the same for all
        statistical categories (length, words, sentences, ...).

        Parameters
        ----------
        stats_dict : StatsType
            The stats dict to remove the 'n_elements' key-value pair from.

        Returns
        -------
        StatsType
            The stats dict with the 'n_elements' key-value pair removed.

        """

        col_name = 'n_elements'
        # The row name equals the subset name:
        row_name = self.subset.name

        # Only remove 'n_elements' if it has already been added to the
        # subset stats once.
        if self._subset_stats:
            # Get the 'n_elements' value in the subset_stats DataFrame
            n_elements = self._get_stats_field(row_name, col_name)

            # Compare the 'n_elements' value in the current stats dictionary
            # with the corresponding value in the length stats DataFrame
            if stats_dict.get(col_name) == n_elements:
                # If the values match, remove the 'n_elements' key-value pair
                # from the dictionary:
                del stats_dict[col_name]

        return stats_dict

    def _set_column_names(self):
        """
        Sets the column names for the subset stats dataframe.
        """

        self.length_col_name = self.subset.LENGTH_COLUMN_NAME
        self.word_count_col_name = self.subset.WORD_COUNT_COLUMN_NAME

        self._set_subset_specific_column_names()

    # endregion --- Protected Methods

    # region --- Abstract Protected Methods

    @abstractmethod
    def _add_subset_specific_stats(self) \
            -> None:
        """
        Adds additional statistics to the subset_stats property.

        This method is called from the compute_all_subset_stats method.

        Notes
        -----
        As not only the statistics columns differ between subsets, but also
        their order is relevant, all the additional statistics need to be
        added in the concrete subset stats implementation.

        """

    @abstractmethod
    def _add_sentiment_frequencies(
            self,
            freqs: Counter,
            col_stats: StatsType
    ) -> StatsType:
        """
        Adds sentiment frequencies columns to the subset statistics.

        Parameters
        ----------
        freqs
            The frequencies of the values in the sentiment column.

        col_stats
            The subset statistics computed so far.

        Returns
        -------
        StatsType
            The subset statistics with sentiment frequencies added.

        Notes
        -----
        As the sentiment categories may differ between subsets,
        the sentiment frequencies need to be added in the concrete subset
        stats implementation.

        """

    @abstractmethod
    def _add_sentiment_percentages(
            self,
            freqs: Counter,
            col_stats: StatsType
    ) -> StatsType:
        """
        Adds percentages of the sentiment polarities to the subset statistics.

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

        Notes
        -----
        As the sentiment categories may differ between subsets,
        the polarity percentages need to be added in the concrete subset
        stats implementation.

        """

    @abstractmethod
    def _initialize_subset_stats_with_subset_specific_column(
            self,
            col_name: str
    ) -> None:
        """
        Initializes subset_stats with the stats for a subset-specific column.

        Uses the 'subset_stats' setter to initialize the 'subset_stats'
        property with a copy of the stats for the given column.

        Parameters
        ----------
        col_name : str
            The name of the column for which to compute the statistics.

        """

    @abstractmethod
    def _set_subset_specific_column_names(self) \
            -> None:
        """
        Sets the subset-specific column names for the subset stats dataframe.


        """

    # endregion --- Abstract Protected Methods
