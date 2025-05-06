"""
length_strategy.py
------------------
Version 1.0, updated on 2024-12-04

"""

from __future__ import annotations

from constants import MAX_ITEMS
from src.data_structures.item_list import ItemList
from src.data_structures.my_ordered_dict import MyOrderedDict
from src.stats.statistics_strategy import StatisticsStrategy
from src.utils.dict_sort_utils import sort_dict_by_asc_values_and_asc_keys
from src.utils.print_utils import WHITE_LINE, SEPARATOR, SUBSEPARATOR


class LengthStrategy(StatisticsStrategy):
    """
    This class is a concrete implementation of the StatisticsStrategy
    interface for statistical analyses. This strategy is used for the analysis
    of lengths of given items (typically string items) collected in an
    ItemList object.

    """

    CATEGORY = 'Length'

    def __init__(self, items: ItemList) -> None:
        """
        Constructor.

        """
        super().__init__(items, self.CATEGORY)

    # region --- Methods

    def compute_items_and_values(self):
        self._items_and_values = self.__compute_string_lengths()

    def compute_item_ids_and_values(self):
        self._item_ids_and_values = self.__compute_string_lengths_by_id()

    def __compute_string_lengths(self) \
            -> MyOrderedDict:
        """
        Get string lengths of items.

        Get ordered dictionary of distinct item strings
        and their lengths, sorted first by length
        and then alphabetically by item strings.

        
        """

        # Creating an empty dictionary
        lengths = {}
        for item in self.items.to_strings():
            if item not in lengths:
                lengths[item] = len(item)
        return sort_dict_by_asc_values_and_asc_keys(lengths)

    def __compute_string_lengths_by_id(self) \
            -> MyOrderedDict:
        """
        Get string lengths of items.

        Get ordered dictionary of distinct item strings
        and their lengths, sorted first by length
        and then alphabetically by item strings.

        
        """

        # Creating an empty dictionary
        lengths = []
        lengths_by_id = {}

        for item in self.items.to_strings():
            if item not in lengths:
                lengths.append(item)
                lengths_by_id[self.items.to_strings().index(item)] = len(item)
        return sort_dict_by_asc_values_and_asc_keys(lengths_by_id)

    def to_string_showing_ids(self) \
            -> str:
        item = f'{self.item_type}'.lower()
        items = f'{self.item_type}s'
        chars = 'characters'

        string = WHITE_LINE + \
                 SEPARATOR + \
                 WHITE_LINE + \
                 f'\n{type(self).__name__} of {self.items.name} \n' + \
                 '(All IDs) \n' + \
                 SUBSEPARATOR + \
                 WHITE_LINE + \
                 (
                     f'Number of {items}:            '
                     f'{self.items.n_elements} \n'
                 ) + \
                 SUBSEPARATOR + \
                 WHITE_LINE + \
                 (
                     f'Mean {item} length:           '
                     f'{self.mean_value} {chars} \n'
                 ) + \
                 f'{items} close to the length means: \n' + \
                 f'{self.ids_near_means} \n' + \
                 (
                     f'Median {item} length:         '
                     f'{self.median_value} {chars} \n'
                 ) + \
                 f'{items} close to the length median: \n' + \
                 f'{self.ids_near_median} \n' + \
                 (
                     f'Shortest {item} length:       '
                     f'{self.lowest_value} {chars} \n'
                 ) + \
                 f'Shortest {items.lower()}: \n' + \
                 f'{self.lowest_value_ids} \n' + \
                 (
                     f'Longest {item} length:         '
                     f'{self.highest_value} {chars} \n'
                 ) + \
                 f'Longest {items.lower()}:\n' + \
                 f'{self.highest_value_ids} \n' + \
                 SEPARATOR + WHITE_LINE

        return string

    def to_string(self) \
            -> str:
        n_examples = MAX_ITEMS
        item = f'{self.item_type}'.lower()
        items = f'{item}s'
        chars = 'characters'

        string = WHITE_LINE + \
                 SEPARATOR + \
                 WHITE_LINE + \
                 f'{type(self).__name__} of {self.items.name} \n' + \
                 'Examples \n' + \
                 SUBSEPARATOR + \
                 WHITE_LINE + \
                 (
                     f'Number of {items}:            '
                     f'{self.items.n_elements} \n'
                 ) + \
                 SUBSEPARATOR + \
                 WHITE_LINE + \
                 (
                     f'Mean {item} length:           '
                     f'{self.mean_value} {chars} \n') + \
                 (
                     f'Up to {n_examples} example {items} '
                     f'close to the length means: \n'
                 ) + \
                 f'{self.examples_near_means}\n' + \
                 (
                     f'Median {item} length:         '
                     f'{self.median_value}  {chars}\n'
                 ) + \
                 (
                     f'Up to {n_examples} example {items} '
                     f'close to the length median: \n'
                 ) + \
                 f'{self.examples_near_median} \n' + \
                 (
                     f'Shortest {item} length:       '
                     f'{self.lowest_value} {chars} \n'
                 ) + \
                 (
                     f'Up to {n_examples} examples '
                     f'of the shortest {items} : \n'
                 ) + \
                 f'{self.examples_lowest_values} \n' + \
                 (
                     f'Longest {item} length:       '
                     f'{self.highest_value} {chars} \n'
                 ) + \
                 (
                     f'Up to {n_examples} examples '
                     f'of the longest {items} :\n'
                 ) + \
                 f'{self.examples_highest_values} \n' + \
                 SEPARATOR + WHITE_LINE

        return string

    # endregion --- Methods
