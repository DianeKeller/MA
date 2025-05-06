"""
data_source_workflow.py
-----------------------
Version 1.0, updated on 2025-05-01

"""

from abc import ABC, abstractmethod
from typing import TypeVar, List

from src.logging_mixin import LoggingMixin
from src.utils.data_utils import is_none_or_empty
from src.utils.print_utils import print_in_box

T = TypeVar('T', bound='DataSourceSuite')


class DataSourceWorkflow(ABC, LoggingMixin):
    """
    DataSourceWorkflow class.

    Base class for workflows of data sources.

    Povides common methods and properties to manage and interact with data
    suites. Concrete subclasses should implement and extend the
    functionalities of this base class according to the needs of the
    specific data source.

    Attributes
    ----------
    data_suite : T
        An instance of the data suite class.

    Methods
    -------
    load_subsets(ubsets: List[str] | None = None) -> None:
        Loads the subsets of the data suite.

    get_statistics()-> None:
        Gets the complete statistics for the data suite.

    Notes
    -----
    Together with its concrete implementations, this base class constitutes
    the entry point for any operations on the data suite the concrete
    workflow is designed for. It provides easy access to the functionalities
    of the suite and its associated classes.

    Examples
    --------
    To access the suite, first initialize the workflow:
    >>> from src.data_sources.mad_tsc_workflow import MadTscWorkflow

    >>> wf = MadTscWorkflow()
    >>> wf.load_subsets()
    >>> suite = wf.suite

    Then do any operations the workflow or the suite provide.

    """

    def __init__(self, data_suite: T) \
            -> None:
        """
        Constructor.

        Initializes the DataSourceWorkflow class with a data suite.

        Parameters
        ----------
        data_suite : T
           Data suite to be managed by the workflow..

        """

        self.data_suite = data_suite

    # region --- Properties

    @property
    def suite(self) -> T:
        """
        Gets the data suite.

        Returns
        -------
        T
            An instance of the data suite class.

        """

        return self.data_suite

    # endregion --- Properties

    # region --- Public Methods
    @abstractmethod
    def execute(self) \
            -> None:
        """
        Defines which operations are included and executed when the workflow
        is executed.

        This method must be implemented by concrete subclasses to allow for
        data source-specific workflows.

        """

    def load_subsets(self, subsets: List[str] | None = None) -> None:
        """
        Loads the specified subsets of the dataset.

        If no subsets are specified, all subsets contained in the suite are
        loaded.

        Parameters
        ----------
        subsets : List[str] | None
            A list of subset names to be loaded. Defaults to all subsets in
            the suite.

        """

        data_suite = self.suite

        # Print the available strategies
        title = "Available strategies:"
        body = data_suite.strategy_names
        print_in_box(title, body)

        # If no subsets are provided, get the list of all subsets in the suite.
        if is_none_or_empty(subsets):
            subsets = self.suite.strategy_names

        # Load the different subsets.
        for subset in subsets:
            data_suite.load_subset(subset)

        # Show the loaded subsets
        title = "Loaded subsets:"
        body = data_suite.subset_names
        print_in_box(title, body)

    def get_statistics(self) -> None:
        """
        Gets the complete statistics for the dataset.
        """

        # self.suite.compute_all_stats()
        print(self.suite.stats)

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
