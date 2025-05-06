"""
dict_sort_utils.py
------------------
Version 1.0, updated on 2024-12-04

This module provides sorting utilities for dictionaries.

Functions
---------
sort_dict_by_asc_values_and_asc_keys(my_dict: Dict) -> MyOrderedDict:
    Sorts a dictionary by ascending values.

sort_dict_by_desc_values_and_asc_keys(my_dict: Dict) -> MyOrderedDict:
    Sorts a dictionary first by descending values, then by ascending keys.

"""

from typing import Dict, OrderedDict, Any

from src.data_structures.my_ordered_dict import MyOrderedDict


# region --- Public Functions

def sort_dict_by_asc_values_and_asc_keys(my_dict: Dict) \
        -> MyOrderedDict:
    """
    Sorts a dictionary by ascending values.

    If there are several keys with the same value, the keys are also sorted
    in ascending order.

    Parameters
    ----------
    my_dict: Dict
        The dictionary to sort.

    Returns
    -------
    MyOrderedDict
        The ordered dictionary.

    """

    sorted_dict = MyOrderedDict(
        OrderedDict[str, Any](
            sorted(
                my_dict.items(),
                key=__sort_key_for_sort_by_value
            )
        )
    )
    return sorted_dict


def sort_dict_by_desc_values_and_asc_keys(my_dict: Dict) \
        -> MyOrderedDict:
    """
    Sorts a dictionary first by descending values, then by ascending keys.

    ATTENTION: Can only be used if the values are numbers,
    not strings!

    Parameters
    ----------
    my_dict: Dict
        The dictionary to sort.

    Returns
    -------
    MyOrderedDict
        The ordered dictionary.

    """

    sorted_dict = MyOrderedDict(
        OrderedDict[str, Any](
            sorted(
                my_dict.items(),
                key=__sort_key_for_desc_value_asc_key
            )
        )
    )
    return sorted_dict


# endregion --- Public Functions

# region --- Private Functions

def __sort_key_for_sort_by_value(item):
    key, value = item
    return value, key


def __sort_key_for_desc_value_asc_key(item):
    """
    ATTENTION: Can only be used if the values are numbers,
    not strings!

    """

    key, value = item
    return -value, key

# endregion --- Private Functions
