"""
dict_utils.py
-------------
Version 1.0, updated on 2025-01-26

This module provides functions for the handling of dictionaries, especially
for determining the specific dictionary structure, filtering a dictionary's
content, extracting items from it, converting the keys or the entire
dictionary to strings, etc.

Functions
---------
convert_keys_to_consecutive_str_numbers(data: Dict[Any, Any])
        -> Dict[str, Any]:
    Converts the keys to consecutive numbers formatted as strings.

dict_to_string(my_dict: Dict[DictKeyType, Any]) -> str:
    Converts a dictionary into a string.

filter_dict_by_value(my_filter: Any, my_dict: Dict[DictKeyType, Any])
        -> Dict[DictKeyType, Any]:
    Filters a dictionary by matching its values to a specified filter.

filter_dict_keys_by_value(my_dict: Dict[DictKeyType, str | int | float],
        my_filter: str | int | float) -> List[DictKeyType]:
    Extracts the keys of a dictionary whose values match a specified value.

get_key_by_index(my_dict: Dict[DictKeyType, Any], idx: int) -> DictKeyType:
    Retrieves the key at the specified index in the dictionary.

get_n_items_from_bottom(my_dict: Dict[DictKeyType, Any], n_items: int)
        -> Dict[DictKeyType, Any]:
    Extracts the given number of items from the end of a dictionary.

get_n_items_from_top(my_dict: Dict[DictKeyType, Any], n_items: int)
        -> Dict[DictKeyType, Any]:
    Extracts the given number of items from the start of a dictionary.

is_dict_of_dicts(data: Dict) -> bool:
    Checks if the provided dictionary is a dictionary of dictionaries.

is_dict_of_list_of_str_int_tuples(data: Dict) -> bool:
    Checks if the provided dictionary's values are lists of (str, int) tuples.

"""

import inspect
from functools import singledispatch
from itertools import islice
from math import floor, ceil
from typing import Dict, List, Any

from src.data_structures.item_list import ItemList
from logger import Logger
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.list_utils import list_to_string, is_list_of_str_int_tuples
from type_aliases import DictKeyType


def dict_to_string(my_dict: Dict[DictKeyType, Any]) \
        -> str:
    """
       Converts a dictionary into a string.

       This function takes a dictionary as input and converts it into a string
       by concatenating each key-value pair into the format "key: value". Each
       pair is separated by a tab and a space and ensures that no single line
       exceeds 80 characters in length. If the concatenated string would
       exceed 80 characters, it is split into multiple lines.

       Parameters
       ----------
       my_dict : Dict[DictKeyType, Any]
           The dictionary to be converted into a string. The dictionary can
           contain any type of objects as keys and values, as long as they can
           be converted into strings.

       Returns
       -------
       str
           THe string representation of the dictionary where each key-value
           pair is separated by a tab and a space and lines do not exceed 80
           characters in length. Each line is terminated with a newline
           character, except possibly the last one. Will be an empty string if
           the dictionary is empty.

       Examples
       --------

       .. code-block:: python

           >>> dict_to_string({'apple': 1, 'banana': 2, 'cherry': 3})
           'apple: 1\t banana: 2\t cherry: 3\t \n'

           >>> dict_to_string({1: 'a', 2: 'b', 3: 'c'})
           '1: a\t 2: b\t 3: c\t \n'

       Notes
       -----
       - The function uses 'list_to_string' from 'utils.list_utils' to format
         the list of key-value pairs into the desired string format. This
         ensures consistency in handling line lengths and formatting.

       - Similar to the list_to_string function, this function is used for
         providing examples of string representations of dictionary items. To
         structure the textual output, the string representation of the
         provided dictionary is indented by a tab and a space ('\t ')
         preceding each line.

       - Special characters in keys or values (such as newlines or tabs) are
         not escaped or handled specially, which might affect the formatting
         or readability of the output string.

       """

    # Using list comprehension to convert all dictionary items into strings,
    # storing them in 'lst'.
    lst = [str(key) + f': {str(value)}' for (key, value) in my_dict.items()]

    # Use list_to_string to get a string representation of the generated list.
    return list_to_string(lst)


