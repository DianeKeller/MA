"""
data_source_suite.py
--------------------
Version 1.0, updated on 2025-05-01

"""

import copy
from abc import ABC, abstractmethod
from typing import Dict, List, no_type_check, TypeVar, Generic

from logger import Logger
from src.data_sources.data_source_stats_mixin import DataSourceStatsMixin
from src.data_sources.data_source_strategy import DataSourceStrategy
from src.decorators.data_check_decorators import (
    output_not_none_or_empty,
    output_not_none, info_output_empty
)
from src.decorators.execution_time_decorator import execution_time
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty

T = TypeVar('T', bound=DataSourceStrategy)


class DataSourceSuite(
    ABC,
    Generic[T],
    DataSourceStatsMixin,
    LoggingMixin
):
    """
    DataSourceSuite class.

    This abstract base class defines the methods for the import of a data
    source collection and the extraction or composition of the different
    data sets forming the suite.

    Attributes
    ----------
    suite_name : str
        The name of the data suite. (Read-only)

    subset_names : List[str]
        A list of the names of the loaded subsets. (Read-only)

    strategy_names : List[str]
        A list of the strategy names available in the suite. (Read-only)

    combined_subsets : T
        The combined subset of all data in the suite. This is computed
        by combining individual subsets when accessed.

    STRATEGY_STR : str
        A format string used for logging strategy-related messages.

    SUBSET_STR : str
        A format string used for logging subset-related messages.

    LANG_DE : str
        Constant for the German language code.

    LANG_EN : str
        Constant for the English language code.

    LANG_ES : str
        Constant for the Spanish language code.

    LANG_FR : str
        Constant for the French language code.

    LANG_IT : str
        Constant for the Italian language code.

    LANG_NL : str
        Constant for the Dutch language code.

    LANG_PT : str
        Constant for the Portuguese language code.

    LANG_RO : str
        Constant for the Romanian language code.

    Methods
    -------
    get_strategy(strategy_name: str) -> T | None:
        Retrieves the specified strategy from the suite.

    use_strategy(strategy_name: str) -> T:
        Ensures the specified strategy exists and returns it.

    get_subset(subset_name: str) -> T | None:
        Retrieves the specified subset from the suite.

    use_subset(subset_name: str) -> T:
        Ensures the specified subset exists and returns it.

    combine_subsets(subset_names: List[str] | None = None) -> T:
        Combines specified subsets into a single subset.

    to_string() -> str:
        Returns a formatted string representation of the data in the suite.

    Abstract Methods
    ----------------
    load_subset(strategy_name: str) -> None:
        Loads the specified data subset into the suite.

    _initialize_strategies() -> None:
        Initializes all strategies, considering their dependencies.

    _compose_from_original_files(subset: T, strategy_name: str) -> None:
        Composes the specified subset from original files.

    """

    # Define format strings as class constants
    STRATEGY_STR: str = "{self.SUITE_NAME} strategy '{strategy_name}'"
    SUBSET_STR: str = "{self.SUITE_NAME} subset '{subset_name}'"

    def __init__(self) -> None:
        """
        Constructor.

        Initializes a new instance of the DataSourceSuite class and provides
        private variables to store the different data subsets of the data suite
        in memory and make them accessible via properties.

        """
        self._languages: List[str] = self._languages if self._languages else []

        self._combined_subsets: T | None = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        # Dictionary for the different strategies to create and store
        self._strategies: Dict[
            str, T
        ] = {}

        # Dictionary for the loaded data subsets
        self._subsets: Dict[
            str, T
        ] = {}

        # Create and store the strategies in the strategies dictionary
        self._initialize_strategies()

    # region --- Properties

    @property
    def suite_name(self) \
            -> str:
        """
        Returns the name of the data suite.

        Returns
        -------
        str
            The name of the data suite.

        """

        return self.__class__.__name__

    @property
    def subset_names(self) \
            -> List[str]:
        """
        Returns the names of the loaded subsets.

        Returns
        -------
        List[str]
            The list of the subset names.

        Notes
        -----
        Ensure you have executed the load_subsets method of the
        DataSourceWorkflow class before attempting to access this subset_names
        property.

        """

        if len(self._subsets) == 0:
            msg = (
                "Make sure you have executed the load_subsets method of the "
                "DataSourceWorkflow class before attempting to access this "
                "subset_names property."
            )
            self._log(msg, "info")

        return list(self._subsets.keys())

    @property
    def strategy_names(self) \
            -> List[str]:
        """
        Returns a list of the strategy names.

        Returns the list of the different strategy names in the suite.

        Returns
        -------
        List[str]
            The list of the strategy names.

        """

        return list(self._strategies.keys())

    @property
    def languages(self) \
            -> List[str]:
        """
        Returns the languages present in the suite.

        """
        if is_none_or_empty(self._languages):
            raise CriticalException(
                self.logger,
                "No languages found in suite. Cannot proceed."
            )

        return self._languages

    @languages.setter
    def languages(self, languages: List[str]) \
            -> None:
        """
        Sets the languages of the suite.
        """

        self._languages = languages

    @property
    def combined_subsets(self) \
            -> T:
        """
        Returns the combined subsets of the data suite.
        """

        if is_none_or_empty(self._combined_subsets):
            self._combined_subsets = self.combine_subsets()

        return self._combined_subsets  # type: ignore

    @combined_subsets.setter
    def combined_subsets(self, combined_subset: T) \
            -> None:
        """
        Sets the combined subsets of the data suite.
        """

        self._combined_subsets = combined_subset

    # endregion --- Properties

    # region --- Public Methods

    def get_strategy(self, strategy_name: str) \
            -> T | None:
        """
        Gets the specified strategy from the _strategies dictionary.

        Parameters
        ----------
        strategy_name : str
            The name of the strategy to return.

        Returns
        -------
        T | None
            The specified strategy.

        Notes
        ------
        - Use this method if the returned strategy may be None.

        - Use the use_strategy() method instead if you want to ensure that
          the strategy actually exists.

        """

        return self._strategies.get(strategy_name)

    @no_type_check
    @output_not_none(STRATEGY_STR)
    def use_strategy(self, strategy_name) \
            -> T:
        """
        Gets the specified strategy from the _strategies dictionary.

        Ensures the strategy exists before returning it.

        Parameters
        ----------
        strategy_name : str
            The name of the strategy to return.

        Returns
        -------
        T
            The specified strategy.

        Notes
        ------
        - Use this method if you want to ensure that the strategy actually
          exists and want the method to raise an error if it does not.

        - Use the get_strategy() method instead if the returned strategy may
          be None and you want to handle this case individually.

        """

        return self.get_strategy(strategy_name)

    def get_subset(self, subset_name: str) \
            -> T | None:
        """
        Gets the specified subset from the _subsets dictionary.

        Parameters
        ----------
        subset_name : str
            The name of the subset to return.

        Returns
        -------
        T | None
            The specified subset.

        Notes
        ------
        - Use this method if the returned subset may be None.

        - Use the use_subset() method instead if you want to ensure that
          the subset actually exists.

        """

        return self._subsets.get(subset_name)

    @no_type_check
    @output_not_none_or_empty(SUBSET_STR)
    def use_subset(self, subset_name: str) \
            -> T:
        """
        Gets the specified subset from the _subsets dictionary.

        Makes sure the subset exists before returning it.

        Parameters
        ----------
        subset_name : str
            The name of the subset to return.

        Returns
        -------
        T
            The specified subset.

        Raises
        ------
        CriticalException
            If the subset does not exist.

        Notes
        ------
        - Use this method if you want to ensure that the subset actually
          exists and you want the method to raise an error if it does not.

        - Use the get_subset() method instead if the returned subset may
          be None and you want to handle this case individually.

        """

        # Make sure the subset is in the dictionary
        if subset_name not in self._subsets:
            raise CriticalException(
                self.logger,
                "%s subset %s not found!" % (self.suite_name, subset_name)
            )

        return self._subsets.get(subset_name)

    @no_type_check
    def combine_subsets(self, subset_names: List[str] | None = None) \
            -> T:
        """
        Combines the specified subsets into a single subset.

        Parameters
        ----------
        subset_names : List[str] | None
            The subsets to combine. Defaults to None. If no subset names are
            provided, all subsets in the suite are combined.

        Returns
        -------
        T
            The combined subset.

        """

        save_combined_subsets: bool = False

        if is_none_or_empty(subset_names):
            subset_names = self.subset_names
            save_combined_subsets = True

        combined_subsets = None

        for name in subset_names:  # type: ignore
            subset = copy.deepcopy(self.use_subset(name))
            if is_none_or_empty(combined_subsets):
                combined_subsets = subset
                new_col_names = []
                for col_name in subset.my_df.col_names:
                    new_col_names.append(f'{col_name}_{subset.language}')
                combined_subsets.my_df.df.columns = new_col_names
            else:
                combined_subsets.join(subset)  # type: ignore
                combined_subsets.name = (f'{combined_subsets.name}_'
                                         f'{subset.language}')

        # Make sure the combined_subsets property is only set if all subsets
        # are included in the combination.
        if save_combined_subsets:
            self.combined_subsets = combined_subsets

        return combined_subsets

    # endregion --- Public Methods

    # region --- Abstract Public Methods
    @execution_time
    def load_subset(
            self,
            strategy_name: str,
    ) -> None:
        """
        Stores the specified data subset in the _subsets dictionary.

        The data subset is loaded from disk, fetched from the original
        online or local source, or extracted from its superset and stored in
        the _subsets dictionary.

        Parameters
        ----------
        strategy_name : str
            The name of the data subset.

        Raises
        ------
        CriticalException
            If the specified data subset could not be loaded from disk,
            fetched from the online source or extracted from its superset.

        Notes
        -----
        - The loaded, fetched or extracted subset data is not returned by
          this method but stored in the data structure of the respective
          strategy collected in the _subsets dictionary of this class

        - This method provides a standard way to load subsets. It may be
          overridden or extended by subclasses to satisfy specific needs.

        """

        self._enforce_load(strategy_name)

        msg = f"Loaded {strategy_name} data."
        self._log(msg, 'info')

        print(self._subsets[strategy_name])

    @abstractmethod
    def to_string(self) -> str:
        """
        Provides a formatted string representation of the data in the current
        suite.

        Expands the base description by suite specific details like the name
        and source of the data collection, the author(s) of the collection
        and the citation of the associated scientific paper. If the data
        is not yet initialized, the description includes statistical insights
        such as the numbers and names of the domains, languages and original
        datasets contained in the data.

        Returns
        -------
        str
            A string representation of the data in the current MMS suite.

        """
        pass

    # endregion --- Abstract Public Methods

    # region --- Protected Methods

    @output_not_none(STRATEGY_STR)
    @info_output_empty(
        STRATEGY_STR + " is not yet on disk. Creating subset...",
        on_empty=lambda self, result, strategy_name:
        self._compose_from_original_files(result, strategy_name)
    )
    def _enforce_load(self, strategy_name: str) \
            -> T:
        """
        Enforces loading the subset defined by the given strategy name.

        If the subset data cannot be loaded from disk, an info message is
        logged and the data is composed from the original files.

        Parameters
        ----------
        strategy_name : str
            The name of the Olympia strategy used to manage the subset.

        Returns
        -------
        Subset
            The subset.

        Notes
        -----
        - The loaded or fetched subset data is only returned by this
          method to enable the decorator to check its content. The caller
          will not use the return value but the subset in the _subsets
          collection of this class where it is identified by its strategy
          name.

        """

        subset = self.use_strategy(strategy_name)

        # Try to load the subset from disk. If this fails, the method
        # specified in the 'info_output_empty' decorator will be called.
        subset.load()

        self._subsets[strategy_name] = subset

        # Return the subset so that the decorator can check its content
        return subset

    # endregion --- Protected Methods

    # region --- Abstract Protected Methods

    @abstractmethod
    def _initialize_strategies(self) \
            -> None:
        """
        Initialize all strategies, respecting their dependencies.

        Each strategy is configured specifying
        - its strategy name,
        - its data type,
        - its file name,
        - its language, if there is only one

        """

    @abstractmethod
    def _compose_from_original_files(
            self,
            subset: T,
            strategy_name: str
    ) -> None:
        """
        Composes the specified subset from the original files.

        Parameters
        ----------
        subset : T
            The subset to compose.

        strategy_name : str
            The name of the strategy used to identify and configure the subset.

        Notes
        -----
        The created subset is not returned from this method but:

        - Stored in the _subsets dictionary of this class.
        - Saved to disk according to the serialization strategy used by the
          strategy of the subset (e.g., PKL format for DataFrame objects).

        """

    # endregion --- Abstract Methods
