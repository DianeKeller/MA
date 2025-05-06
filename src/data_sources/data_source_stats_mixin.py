"""
data_source_stats_mixin.py
--------------------------
Version 1.0, updated on 2025-05-01

"""

from typing import no_type_check

from pandas import DataFrame

from constants import INT, FLOAT
from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.decorators.ensure_implements_decorator import ensure_implements
from src.decorators.execution_time_decorator import execution_time
from src.loggable import Loggable
from src.logging_mixin import LoggingMixin
from src.utils.data_utils import is_none_or_empty


class DataSourceStatsMixin(LoggingMixin):
    """
    DataSourceStatsMixin class.

    Mixin class for handling statistics-related functionalities for the
    data source suites.

    This class provides properties and methods for computing, storing,
    and retrieving various statistics for data subsets within a data source
    suite.

    Attributes
    ----------
    COL_DTYPES : Dict[str, type]
        A dictionary mapping column names to their respective data types
        (e.g., INT, FLOAT). This is used to assign appropriate data types to
        the columns of the statistics DataFrame.

    stats : MyDataFrame
        The computed statistics.

    transposed_stats : MyDataFrame | None
        A MyDataFrame containing a transposed version of the stats MyDataFrame.

    Methods
    -------
    get_stats(category: str = '') -> MyDataFrame:
        Returns the statistics for the specified category.

    compute_all_stats()-> None:
        Computes the statistics for all loaded data subsets.

    """

    # Classes that use this mixin are expected to have the following
    # attributes:
    _subsets: dict

    # Dtypes for the different stats columns:
    COL_DTYPES = {
        'n_elements': INT,
        'min_length': INT,
        'max_length': INT,
        'mean_length': FLOAT,
        'median_length': FLOAT,
        'std_dev_length': FLOAT,
        'min_words': INT,
        'max_words': INT,
        'mean_words': FLOAT,
        'median_words': FLOAT,
        'std_dev_words': FLOAT,
        'min_sentences': INT,
        'max_sentences': INT,
        'mean_sentences': FLOAT,
        'median_sentences': FLOAT,
        'std_dev_sentences': FLOAT,
        'min_confidence': FLOAT,
        'max_confidence': FLOAT,
        'mean_confidence': FLOAT,
        'median_confidence': FLOAT,
        'min_polarity': INT,
        'max_polarity': INT,
        'mean_polarity': FLOAT,
        'median_polarity': FLOAT,
        'std_dev_polarity': FLOAT,
        'unique_polarity': object,
        'n_positive': INT,
        'n_negative': INT,
        'n_neutral': INT,
        'n_other': INT,
        '%_positive': FLOAT,
        '%_negative': FLOAT,
        '%_neutral': FLOAT,
        '%_other': FLOAT,
        'n_unique_elements': INT,
        'n_most_frequent_unique_elements': INT,
        'n_least_frequent_unique_elements': INT,
        'most_frequent_unique_elements': object,
        'least_frequent_unique_elements': object,
        'max_frequency': INT,
        'min_frequency': INT,
        'mean_frequency': FLOAT,
        'median_frequency': FLOAT,
        'std_dev_frequency': FLOAT,
        'max_percentage_of_occurrences': FLOAT,
        'min_percentage_of_occurrences': FLOAT,
        'mean_percentage_of_occurrences': FLOAT,
        'median_percentage_of_occurrences': FLOAT,
        'std_dev_percentage_of_occurrences': FLOAT,

    }

    # region --- Properties

    @property
    def stats(self) \
            -> MyDataFrame:
        """
        Retrieves the statistics MyDataFrame.

        If the statistics have not yet been computed and set, the
        compute_all_stats method is called to compute them.

        """

        if is_none_or_empty(getattr(self, '_stats', None)):
            self.compute_all_stats()

        return getattr(self, '_stats', MyDataFrameFactory.create())

    @stats.setter
    def stats(self, stats: MyDataFrame) \
            -> None:
        """
        Sets the stats property and resets the transposed_stats to None.

        Sets the stats property ensuring that the MyDataFrame columns
        are assigned the appropriate dtypes defined in the COL_DTYPES
        dictionary and resets the transposed_stats property to None so that
        it has to be recomputed when it is accessed to ensure the transposed
        data always matches the newest state of stats.

        """

        setattr(self, '_stats', self._assign_dtypes(stats))

        # Reset transposed stats property to None.
        setattr(self, '_transposed_stats', None)

    @property
    def transposed_stats(self) \
            -> MyDataFrame | None:
        """
        Retrieves the MyDataFrame containing a transposed statistics DataFrame.

        If the transposed DataFrame has not been set yet or has been reset
        to None, the _transpose_stats_copy method is called to create a
        transposed DataFrame from a copy of the normal statistics DataFrame.

        """

        if getattr(self, '_transposed_stats', None) is None:
            self._transpose_stats_copy()

        return getattr(self, '_transposed_stats', None)

    @transposed_stats.setter
    def transposed_stats(self, t_stats: MyDataFrame) \
            -> None:
        setattr(self, '_transposed_stats', t_stats)

    # endregion --- Properties

    # region --- Public Methods
    def get_stats(self, category: str = '') \
            -> MyDataFrame:
        """
        Returns the stats for the specified stats category.

        Returns
        -------
        MyDataFrame
            The stats DataFrame.

        """

        selected_col_names = [x for x in self.stats.col_names if category in x]
        selected_col_names.insert(0, 'n_elements')

        if category == 'polarity':
            additional_col_names = [
                'n_positive',
                'n_negative',
                'n_neutral',
                '%_positive',
                '%_negative',
                '%_neutral'
            ]
            selected_col_names.extend(additional_col_names)

        return MyDataFrame(DataFrame(self.stats.df[selected_col_names]))

    @execution_time
    def compute_all_stats(self) \
            -> None:
        """
        Computes the statistics for all loaded data subsets.

        Calls the _compute_stats method to compute all statistics for the
        loaded data subsets, telling the method which method to execute to
        get the relevant statistics.

        Notes
        -----
        This method is called automatically if the stats property is being
        accessed without having been set previously, but it can also be
        called from the outside, e.g. via the compute_statistics method of the
        data set's workflow.

        Examples
        --------
        >>> from src.data_sources.mad_tsc_workflow import MadTscWorkflow

        # Via the compute_statistics method of the workflow:
        >>> wf = MadTscWorkflow()
        >>> wf.load_subsets()
        >>> wf.compute_statistics()

        # Direct call after initialization of the Workflow
        >>> wf = MadTscWorkflow()
        >>> wf.suite.compute_all_stats()

        """

        self._compute_stats(
            compute_method=lambda subset_stats_instance:
            subset_stats_instance.compute_all_subset_stats()
        )

    # endregion --- Public Methods

    # region --- Protected Methods

    @no_type_check
    @ensure_implements(Loggable)
    def _compute_stats(self, compute_method: callable) \
            -> None:
        """
        Computes statistics for all loaded data subsets.

        Contains the common logic of the compute_all_stats and the
        _compute_col_stats methods.

        Parameters
        ----------
        compute_method : callable
            A method that takes a subset_stats_instance and performs the
            specific stats computation.

        Notes
        -----
        - This method does not return anything. Instead, it sets the stats
          property with the computed statistics.

        - The different subset stats consist of multiple rows, and a single
          column containing the data for the respective subset. When the
          different subset stats DataFrames are joined, the resulting DataFrame
          maintains this structure, the columns corresponding to the different
          subsets and the data in the columns being of different kinds. For
          this reason, the DataFrame is transposed at the end, so that the
          columns contain the same kind of data across all rows and can be
          assigned the appropriate data types.

        """

        # Create empty MyDataFrame instance
        stats = MyDataFrameFactory.create()

        for subset in self._subsets.values():
            subset_stats_instance = subset.create_subset_stats_instance()
            compute_method(subset_stats_instance)
            subset_stats = subset_stats_instance.subset_stats

            msg = f"Adding statistics for {subset.name} ..."
            self._log(msg, 'info')

            if is_none_or_empty(stats):
                stats.do_with_column(
                    "add_column",
                    data=subset_stats.data,
                    col_name=subset_stats.col_names[0]
                )
                stats.df = stats.df.T
            else:
                stats.do_with_column(
                    "add_column",
                    data=subset_stats.data.T
                )

            msg = f"Statistics added successfully for {subset.name}"
            self._log(msg, 'info')

        msg = "All statistics added successfully."
        self._log(msg, 'info')

        # Transpose the DataFrame in the MyDataFrame object
        stats.transpose()

        # Set the stats property
        self.stats = stats

    def _compute_col_stats(self, col_name: str = '') \
            -> None:
        """
        Computes statistics for the given column.

        Calls the _compute_stats method to compute statistics for the given
        column of all loaded data subsets, telling the method which
        method to execute to get the column statistics.

        """

        self._compute_stats(
            compute_method=lambda subset_stats_instance:
            subset_stats_instance.compute_col_stats(col_name)
        )

    def _transpose_stats_copy(self) \
            -> None:
        """
        Transposes a copy of the 'stats' property.
        """

        t_stats = self.stats.copy()
        t_stats.transpose()

        setattr(self, '_transposed_stats', t_stats)

    def _assign_dtypes(self, stats: MyDataFrame) \
            -> MyDataFrame:
        """
        Assigns the appropriate dtypes to the columns in the stats DataFrame.

        Parameters
        ----------
        stats : MyDataFrame
            The stats DataFrame to assign dtypes to.

        Returns
        -------
        MyDataFrame
            The stats DataFrame with the appropriate dtypes assigned.

        """

        stats.do_with_column(
            'assign_dtypes',
            col_type_map=self.COL_DTYPES
        )

        return stats

    # endregion --- Protected Methods