def filter_dict_by_keys(
        keys: List[DictKeyType],
        my_dict: Dict[DictKeyType, Any]
) -> Dict[DictKeyType, Any]:
    """
    Filters a dictionary by matching its keys to a list of specified keys.

    Parameters
    ----------
    keys : List[DictKeyType]
        The list of keys to match in the dictionary.

    my_dict : Dict[DictKeyType, Any]
        The dictionary to filter.

    Returns
    -------
    Dict[DictKeyType, Any]
        A new dictionary containing the items that have been found to match
        the key criteria.

    """

    return {key: val for key, val in my_dict.items() if key in keys}


@singledispatch
def filter_dict_by_value(
        my_filter: Any,
        my_dict: Dict[DictKeyType, Any]
) -> Dict[DictKeyType, Any]:
    """
    Filters a dictionary by matching its values to a specified filter.

    This generic function defines the default behaviour of a single-dispatch
    mechanism. It handles cases where the filter value provided is not an 
    int or float by looking for exact matches in the dictionary's values.

    Parameters
    ----------
    my_filter : Any
        The filter value used to select items from the dictionary.

    my_dict : Dict[DictKeyType, Any]
        The dictionary to filter.

    Returns
    -------
    Dict[DictKeyType, Any]
        A new dictionary containing the items that have been found to match
        the filter criteria.

    """

    return {key: val for key, val in my_dict.items() if val == my_filter}


@filter_dict_by_value.register(int)
@filter_dict_by_value.register(float)
def _(
        my_filter: float | int,
        my_dict: Dict[DictKeyType, Any],
) -> Dict[DictKeyType, Any]:
    """
    Extracts dictionary items with values within a specified numerical range.

    This function is part of a single-dispatch mechanism named
    "filter_dict_by_value". It handles cases where the filter value provided
    is a number (int or float).

    Based on the provided filter value, this function sets a minimum and a
    maximum value for the range of values in which to search for dictionary
    items. If the range is too small and no items are found within it,
    the range is expanded until at least one match is found.

    This function is used for selecting dictionary items that represent
    statistical outliers or averages, such as items close to the median, mean,
    maximum or minimum values of a dataset's characteristic (e.g., length of
    text strings, frequency of words).

    Parameters
    ----------
    my_filter : float | int
        The filter value used to select items from the dictionary.

    my_dict : Dict[DictKeyType, Any]
        The dictionary to filter.

    Returns
    -------
    Dict[DictKeyType, Any]
        A new dictionary containing items where values matched the filter 
        criteria.

    Examples
    --------

    .. code-block:: python

        >>> from src.utils.dict_utils import filter_dict_by_value

        >>> ex_my_dict = {'a': 1, 'b': 2.5, 'c': 3, 'd': 4.5}
        >>> filter_dict_by_value(2.5, ex_my_dict)
        {'b': 2.5}

        >>> filter_dict_by_value(3, ex_my_dict)
        {'c': 3}

        >>> filter_dict_by_value(2.7, ex_my_dict)
        {'b': 2.5}

    Notes
    -----
    If the filter is a floating point number, it is improbable that the
    dictionary contains items that directly match the exact number.
    Therefore, in this case, the function directly computes a range of
    values, in which to search for dictionary items.

    If the filter is an integer, the initial range of values is set so that
    in a first attempt, it is searched for a dictionary item that matches the
    exact filter value provided.

    In both cases, if no matches are found within the initial range,
    the range is gradually expanded until at least one match is found.

    """

    # set the initial range
    if isinstance(my_filter, float):
        min_filter, max_filter = floor(my_filter), ceil(my_filter)
    else:  # my_filter is int
        min_filter, max_filter = my_filter, my_filter + 1

    counter = sum(
        1 for val in my_dict.values()
        if min_filter <= val <= max_filter
    )

    # expand the range while no match is found
    while counter == 0:
        min_filter -= 1
        max_filter += 1
        counter = sum(
            1 for val in my_dict.values()
            if min_filter <= val < max_filter
        )

    return {
        key: val for key, val in my_dict.items()
        if min_filter <= val <= max_filter
    }


