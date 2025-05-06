"""
list_sort_utils.py
------------------
Version 1.0, validated on 2024-09-10

This module provides sorting utilities for lists.

Functions
---------
sort_list(lst: List[T] | Set[T] | Tuple[T, ...]) -> List[T]:
    Sorts a tuple, list or set of strings or numbers.

sort_list_of_tuples_by_desc_second_element_asc_first(
        lst: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
    Sorts a list of tuples by the second tuple element in descending order.

sort_list_with_int_behind_last_underscore(lst: List[str]) -> List[str]:
    Sorts a list of strings with an integer behind the last underscore.

"""

from typing import List, Set, Tuple, TypeVar

from src.logging_mixin import LoggingMixin
from src.utils.string_utils import StringUtils

# Define a type variable that can be str, int, or float
T = TypeVar('T', str, int, float)

log = LoggingMixin().log


def sort_list(
        lst: List[T] | Set[T] | Tuple[T, ...]
) -> List[T]:
    """
    Sorts a tuple, list or set of strings or numbers.

    Takes a list, a set or a tuple as input.

    Parameters
    ----------
    lst : List[T] | Set[T] | Tuple[T, ...]
        The list, set or tuple of strings or numbers to be sorted.

    Returns
    -------
    List[T]
        The sorted list of strings or numbers.

    Raises
    ------
    TypeError
        If the input mixes strings and numbers (int or float).

    Notes
    -----
    - If a set with duplicate values is given, the sorted list will contain
      only one of the duplicate values.
      
    - Upper case strings are sorted in front of lower case strings:
      A, B, ... a, b, ...
      
    """

    # Check for mixed types of str and numeric types
    if (any(isinstance(el, str) for el in lst) and
            not all(isinstance(el, str) for el in lst)):
        msg = "Input cannot mix strings and numbers"
        log(msg, "error")
        raise TypeError(msg)

    return sorted(lst)


def sort_list_with_int_behind_last_underscore(lst: List[str]) \
        -> List[str]:
    """
    Sorts a list of strings with an integer behind the last underscore.

    Sorts the strings first alphabetically by the first part of the strings
    and then numerically by the integer at the end of the strings.

    Parameters
    ----------
    lst : List[str]
        List of strings with integers behind the last underscores.

    Returns
    -------
    List[str]
        The alphanumerically sorted list of strings.

    """

    return sorted(
        lst, key=lambda x: (
            StringUtils.get_str_before_last_underscore(x),
            StringUtils.get_int_behind_last_underscore(x)
        )
    )


def sort_list_of_tuples_by_desc_second_element_asc_first(
        lst: List[Tuple[str, int]]
) -> List[Tuple[str, int]]:
    """
    Sorts a list of tuples by the second tuple element in descending order.
    
    Sorts a list of tuples first by the value of the second tuple element in 
    descending order and then by the value of the first element in 
    alphabetical order.
    
    Parameters
    ----------
    lst : List[Tuple[str, int]]
        The list of tuples to be sorted. The first element in each tuple is 
        a string, whereas the second one is an integer, e.g. a frequency.

    Returns
    -------
    List[Tuple[str, int]]
        The sorted list of tuples.
        
    """

    return sorted(lst, key=lambda x: (-x[1], x[0]))
