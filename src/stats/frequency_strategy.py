"""
frequency_strategy.py
---------------------
Version 1.0, updated on 2025-01-27

"""

from __future__ import annotations

from collections import Counter, OrderedDict
from typing import TYPE_CHECKING, Dict, Any, List

import matplotlib.pyplot as plt

from constants import MAX_ITEMS
from src.data_structures.my_ordered_dict import MyOrderedDict
from src.stats.statistics_strategy import StatisticsStrategy
from src.utils.dict_sort_utils import sort_dict_by_desc_values_and_asc_keys
from src.utils.print_utils import WHITE_LINE, SEPARATOR, SUBSEPARATOR, \
    restrict_length

if TYPE_CHECKING:
    from src.data_structures.item_list import ItemList


class FrequencyStrategy(StatisticsStrategy):
    """
    This class is a concrete implementation of the StatisticsStrategy
    interface for statistical analyses. This strategy is used for the analysis
    of frequencies of given items collected in an ItemList object.

    """

    CATEGORY = 'Frequency'

    def __init__(
            self,
            items: ItemList,
            name: str = ''
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the FrequencyStrategy class with items
        organized in an ItemList object.
        .
        """

        if not name:
            name = items.name

        super().__init__(items, self.CATEGORY, name)

    def compute_items_and_values(self) \
            -> None:
        """
        Computes the items and their corresponding frequency values and sets
        the _items_and_values attribute accordingly.

        This method implements the abstract method in the StatisticsStrategy
        parent class.

        Notes
        -----
        - For compatibility with the other statistics strategies, the Counter
          object returned from the '__count_frequencies' method is converted to
          a MyOrderedDict object, preserving the order from the highest to
          the lowest frequency by using the 'most_common' method of the
          Counter object.

        - The computed result is not returned, but used to set the
          items_and_values property of this class.

        """

        self._items_and_values = MyOrderedDict(
            OrderedDict(self.__count_frequencies().most_common())
        )

    def compute_item_ids_and_values(self) \
            -> None:
        """
        Computes the item ids and their corresponding frequency values and
        sets the _item_ids_and_values attribute accordingly.

        This method  implements the abstract method in the StatisticsStrategy
        parent class.

        Notes
        -----
        The computed result is not returned, but used to set the
        item_ids_and_values property of this class.

        """

        self._item_ids_and_values = self.__count_frequencies_by_first_id()

    def __count_frequencies(self) \
            -> Counter[str]:
        """
        Counts frequencies of items.

        This private method contains the computing logic for the
        compute_items_and_values method implementation in this subclass.

        Returns
        -------
        Counter[str]
            The frequencies of the items in the item list, where the
            unique items are the keys and the frequencies are the values.

        """

        return Counter(self.items.to_strings())

    def __count_frequencies_by_first_id(self) \
            -> MyOrderedDict:
        """
        Counts frequencies of items by their first id.

        Counts frequencies of items remembering the index ('id') of the first
        occurrence of each item.

        Gets ordered dictionary of the ids of the first occurrence of each
        distinct item and the items' frequencies, sorted first by frequencies
        and then by id.

        Notes
        -----
        The dictionary does not contain the item itself, but only the id of
        the first occurrence of the item in the original item list.

        """

        # Creating an empty list to store and lookup unique items.
        freq: List[Any] = []
        # Creating an empty dictionary to store the ids of the first
        # occurrences of the items and the item frequencies.
        freq_by_id: Dict[int, int] = {}

        for item in self.items.to_strings():
            if item in freq:
                freq_by_id[self.items.to_strings().index(item)] += 1
            else:
                freq.append(item)
                freq_by_id[self.items.to_strings().index(item)] = 1

        return sort_dict_by_desc_values_and_asc_keys(freq_by_id)

    def to_string_showing_ids(self) \
            -> str:
        """
        This method returns a string representation of the object similar to
        the 'to_string' method, but showing item IDs instead of item values.

        Returns
        -------
        str
            The string representation of the object.

        """

        item = f'{self.item_type}'
        items = f'{item}s'

        string = WHITE_LINE + \
                 SEPARATOR + \
                 WHITE_LINE + \
                 f'{type(self).__name__} of {self.items.name} \n' + \
                 '(All IDs)\n' + \
                 SUBSEPARATOR + \
                 WHITE_LINE + \
                 (
                     f'Number of {items}:            '
                     f'{self.items.n_elements} \n'
                 ) + \
                 SUBSEPARATOR + \
                 WHITE_LINE + \
                 (
                     f'Average {item.lower()} frequency:           '
                     f'{self.mean_value} \n'
                 ) + \
                 f'{items} with frequency close to average: \n' + \
                 f'{self.ids_near_means} \n' + \
                 (
                     f'Median {item.lower()} frequency:         '
                     f'{self.median_value} \n'
                 ) + \
                 f'{items} with close to median frequency: \n' + \
                 f'{self.ids_near_median} \n' + \
                 (
                     f'Lowest {item.lower()} frequency:       '
                     f'{self.lowest_value} \n'
                 ) + \
                 f'Least frequent {items.lower()}: \n' + \
                 f'{self.lowest_value_ids} \n' + \
                 (
                     f'Highest {item} frequency:        '
                     f'{self.highest_value}  \n'
                 ) + \
                 f'Most frequent {items.lower()}: \n' + \
                 f'{self.highest_value_ids} \n' + \
                 SEPARATOR + WHITE_LINE

        return string

    def visualize(self, ax: plt.Axes = None) \
            -> None:
        """
        Visualizes the results of the frequency analysis.

        This method uses the basic visualization method provided by the
        StatisticsStrategy base class to visualize the results in a Pandas
        DataFrame, and adds a Zipf frequency diagram.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            The axes on which to plot the data. If None, plots on the current
            axes.

        """
        super().visualize()

        data = self.to_dataframe().df

        self.diagram.frequency_diagram(
            data,
            col_name=type(self).CATEGORY,
            n_rows=15,
            title=f'{restrict_length(self.items.name, 20)}'
        )

    def to_string(self) \
            -> str:
        """
        Returns a string representation of the object, including various
        statistics and examples derived from the items.

        Returns
        -------
        str
            The string representation of the object.

        """

        n_examples = MAX_ITEMS
        item = f'{self.item_type}'.lower()
        items = f'{item}s'

        string = WHITE_LINE + \
                 SEPARATOR + \
                 WHITE_LINE + \
                 f'{type(self).__name__} of {self.items.name} \n' + \
                 '(Examples) \n' + \
                 SUBSEPARATOR + \
                 WHITE_LINE + \
                 (
                     f'Number of {items}:            '
                     f'{self.items.n_elements} \n'
                 ) + \
                 SUBSEPARATOR + \
                 WHITE_LINE + \
                 (
                     f'Average {item} frequency:           '
                     f'{self.mean_value}  \n'
                 ) + \
                 (
                     f'Up to {n_examples} example {items} '
                     f'with frequency close to average: \n'
                 ) + \
                 f'{self.examples_near_means} \n' + \
                 (
                     f'Median {item} frequency:         '
                     f'{self.median_value}  \n'
                 ) + \
                 (
                     f'Up to {n_examples} example {items} '
                     f'with close to median frequency: \n'
                 ) + \
                 f'{self.examples_near_median} \n' + \
                 (
                     f'Lowest {item} frequency:       '
                     f'{self.lowest_value}  \n'
                 ) + \
                 (
                     f'Up to {n_examples} examples '
                     f'of least frequent {items}: \n'
                 ) + \
                 f'{self.examples_lowest_values} \n' + \
                 (
                     f'Highest {item} frequency:        '
                     f'{self.highest_value}  \n'
                 ) + \
                 (
                     f'Up to {n_examples} examples '
                     f'of most frequent {items}: \n'
                 ) + \
                 f'{self.examples_highest_values} \n' + \
                 SEPARATOR + WHITE_LINE

        return string