def filter_dict_keys_by_value(
        my_dict: Dict[DictKeyType, str | int | float],
        my_filter: str | int | float
) -> List[DictKeyType]:
    """
    Extracts the keys of a dictionary whose values match a specified value.

    This function iterates through the given dictionary, 'my_dict', and
    compiles a list of keys whose corresponding values match the 'my_filter'
    value.

    Parameters
    ----------
    my_dict : Dict[DictKeyType, str | int | float]
        The dictionary whose keys are to be extracted if their values match
        the specified filter. The dictionary's keys can be of type
        'str' or 'int', and the values can be of type 'str', 'int', or 'float'.

    my_filter : str | int | float
        The value the dictionary values must match for their keys to be
        included in the returned list of keys. Corresponding to the possible
        types the dictionary values can have, the filter can be of type 
        'str', 'int', or 'float'.

    Returns
    -------
    List[DictKeyType]
        A list of keys from 'my_dict' whose values match 'my_filter'. The keys
        in the returned list will be of the same type as they are in 'my_dict'.

    Examples
    --------

    .. code-block:: python

        >>> ex_my_dict = {'a': 1, 'b': 2, 'c': 1}
        >>> filter_dict_keys_by_value(ex_my_dict, 1)
        ['a', 'c']

        >>> ex_my_dict = {1: 'apple', 2: 'banana', 3: 'apple'}
        >>> filter_dict_keys_by_value(ex_my_dict, 'apple')
        [1, 3]

    Notes
    -----
    - If no keys match the 'my_filter' value, an empty list is returned.

    - The order of the keys in the returned list follows the order they appear
      in 'my_dict'.

    """

    return [key for key, value in my_dict.items() if value == my_filter]


def get_key_by_index(my_dict: Dict[DictKeyType, Any], idx: int) \
        -> DictKeyType:
    """
    Retrieves the key at the specified index in the dictionary.

    Parameters
    ----------
    my_dict : Dict[DictKeyType, Any]
        The dictionary from which the key is to be retrieved.

    idx : int
        The index of the key to retrieve.

    Returns
    -------
    DictKeyType
        The key at the specified index in the dictionary, or None if the index
        is out of bounds.

    """

    try:
        return list(my_dict.keys())[idx]
    except IndexError:
        return None


def get_n_items_from_top(
        my_dict: Dict[DictKeyType, Any],
        n_items: int
) -> Dict[DictKeyType, Any]:
    """
    Extracts the given number of items from the start of a dictionary.

    This function maintains the order of the extracted items as they appear in
    the original dictionary.

    Parameters
    ----------
    my_dict : Dict[DictKeyType, Any]
        The input dictionary from which to extract items.

    n_items : int
        The number of items to extract from the start of the dictionary.

    Returns
    -------
    Dict[DictKeyType, Any]
        A new dictionary containing the first 'n_items' from the input
        dictionary, preserving their order.

    Raises
    ------
    TypeError
        If 'n_items' is not an integer.

    CriticalException
        If 'n_items' is negative.

    Examples
    --------

    .. code-block:: python

        >>> ex_my_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        >>> get_n_items_from_top(ex_my_dict, 2)
        {'a': 1, 'b': 2}

        >>> ex_my_dict = {'apple': 'green', 'carrot': 'orange', 'pear': 'yellow'}
        >>> get_n_items_from_top(ex_my_dict, 1)
        {'apple': 'green'}

    Notes
    -----
    - The function returns an empty dictionary
      - if 'n_items' is 0
      - or if the input dictionary is empty.

    - If 'n_items' is greater than the number of items in the input
      dictionary, the function returns a copy of the entire dictionary.

    """

    if n_items < 0:
        raise CriticalException(
            Logger(f"{inspect.currentframe().f_code.co_name}").get_logger(),
            'The number of items in a dictionary cannot be negative.'
        )

    # Use dictionary comprehension to extract the wanted number of items
    # from the start of the dictionary:
    return {key: my_dict[key] for key in list(my_dict)[:n_items]}


