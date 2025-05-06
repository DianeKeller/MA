"""
statistics_strategy.py
----------------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

import heapq
from abc import abstractmethod, ABC
from collections import OrderedDict
from statistics import mean, median
from typing import TYPE_CHECKING, List, Dict, Any, Set

import matplotlib.pyplot as plt

from constants import BIG_DATA_THRESHOLD, INT_NONE
from logger import Logger
from src.data_structures.my_ordered_dict import MyOrderedDict
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.stats.visualization.command_line_strategy import CommandLineStrategy
from src.stats.visualization.diagram import Diagram
from src.stats.visualization.plotter import Plotter
from src.utils.data_utils import is_none_or_empty
from src.utils.dict_utils import (
    filter_dict_by_value,
    filter_dict_keys_by_value,
    get_n_items_from_top,
    get_n_items_from_bottom, dict_to_string
)
from src.utils.late_imports import LateImports
from src.utils.list_utils import list_to_string
from src.utils.print_utils import examples
from type_aliases import DictKeyType

if TYPE_CHECKING:
    from src.data_structures.item_list import ItemList
    from src.data_structures.my_data_frame import MyDataFrame


class StatisticsStrategy(ABC, LoggingMixin):
    """
    This class serves as an interface within the framework of
    a strategy pattern. It enables a dynamic change of statistical
    strategies according to the statistical categories to be analyzed (
    e.g. length, frequency, element count) from a collection of items. The
    class declares common methods used by all supported statistics strategies
    for the computation, analysis and visualization of statistical data.

    Attributes
    ----------
    diagram : Diagram
        A diagram object used for visualizing statistical data.

    examples_highest_values : str
        A string representation of some of the items having the highest
        statistical value in the collection. Computed property without setter.

    examples_lowest_values : str
        A string representation of some of the items having the lowest
        statistical value in the collection. Computed property without setter.

    examples_near_means : str
        A string representation of some of the items having statistical values
        close to the mean of the collection. Computed property without setter.

    examples_near_median : str
        A string representation of some of the items having statistical values
        close to the median of the collection. Computed property without
        setter.

    highest_value : int
        The highest statistical value in the collection. Computed property
        without setter.

    highest_value_ids : List[Any]
        A list of item IDs having the highest statistical value. Computed
        property without setter.

    highest_value_items : List[Any]
        A list of items having the highest statistical value.  Computed
        property without setter.

    item_ids_and_values : MyOrderedDict
        A dictionary containing the item IDs and their corresponding
        statistical values.

    item_type : str
        The type of the elements in the item list as a string. Computed
        property without setter.

    items : ItemList
        A collection of items to be analyzed statistically.

    items_and_values : MyOrderedDict
        A dictionary containing the items and their corresponding statistical
        values.

    items_near_means : Dict[DictKeyType, int]
        A dictionary of items having statistical values close to the mean of
        the collection. Computed property without setter.

    items_near_median : Dict[DictKeyType, int]
        A dictionary of items having statistical values close to the median of
        the collection. Computed property without setter.

    lowest_value : int
        The lowest statistical value in the collection. Computed property
        without setter.

    lowest_value_ids : List[Any]
        A list of item IDs having the lowest statistical value. Computed
        property without setter.

    lowest_value_items : List[Any]
        A list of items having the lowest statistical value. Computed property
        without setter.

    mean_value : float
        The mean of the statistical values in the collection. Computed
        property without setter.

    median_value : float
        The median of the statistical values in the collection. Computed
        property without setter.

    name : str
        The name of the statistics, used to identify the data row in case the
        statistics for different data rows are assembled in a common data
        structure.

    n_items : int
        The number of items to be analyzed. Computed property without setter.

    second_highest_value : int
        The second-highest statistical value in the collection. Computed
        property without setter.

    second_highest_value_ids : List[Any]
        A list of item IDs having the second-highest statistical value.
        Computed property without setter.

    second_highest_value_items : List[Any]
        A list of items having the second-highest statistical value. Computed
        property without setter.

    second_lowest_value : int
        The second-lowest statistical value in the collection. Computed
        property without setter.

    second_lowest_value_ids : List[Any]
        A list of item IDs having the second-lowest statistical value.
        Computed property without setter.

    second_lowest_value_items : List[Any]
        A list of items having the second-lowest statistical value. Computed
        property without setter.

    stat_category : str
        The name of the statistical category to be analyzed. It is used to
        name the column holding the statistical values of the items in the
        dataframe used to store the statistical data, e.g. 'Frequency',
        'Length', 'Count'.

    unique_values : Set[int]
        A set containing the unique statistical values in the collection.
        Computed property without setter.

    values : List[int]
        A list of statistical values of all items in the collection. Computed
        property without setter.

    Methods
    -------
    analyze(items: Any) -> None:
        Analyzes the given items.

    get(item: Any, default: int = 0) -> int:
        Returns the statistical value for the given item.

    get_n_highest_items(n: int) -> Dict[DictKeyType, Any]:
        Gets n items having the highest statistical values in the collection.

    get_n_lowest_items(self, n: int) -> Dict[DictKeyType, Any]:
        Gets n items having the lowest statistical values in the collection.

    to_dataframe() -> MyDataFrame:
        Converts the items and their statistical values into a dataframe.

    visualize(ax: plt.Axes | None = None) -> None:
        Visualizes the data statistics.


    Abstract Methods
    ----------------
    compute_items_and_values() -> None:
        Computes the items and their corresponding statistical values.

    compute_item_ids_and_values() -> None:
        Computes the item IDs and their corresponding statistical values.

    to_string() -> str:
        Returns a string representation of the strategy.

    to_string_showing_ids() -> str:
        Returns a string representation of the strategy showing item IDs
        instead of item values.

    """

    def __init__(
            self,
            items: ItemList,
            stat_category: str,
            name: str = ''
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the StatisticsStrategy class with a
        collection of items and a statistical category.

        Parameters
        ----------
        items : ItemList
            A collection of items to be analyzed statistically. An ItemList
            object contains a list of elements, a name identifying the
            ItemList and some methods to manipulate the list elements and to
            get some basic characteristics of the list (number of elements,
            distinct elements).

        stat_category : str
            The name of the statistical category to be analyzed.

        name : str
            The name of the statistics. Defaults to an empty string. Can be
            used to identify the data row in case the statistics for
            different data rows are assembled in a common data structure.

        """

        # Override the default logger of the 'LoggingMixin' class.
        self._name = name
        self._unique_values: Set[int] = set()
        self.logger = Logger(self.__class__.__name__).get_logger()

        # Initializing MyOrderedDict objects with empty OrderedDicts.
        self._items_and_values: MyOrderedDict = MyOrderedDict(OrderedDict())
        self._item_ids_and_values: MyOrderedDict = MyOrderedDict(OrderedDict())

        self._items: ItemList = items
        self._stat_category: str = stat_category
        self._diagram: Diagram = Diagram(Plotter(CommandLineStrategy()))

    # region --- Properties

    @property
    def name(self) \
            -> str:
        """
        Returns the name of the statistics.

        Used to identify the data row in case the statistics for different
        data rows are assembled in a common data structure.

        """
        return self._name

    @name.setter
    def name(self, name: str) \
            -> None:
        """
        Sets the name of the statistics.
        """

        self._name = name

    @property
    def diagram(self) \
            -> Diagram:
        """
        Returns the diagram object.

        Returns
        -------
        Diagram
            The diagram object.

        """

        return self._diagram

    @diagram.setter
    def diagram(self, diagram: Diagram) -> None:
        """
        Sets the diagram object.

        Parameters
        ----------
        diagram : Diagram
            The new diagram object.

        """

        self._diagram = diagram

    @property
    def items(self) \
            -> ItemList:
        """
        Returns the collection of items to be analyzed.

        Returns
        -------
        ItemList
            The collection of items to be analyzed.

        """

        return self._items

    @items.setter
    def items(self, items: ItemList) \
            -> None:
        """
        Sets the collection of items to be analyzed.

        Parameters
        ----------
        items : ItemList
        The new collection of items to be analyzed.

"""

        self._items = items

    @property
    def n_items(self) \
            -> int:
        """
        Gets the number of items. 
        """
        return self.items.n_elements

    @property
    def stat_category(self) \
            -> str:
        """
        Gets the name of the statistical category to be analyzed.
        """

        return self._stat_category

    @stat_category.setter
    def stat_category(self, stat_category: str) -> None:
        """
        Sets the name of the statistical category to be analyzed.
        """

        self._stat_category = stat_category

    @property
    def items_and_values(self) \
            -> MyOrderedDict:
        """
        Gets the items and their corresponding statistical values.
        """

        if not self._items_and_values:
            self.compute_items_and_values()
        return self._items_and_values

    @items_and_values.setter
    def items_and_values(self, items_and_values: MyOrderedDict) \
            -> None:
        """
        Sets the item ids and their corresponding statistical values.
        """

        self._items_and_values = items_and_values

    @property
    def item_ids_and_values(self) \
            -> MyOrderedDict:
        """
        Gets the item ids and their corresponding statistical values.
        """

        if not self._item_ids_and_values:
            self.compute_item_ids_and_values()

        if not self._item_ids_and_values:
            raise CriticalException(
                self.logger,
                "item_ids_and_values could not be computed."
            )

        return self._item_ids_and_values

    @item_ids_and_values.setter
    def item_ids_and_values(self, item_ids_and_values: MyOrderedDict) \
            -> None:
        """
        Sets the item ids and their corresponding statistical values.
        """

        self._item_ids_and_values = item_ids_and_values

    @property
    def item_type(self) \
            -> str:
        """
        Gets the type of the elements in the item list as a string.
        """

        return self.items.element_type

    @property
    def values(self) \
            -> List[int]:
        """
        Gets the list of statistical values of all items in the collection.
        """

        return list(self.items_and_values.my_dict.values())

    @property
    def highest_value(self) \
            -> int:
        """
        Returns the highest statistical value in the collection.
        """

        if self._require_n_unique_items(1):
            return max(self.values)

        return INT_NONE

    @property
    def second_highest_value(self) \
            -> int:
        """
        Returns the second-highest statistical value in the collection.

        Notes
        -----
        This method distinguishes between small and big datasets to delegate
        the task of finding the second-highest value in the collection to the
        corresponding method that is optimized for this task and the given
        size of data.

        """

        if self._require_n_unique_items(2):

            if self.items.n_elements < BIG_DATA_THRESHOLD:
                return self._small_dataset_second_highest_value

            return self._big_dataset_second_highest_value

        return INT_NONE

    @property
    def _small_dataset_second_highest_value(self) \
            -> int:
        """
        Returns the second-highest statistical value in the collection.

        Notes
        -----
        This method is optimized for small datasets of up to 300,000 elements.
        For bigger datasets, use the '_big_dataset_second_highest_value'
        method.

        """

        if self._require_n_unique_items(2):
            values = self.values
            values.remove(self.highest_value)
            return max(values)

        return INT_NONE

    @property
    def _big_dataset_second_highest_value(self) \
            -> int:
        """
        Returns the second-highest statistical value in the collection.

        Notes
        -----
        This method is optimized for big datasets of over 300,000 elements.
        For smaller datasets, use the '_small_dataset_second_highest_value'
        method.

        """

        if self._require_n_unique_items(2):
            return heapq.nlargest(2, self.unique_values)[-1]
        return INT_NONE

    @property
    def unique_values(self) \
            -> Set[int]:
        """
        Returns the unique statistical values in the collection.

        """

        if is_none_or_empty(self._unique_values):
            self._unique_values = set(self.values)

        return self._unique_values

    @property
    def lowest_value(self) \
            -> int:
        """
        Returns the lowest statistical value in the collection.
        """
        if self._require_n_unique_items(1):
            return min(self.unique_values)
        return INT_NONE

    @property
    def second_lowest_value(self) \
            -> int:
        """
        Returns the second-lowest statistical value in the collection.

        Notes
        -----
        This method distinguishes between small and big datasets to delegate
        the task of finding the second-lowest value in the collection to the
        corresponding method that is optimized for this task and the given
        size of data.

        """

        if self._require_n_unique_items(2):
            if self.items.n_elements < BIG_DATA_THRESHOLD:
                return self._small_dataset_second_lowest_value
            return self._big_dataset_second_lowest_value

        return INT_NONE

    @property
    def _small_dataset_second_lowest_value(self) \
            -> int:
        """
        Returns the second-lowest statistical value in the collection.

        Notes
        -----
        This method is optimized for small datasets of up to 300,000 elements.
        For bigger datasets, use the '_big_dataset_second_lowest_value'
        method.

        """

        if self._require_n_unique_items(2):
            values = self.values
            values.remove(self.lowest_value)
            return min(values)

        return INT_NONE

    @property
    def _big_dataset_second_lowest_value(self) \
            -> int:
        """
        Returns the second-lowest statistical value in the collection.

        Notes
        -----
        This method is optimized for big datasets of over 300,000 elements.
        For smaller datasets, use the '_small_dataset_second_lowest_value'
        method.

        """

        if self._require_n_unique_items(2):
            return heapq.nsmallest(2, self.unique_values)[-1]
        return INT_NONE

    @property
    def mean_value(self) \
            -> float:
        """
        Returns the mean of the statistical values in the collection.
        """

        return mean(self.values)

    @property
    def median_value(self) \
            -> float:
        """
        Returns the median of the statistical values in the collection.
        """

        return median(self.values)

    @property
    def highest_value_items(self) \
            -> List[Any]:
        """
        Gets the items having the highest statistical value.
        """

        if self._require_n_unique_items(1):
            return filter_dict_keys_by_value(
                self.items_and_values.my_dict,
                self.highest_value
            )

        return []

    @property
    def second_highest_value_items(self) \
            -> List[Any]:
        """
        Gets the items having the second-highest statistical value.
        """

        if self._require_n_unique_items(2):
            return filter_dict_keys_by_value(
                self.items_and_values.my_dict,
                self.second_highest_value
            )

        return []

    @property
    def lowest_value_items(self) \
            -> List[Any]:
        """
        Gets the items having the lowest statistical value.
        """

        if self._require_n_unique_items(1):
            return filter_dict_keys_by_value(
                self.items_and_values.my_dict,
                self.lowest_value
            )

        return []

    @property
    def second_lowest_value_items(self) \
            -> List[Any]:
        """
        Gets the items having the second-lowest statistical value.
        """

        if self._require_n_unique_items(2):
            return filter_dict_keys_by_value(
                self.items_and_values.my_dict,
                self.second_lowest_value
            )

        return []

    @property
    def items_near_median(self) \
            -> Dict[DictKeyType, int]:
        """
        Gets items having statistical values close to the median of the
        collection.
        """

        return filter_dict_by_value(
            self.median_value,
            self.items_and_values.my_dict
        )

    @property
    def items_near_means(self) \
            -> Dict[DictKeyType, int]:
        """
        Gets items having statistical values close to the means of the
        collection.
        """

        return filter_dict_by_value(
            self.mean_value,
            self.items_and_values.my_dict
        )

    @property
    def highest_value_ids(self) \
            -> List[Any]:
        """
        Gets the ids of the items having the highest statistical value.
        """

        if self._require_n_unique_items(1):
            return filter_dict_keys_by_value(
                self.item_ids_and_values.my_dict,
                self.highest_value
            )

        return []

    @property
    def second_highest_value_ids(self) \
            -> List[Any]:
        """
        Gets the ids of the items having the second-highest statistical value.
        """

        if self._require_n_unique_items(2):
            return filter_dict_keys_by_value(
                self.item_ids_and_values.my_dict,
                self.second_highest_value
            )

        return []

    @property
    def lowest_value_ids(self) \
            -> List[Any]:
        """
        Gets the ids of the items having the lowest statistical value.
        """

        if self._require_n_unique_items(1):
            return filter_dict_keys_by_value(
                self.item_ids_and_values.my_dict,
                self.lowest_value
            )

        return []

    @property
    def second_lowest_value_ids(self) \
            -> List[Any]:
        """
        Gets the ids of the items having the second-lowest statistical value.
        """

        if self._require_n_unique_items(2):
            return filter_dict_keys_by_value(
                self.item_ids_and_values.my_dict,
                self.second_lowest_value
            )

        return []

    @property
    def ids_near_median(self) \
            -> Dict[DictKeyType, int]:
        """
        Gets the ids of the items having statistical values close to the
        median of the collection.
        """

        return filter_dict_by_value(
            self.median_value,
            self.item_ids_and_values.my_dict
        )

    @property
    def ids_near_means(self) \
            -> Dict[DictKeyType, int]:
        """
        Gets the ids of the items having statistical values close to the
        means of the collection.
        """

        return filter_dict_by_value(
            self.mean_value,
            self.item_ids_and_values.my_dict
        )

    @property
    def examples_near_means(self) \
            -> str:
        """
        Gets the string representation of some of the items having statistical
        values close to the means of the collection.

        Notes
        -----
        The number of items included in the string representation is
        restricted by the examples function to the number of MAX_ITEMS set in
        the 'NUM' category of the project settings.

        """

        return dict_to_string(dict(examples(self.items_near_means)))

    @property
    def examples_near_median(self) \
            -> str:
        """
        Gets the string representation of some of the items having statistical
        values close to the median of the collection.

        Notes
        -----
        The number of items included in the string representation is
        restricted by the examples function to the number of MAX_ITEMS set in
        the 'NUM' category of the project settings.

        """

        return dict_to_string(dict(examples(self.items_near_median)))

    @property
    def examples_lowest_values(self) \
            -> str:
        """
        Gets the string representation of some of the items having the highest
        statistical value in the collection.

        Notes
        -----
        The number of items included in the string representation is
        restricted by the examples function to the number of MAX_ITEMS set in
        the 'NUM' category of the project settings.

        """

        if self._require_n_unique_items(1):
            return list_to_string(examples(self.lowest_value_items))

        return ""

    @property
    def examples_highest_values(self) \
            -> str:
        """
        Gets the string representation of some of the items having the highest
        statistical value in the collection.

        Notes
        -----
        The number of items included in the string representation is
        restricted by the examples function to the number of MAX_ITEMS set in
        the 'NUM' category of the project settings.

        """

        if self._require_n_unique_items(1):
            return list_to_string(examples(self.highest_value_items))

        return ""

    # endregion --- Properties

    # region --- Methods

    # TODO: implement or remove
    def analyze(self, items: Any) \
            -> None:
        """
        Analyzes the given items.
        """
        pass

    def get(self, item: Any, default: int = 0) \
            -> int:
        """
        Returns the statistical value for the given item.

        Parameters
        ----------
        item : Any
            The item for which the statistical value is requested.

        default : int
            The default value to return if the item is not found in the
            collection. Defaults to 0.

        Returns
        -------
        int
            The statistical value for the given item. Equals to the specified
            default value if the item is not in the collection.

        Notes
        -----
        - The possible statistical categories being frequency, length or
          count, the statistical values are all supposed to be integers.

        - This method aims at providing a safe way to query statistical values
          by returning a default value when the requested item is not present,
          thus avoiding KeyErrors.

        - The caller can specify a different default value if 0 is not
          suitable for their context.

        """

        # The 'get' method of the dict type also provides the option to
        # specify a default value.
        return self.items_and_values.my_dict.get(item, default)

    def get_n_highest_items(self, n: int) \
            -> Dict[DictKeyType, Any]:
        """
        Gets n items having the highest statistical values in the collection.
        """

        return get_n_items_from_top(
            self.items_and_values.my_dict,
            n
        )

    def get_n_lowest_items(self, n: int) \
            -> Dict[DictKeyType, Any]:
        """
        Gets n items having the lowest statistical values in the collection.
        """

        return get_n_items_from_bottom(
            self.items_and_values.my_dict,
            n
        )

    def to_dataframe(self) \
            -> MyDataFrame:
        """
        Converts the items and their statistical values into a dataframe.

        Returns
        -------
        MyDataFrame
            The dataframe containing the items and statistical values,
            wrapped in a MyDataFrame object.

        """

        # Prevent circular imports
        my_dataframe_factory_cls = LateImports.get_my_dataframe_factory_class()

        return my_dataframe_factory_cls().create(
            self.items_and_values.my_dict,
            row_names=[self.items.name]
        )

    def visualize(self, ax: plt.Axes | None = None) \
            -> None:
        """
        Visualizes the data statistics.

        Provides a basic visualization of the statistical data by printing a
        DataFrame summary leveraging DataFrame properties and functions:

        - shape
            Displays the number of rows and columns in the DataFrame.
        - describe
            Provides descriptive statistics such as mean, median, and others
            for columns containing numerical data.
        - head
            Prints the first 5 rows of the DataFrame.
        - tail
            Prints the last 5 rows of the DataFrame.

        Parameters
        ----------
        ax : plt.Axes
            The axes on which to plot the data. Needed by some of the
            concrete statistics strategies. Defaults to None.

        Notes
        -----
        Where appropriate, strategy subclasses will extend this method by
        adding individual diagrams, e.g. a Zipf frequency diagram showing
        the frequency distribution of the data.


        """

        data = self.to_dataframe().df
        print(data.shape)
        print(data.describe())
        print(data.head(10))
        print(data.tail())

    # endregion --- Methods

    # region --- Abstract Methods

    @abstractmethod
    def compute_items_and_values(self) \
            -> None:
        """
        Abstract method to compute the items and their corresponding
        statistical values and set the _items_and_values attribute accordingly.

        The way the statistical values are computed depends on the
        statistical categories and must be defined by the corresponding
        strategy subclasses.

        """

    @abstractmethod
    def compute_item_ids_and_values(self) \
            -> None:
        """
        Abstract method to compute the item ids and their corresponding
        statistical values and set the _item_ids_and_values attribute
        accordingly.

        The way the statistical values are computed depends on the
        statistical categories and must be defined by the corresponding
        strategy subclasses.

        """

    @abstractmethod
    def to_string_showing_ids(self) \
            -> str:
        """
        Composes a string representation of the strategy showing item IDs
        instead of item values.

        Returns
        -------
        str
            The string representation of the strategy.

        """

    @abstractmethod
    def to_string(self) \
            -> str:
        """
        Composes a detailed string representation of the strategy.

        Returns
        -------
        str
            A string describing the strategy.

        """

    # endregion --- Abstract Methods

    # region --- Protected Methods

    def _require_n_unique_items(self, n: int) \
            -> bool:
        """
        Checks if the number of unique items in the collection is equal to n.
        """

        # Handle case where there aren't enough unique values
        if len(self.unique_values) < n:
            msg = f"There are less than {n} unique values in the collection."
            self._log(msg, "warning")

            # Handle gracefully
            return False

        return True

    # endregion --- Protected Methods