def get_n_items_from_bottom(
        my_dict: Dict[DictKeyType, Any],
        n_items: int
) -> Dict[DictKeyType, Any]:
    """
    Extracts the given number of items from the end of a dictionary.

    This function returns the extracted items in reverse order compared to
    their order in the original dictionary.

    Parameters
    ----------
    my_dict : Dict[DictKeyType, Any]
        The input dictionary from which to extract items.

    n_items : int
        The number of items to extract from the end of the dictionary.

    Returns
    -------
    Dict[DictKeyType, Any]
        A new dictionary containing the last 'n_items' from the input
        dictionary, in reverse order.

    Raises
    ------
    CriticalException
        If 'n_items' is negative or if it is not an integer.

    Examples
    --------

    .. code-block:: python

        >>> ex_my_dict = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        >>> get_n_items_from_bottom(ex_my_dict, 2)
        {'c': 3, 'd': 4}

        >>> ex_my_dict = {'apple': 'fruit', 'carrot': 'vegetable', 'pear': 'fruit'}
        >>> get_n_items_from_bottom(ex_my_dict, 1)
        {'pear': 'fruit'}

    Notes
    -----
    - The function returns an empty dictionary
      - if 'n_items' is 0
      - or if the input dictionary is empty.

    - If 'n_items' is greater than the number of items in the input
      dictionary, the function returns a copy of the entire dictionary.

    """

    if n_items < 0:
        raise CriticalException(
            Logger(f"{inspect.currentframe().f_code.co_name}").get_logger(),
            'The number of items in a dictionary cannot be negative.'
        )

    # Reverse the dictionary items and take the last n_items
    last_n_items = islice(reversed(my_dict.items()), 0, n_items)

    # Convert the sliced items back into a dictionary
    new_dict = dict(list(last_n_items))

    return new_dict


def value_is_in_dict(value: Any, my_dict: Dict) \
        -> bool:
    """
    Checks whether a value is in a dictionary as the value of one of its keys.

    Parameters
    ----------
    value : Any
        The value to check.

    my_dict : Dict
        The dictionary to check.

    Returns
    -------
    bool
        True if the value is in the dictionary, False otherwise.

    """

    return any(val == value for val in my_dict.values())


def dict_is_in_list_of_dicts(item: Dict, data: List[Dict]) \
        -> bool:
    """
    Checks whether a dictionary is in a list of dictionaries.

    Parameters
    ----------
    item : Dict
        The dictionary to check.

    data : List[Dict]
        The list of dictionaries to check.

    Returns
    -------
    bool
        True if the dictionary is in the list, False otherwise.

    """

    #return item in data
    return any(d == item for d in data)


def is_dict_of_dicts(data: Dict) \
        -> bool:
    """
    Checks if the provided dictionary is a dictionary of dictionaries.

    Parameters
    ----------
    data : Dict
       The dictionary to check.

    Returns
    -------
    bool
       True if the provided dictionary's values are all dictionaries, False
       otherwise.

    """

    if not isinstance(data, dict):
        return False

    for key, value in data.items():
        if not isinstance(value, dict):
            return False

    return True


def is_dict_of_list_of_str_int_tuples(data: Dict) \
        -> bool:
    """
    Checks if the provided dictionary's values are lists of (str, int) tuples.

    Parameters
    ----------
    data : Dict
       The dictionary to check.

    Returns
    -------
    bool
       True if all values in the dictionary are lists of (str, int) tuples,
       False otherwise.

    """

    if not isinstance(data, dict):
        return False

    for key, value in data.items():
        if not is_list_of_str_int_tuples(value):
            return False

    return True


def convert_keys_to_consecutive_str_numbers(data: Dict[Any, Any]) \
        -> Dict[str, Any]:
    """
    Converts the keys to consecutive numbers formatted as strings.

    Replaces the keys of the given Dictionary by consecutive numbers
    formatted as strings.

    Parameters
    ----------
    data : Dict[Any, Any]
        The dictionary whose keys are to be converted.

    Returns
    -------
    Dict[str, Any]
        The dictionary with the converted keys.

    """

    values = data.values()

    data = {str(index + 1): value for index, value in enumerate(values)}

    return data


def merge_dicts(
        dict1: Dict[str, List[Any]],
        dict2: Dict[str, List[Any]]
) -> Dict[str, List[Any]]:
    """
    Merges two dictionaries of type Dict[str, List[Any]].

    If a key exists in both dictionaries, their lists are merged.
    If a key exists in only one dictionary, it is added as is.

    """

    merged_dict = dict1.copy()

    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key].extend(value)
        else:
            merged_dict[key] = value.copy()

    return merged_dict


def exclude_list_elements_from_dict(
        dict1: Dict[str, List[Any]], dict2: Dict[str, List[Any]]
) -> Dict[str, List[Any]]:
    """
    "Subtracts" lists from dict1 using dict2 based on matching keys.

    Excludes elements from lists in dict1 based on matching lists and their
    elements in dict2.

    Prints a warning
        - If a key exists in dict2 but not in dict1.
        - If an element to be removed is not in the corresponding list in
          dict1.

    """

    result = dict1.copy()

    for key, values_to_remove in dict2.items():
        if key not in result:
            print(f"WARNING: Key '{key}' found in dict2 but not in dict1.")
            continue

        for value in values_to_remove:
            if value in result[key]:
                result[key].remove(value)
            else:
                print(
                    f"WARNING: Value '{value}' not found in list for key "
                    f"'{key}' in dict1.")

    return result


def unique(data: Dict[Any, Any]) \
        -> Dict[Any, Any]:
    """
    Returns the given dictionary with unique elements only.

    Parameters
    ----------
    data : Dict
        The input dictionary.

    Returns
    -------
    Dict
        The dictionary with unique elements only.

    """

    seen = set()
    result = {}

    for key, value in data.items():
        # Convert dictionary values to tuples if necessary to ensure hashability
        value_to_check = tuple(value.items()) \
            if isinstance(value, dict) else value

        if value_to_check not in seen:
            seen.add(value_to_check)
            result[key] = value

    return result


def get_values_for_inner_key(data: Dict[Any, Dict[Any, Any]], key: Any) \
        -> ItemList:
    """
    Returns the values for an inner key in a dictionary of dictionaries.

    The values are collected into an ItemList. Double values are kept.

    Parameters
    ----------
    data : Dict[Any, Dict[Any, Any]]
        The dictionary of dictionaries.

    key : Any
        The key of the inner dictionary.

    Returns
    -------
    ItemList
        The values for the inner key.

    """

    return ItemList(
        [entry[key] for entry in data.values()],
        "inner_values"
    )


def get_unique_values_for_inner_key(data: Dict[Any, Dict[Any, Any]], key: Any) \
        -> List[Any]:
    """
    Returns the unique values for an inner key in a dictionary of dictionaries.

    Parameters
    ----------
    data : Dict[Any, Dict[Any, Any]]
        The dictionary of dictionaries.

    key : Any
        The key of the inner dictionary.

    Returns
    -------
    List[Any]
        The unique values for the inner key.

    """

    return list(set([entry[key] for entry in data.values()]))


def are_all_values_equal_for_key(data: Dict[Any, Dict[Any, Any]], key: Any) \
        -> bool:
    key_values = [entry[key] for entry in data.values()]

    return all(value == key_values[0] for value in key_values)


def get_inner_keys_of_dict_of_dict(data: Dict[Any, Dict[Any, Any]]) \
        -> List[Any]:
    keys = set()
    for inner_dict in data.values():
        keys.update(inner_dict.keys())

    return list(keys)


def find_dict_of_dicts_entries_with_same_values_for_inner_key(
        data: Dict[Any, Dict[Any, Any]],
        key: Any,
        value: Any
) -> List[Any]:
    return [outer_key for outer_key, inner_dict in data.items()
            if inner_dict.get(key) == value]
