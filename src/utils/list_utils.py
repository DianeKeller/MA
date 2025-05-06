"""
list_utils.py
-------------
Version 1.0, updated on 2025-05-01

This module provides functions for the handling of lists and tuples.

Functions
---------
are_all_elements_included(partial_list: list, complete_list: list) -> bool:
    Checks if the given partial list is contained in the given complete list.
    
are_all_of_the_same_type(lst: List[Any] | Tuple[Any]) -> bool:
    Checks if the elements of the given list or tuple are all of the same type.

def filter_list_of_tuples_by_min_second_element(
        lst: List[Tuple[Any, Any]],
        min_value: Any
) -> List[Tuple[Any, Any]]:
    Filters a list of tuples based on a minimum value for the second element.

def filter_list_of_tuples_by_second_element(lst: List[Tuple[Any, Any]],
        element: Any) -> List[Tuple[Any, Any]]:
    Filters a list of tuples based on the second element of each tuple.

get_common_elements(first_list: list[T], second_list: list[T]) -> list[T]:
    Returns a list of elements that two input lists have in common.

get_elements_by_substring(lst: List[str], substr: str) -> List[str]:
    Retrieves all elements in a list that contain the specified substring.

get_first_elements_from_list_of_tuples(lst: List[Tuple[Any, Any]])
        -> List[Any]:
    Extracts the first elements from all tuples in the given list.

get_first_elements_from_tuple_list_by_second_element(
        lst: List[Tuple[Any, Any]], element: Any) -> List[Any]:
    Extracts the first elements from all tuples by the second elements.

get_second_elements_from_list_of_tuples(lst: List[Tuple[Any, Any]])
        -> List[Any]:
    Extracts the second elements from all tuples in the given list.

have_intersection(first_list: list, second_list: list) -> bool:
    Check if the intersection of two lists is not empty.

is_flat(lst: Sequence) -> bool:
    Check if the given list is flat.

is_list_of_str_int_tuples(data: List[Tuple[str, int]]) -> bool:
    Checks if the provided list contains only (str, int) tuples.

is_str_int_tuple(data: Tuple[str, int]) -> bool:
    Checks if the provided tuple is of the form (str, int).

is_subset(partial_list: list, complete_list: list) -> bool:
    Checks whether all elements in 'partial_list' are contained in
`complete_list`.

is_substring_of_list_content(substring: str, lst: List[str]) -> bool:
    Checks if a given substring exists in any of the strings within a list.

list_to_string(lst: Iterable[Any]) -> str:
    Converts a list or set of elements into a formatted string.

remove_elements_from_list(lst: List[Any], elements_to_remove: List[Any])
        -> List[Any]:
    Removes specified elements from a list.

remove_tuples_from_list_of_tuples(
        tuples: List[Tuple[str, ...]], tuples_to_remove: List[Tuple[str, ...]])
        -> List[Tuple[str, ...]]:
    Removes specified tuples from a list of tuples.

"""

import itertools
from typing import List, Set, Any, Tuple, Sequence, TypeVar, Dict, Counter

from src.utils.type_utils import is_int
from type_aliases import ExamplesType

T = TypeVar('T')


def are_all_elements_included(partial_list: list, complete_list: list) \
        -> bool:
    """
    Checks if the given partial list is contained in the given complete list.
    
    Checks whether all elements in 'partial_list' are contained in
    'complete_list'.

    Parameters
    ----------
    partial_list : list
       List of elements.

    complete_list : list
       Potentially more extensive list of elements.

    Returns
    -------
    bool
       - True if all elements in 'partial_list' are found in 'complete_list'.
       - False if there are elements in 'partial_list' that are not found
         in 'complete_list'.

    Notes
    -----
    This function is optimized for small lists where the linear search time
    for each element does not significantly impact performance. It directly
    checks each element's presence, making it straightforward but potentially
    slower for large lists due to linear search complexity.

    """

    return all(el in complete_list for el in partial_list)


def is_subset(partial_list: list, complete_list: list) \
        -> bool:
    """
    Checks whether all elements in 'partial_list' are contained in
    'complete_list`.

    Parameters
    ----------
    partial_list : list
       List of elements.

    complete_list : list
       Potentially more extensive list of elements.

    Returns
    -------
    bool
       - 'True' if all elements in 'partial_list' are found in 'complete_list'.
       - 'False' if there are elements in 'partial_list' that are not found
         in 'complete_list'.

    Notes
    -----
    This function is optimized for large lists by converting them to sets,
    which allows for constant-time membership checks. However, it does not
    account for the multiplicity of elements, as sets only consider element
    uniqueness. This approach is most effective when the lists are large and
    the exact count of duplicate elements is not critical for the subset check.

    """

    return set(partial_list).issubset(set(complete_list))


def have_intersection(first_list: list, second_list: list) \
        -> bool:
    """
    Check if the intersection of two lists is not empty.

    Parameters
    ----------
    first_list: list
        The first list to check.

    second_list: list
        The second list to check.

    Returns
    -------
    bool
        - True if the intersection of the two lists is not empty.
        - False otherwise.

    """

    return not set(first_list).isdisjoint(set(second_list))


def get_common_elements(first_list: list[T], second_list: list[T]) \
        -> list[T]:
    """
    Returns a list of elements that two input lists have in common.

    Parameters
    ----------
    first_list[T]: list
        The first list to compare with the second list.

    second_list[T]: list
        The second list to compare with the first list.

    Returns
    -------
    list[T]
        The list of elements that both input lists have in common.

    """

    # Convert second_list to a set to also allow for large lists
    second_set = set(second_list)
    return [item for item in first_list if item in second_set]


def is_flat(lst: Sequence) \
        -> bool:
    """
    Check if the given list is flat.

    Verify that the list contains no nested data types.

    Parameters
    ----------
    lst: list
        The list to check.

    Returns
    -------
    bool:
        - True if the list is flat.
        - False otherwise.

    """

    for element in lst:
        if isinstance(element, (list, tuple, set, dict)):
            return False

    return True


def are_all_of_the_same_type(lst: List[Any] | Tuple[Any]) \
        -> bool:
    """
    Checks if the elements of the given list or tuple are all of the same type.

    Parameters
    ----------
    lst: List[Any] | Tuple[Any]
        The list or tuple to check.

    Returns
    -------
    bool:
        - True if the elements are all of the same type.
        - False otherwise.

    Notes
    -----
    This function works for lists and tuples.

    """

    # Compare the types of all elements with the type of the first element.
    return all(isinstance(el, type(lst[0])) for el in lst)


def get_first_elements_from_list_of_tuples(lst: List[Tuple[Any, Any]]) \
        -> List[Any]:
    """
    Extracts the first elements from all tuples in the given list.

    Parameters
    ----------
    lst : List[Tuple[Any, Any]]
        The list of tuples to get the elements from.

    Returns
    -------
    List[Any]
        The extracted list of first elements.

    """

    return [t[0] for t in lst]


def get_second_elements_from_list_of_tuples(lst: List[Tuple[Any, Any]]) \
        -> List[Any]:
    """
    Extracts the second elements from all tuples in the given list.

    Parameters
    ----------
    lst : List[Tuple[Any, Any]]
        The list of tuples to get the elements from.

    Returns
    -------
    List[Any]
        The extracted list of second elements.

    """

    return [t[1] for t in lst]


def get_first_elements_from_tuple_list_by_second_element(
        lst: List[Tuple[Any, Any]],
        element: Any
) -> List[Any]:
    """
    Extracts the first elements from all tuples by the second elements.

    Extracts the first elements from all tuples where the second elements
    match the given element.

    Parameters
    ----------
    lst : List[Tuple[Any, Any]]
        The list of tuples to get the elements from.

    element: Any
        The element the second elements must match for the first element to
        be included in the result list.

    Returns
    -------
    List[Any]
        The extracted list of first elements.

    """

    filtered_tuples = filter_list_of_tuples_by_second_element(lst, element)

    return get_first_elements_from_list_of_tuples(filtered_tuples)


def filter_list_of_tuples_by_second_element(
        lst: List[Tuple[Any, Any]],
        element: Any
) -> List[Tuple[Any, Any]]:
    """
    Filters a list of tuples based on the second element of each tuple.

    Parameters
    ----------
    lst : List[Tuple[Any, Any]]
        The list of tuples to filter.

    element : Any
         The value to compare against the second element of each tuple.

    Returns
    -------
    List[Tuple[Any, Any]]
        A list of tuples where the second element matches the specified value.

    """

    return [tup for tup in lst if tup[1] == element]

def filter_list_of_tuples_by_min_second_element(
        lst: List[Tuple[Any, Any]] | Counter,
        min_value: Any
) -> List[Tuple[Any, Any]]:
    """
    Filters a list of tuples based on a minimum value for the second element.

    Filters a list of tuples based on the condition that the second element of
    each tuple is greater than or equal to the specified value.


    Parameters
    ----------
    lst : List[Tuple[Any, Any]] | Counter
        The list of tuples to filter. May be of type "Counter".

    min_value : Any
         The minimum value to compare against the second element of each tuple.

    Returns
    -------
    List[Tuple[Any, Any]]
        A list of tuples where the second element is greater than or equal to
        the specified value.

    """

    if isinstance(lst, Counter):
        lst = list(lst.items())

    return [tup for tup in lst if int(tup[1]) >= min_value]


def list_to_string(lst: ExamplesType) \
        -> str:
    """
    Converts a list or set of elements into a formatted string.

    This function takes a list or set of elements, concatenates them into a
    string with elements separated by tabs and spaces, and ensures that no
    single line exceeds 80 characters in length. If the concatenated string
    would exceed 80 characters, it is split into multiple lines, with each
    line appended to the final string with a newline character.

    This function is used for providing examples of string elements
    collected in lists or sets, illustrating the results of statistical
    analyses of corpora, texts or parts of texts. To structure the
    textual output, the string representation of the provided list is indented
    by a tab and a space (`'\t '`) preceding each line.

    Parameters
    ----------
    lst : List[Any] | Set[Any]
        The list or set of elements to be converted into a string. The
        elements are expected to be stringifiable (i.e., they should
        implement the '__str__' or '__repr__' methods).

    Returns
    -------
    str
        A string representation of the list or set where elements are
        separated by tabs and spaces, and lines do not exceed 80 characters in
        length. Each line is terminated with a newline character, except
        possibly the last one. Will be an empty string if the list is empty.

    Examples
    --------

    .. code-block:: python

        >>> list_to_string(['apple', 'banana', 'pear'])
        '\t apple\t banana\t pear\t \n'

        >>> list_to_string({'apple', 'banana', 'pear'})
        '\t apple\t banana\t pear\t \n'

    Notes
    -----
    The function does not guarantee the order of elements when a set is passed
    due to the inherent unordered nature of sets. The final string's line
    breaks are designed to ensure readability and adherence to a maximum line
    length.

    Raises
    ------
    TypeError
        If any element in the list or set does not implement the '__str__' or
        '__repr__' method, resulting in a TypeError when attempting to
        concatenate non-string types.

    """

    lines = []
    line = '\t '

    # append elements to lines list if the total length exceeds 80 characters
    for el in lst:
        new_element = str(el) + '\t '
        if len(line + new_element) > 80:
            lines.append(line)
            line = '\t ' + new_element
        else:
            line += new_element

    # append the last line, if it has more than just initial tab and space
    if len(line.strip()) > 0:
        lines.append(line)

    # join lines into a single string with newline separation and ensure it
    # ends with "\n"
    result_string = '\n'.join(lines)

    if result_string:
        result_string += '\n'

    return result_string


def is_list_of_str_int_tuples(data: List[Tuple[str, int]]) \
        -> bool:
    """
    Checks if the provided list contains only (str, int) tuples.

    Parameters
    ----------
    data : List[Tuple[str, int]]
       The list to check.

    Returns
    -------
    bool
       True if all items in the list are (str, int) tuples, False otherwise.

    """

    if not isinstance(data, list):
        return False

    for item in data:
        if not is_str_int_tuple(item):
            return False

    return True


def is_str_int_tuple(data: Tuple[str, int]) \
        -> bool:
    """
    Checks if the provided tuple is of the form (str, int).

    Parameters
    ----------
    data : Tuple[str, int]
        The tuple to check.

    Returns
    -------
    bool
        True if the tuple consists of a string and an integer, False otherwise.

    """

    if not isinstance(data, tuple) or len(data) != 2:
        return False

    if not isinstance(data[0], str):
        return False

    if not is_int(data[1]):
        return False

    return True


def is_substring_of_list_content(substring: str, lst: List[str]) \
        -> bool:
    """
    Checks if a given substring exists in any of the strings within a list.

    Parameters
    ----------
    substring : str
       The substring to search for within the list of strings.

    lst : List[str]
       The list of strings in which to search for the substring.

    Returns
    -------
    bool
       True if the substring is found in any string in the list, False
       otherwise.

    Examples
    --------

    .. code-block:: python

        >>> is_substring_of_list_content("foo", ["bar", "foo", "baz"])
        True

        >>> is_substring_of_list_content("xyz", ["bar", "foo", "baz"])
        False

    """

    return any(substring in string for string in lst)


def get_elements_by_substring(lst: List[str], substr: str) \
        -> List[str]:
    """
    Retrieves all elements in a list that contain the specified substring.

    Parameters
    ----------
    lst : List[str]
        The list of strings to search through.

    substr : str
        The substring to search for within each string in the list.

    Returns
    -------
    List[str]
        A list of strings that contain the specified substring.

    Examples
    --------

    .. code-block:: python

        >>> get_elements_by_substring(["apple", "banana", "grape", "pineapple"],
        ...     "apple")
        ['apple', 'pineapple']

        >>> get_elements_by_substring(["car", "bike", "truck"], "plane")
        []

    """

    return [el for el in lst if substr in el]


def remove_elements_from_list(lst: List[Any], elements_to_remove: List[Any]) \
        -> List[Any]:
    """
    Removes specified elements from a list.

    Parameters
    ----------
    lst : List[Any]
       The original list of elements.

    elements_to_remove : List[Any]
       The list of elements to be removed from the original list.

    Returns
    -------
    List[Any]
       A new list with the specified elements removed.

    Examples
    --------

    .. code-block:: python

        >>> remove_elements_from_list([1, 2, 3, 4], [2, 4])
        [1, 3]

        >>> remove_elements_from_list(["a", "b", "c"], ["b"])
        ['a', 'c']

    """

    return [el for el in lst if el not in elements_to_remove]


def remove_tuples_from_list_of_tuples(
        tuples: List[Tuple[str, ...]],
        tuples_to_remove: List[Tuple[str, ...]]
) -> List[Tuple[str, ...]]:
    """
    Removes specified tuples from a list of tuples.

    Parameters
    ----------
    tuples : List[Tuple[str, ...]]
        The original list of tuples.

    tuples_to_remove : List[Tuple[str, ...]]
        The list of tuples to remove from the original list of tuples.

    Returns
    -------
    List[Tuple[str, ...]]
        A new list of tuples with the specified tuples removed.

    Examples
    --------

    .. code-block:: python

        >>> remove_tuples_from_list_of_tuples(
        ...     [("a", "b"), ("c", "d")], [("c", "d")]
        ... )
        [('a', 'b')]

        >>> remove_tuples_from_list_of_tuples(
        ...     [("apple", "banana"), ("pear", "peach")], [("pear", "peach")]
        ... )
        [('apple', 'banana')]

    """

    return list(set(tuples) - set(tuples_to_remove))


def permute_elements(lst: List[Any]) \
        -> List[Tuple[Any, ...]]:
    """
    Returns all permutations of the elements in the list.

    Parameters
    ----------
    lst : List[Any]
        A list of elements

    Returns
    -------
        A list of all permuted versions of the original list.

    """

    return list(itertools.permutations(lst))


def permute_and_join(*lists: List[Any]) \
        -> List[Tuple[Any, ...]]:
    """
    Permute each list and join the results for any number of lists

    Usage
    -----
    >>> lst_1 = [1, 2, 3]
    >>> lst_2 = ["a", "b", "c"]

    >>> result = permute_and_join(lst_1, lst_2)
    [
        (1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2),
        (3, 2, 1), ('a', 'b', 'c'), ('a', 'c', 'b'),
        ('b', 'a', 'c'), ('b', 'c', 'a'), ('c', 'a', 'b'),
        ('c', 'b', 'a')
    ]

    """

    permuted_lists = [permute_elements(lst) for lst in lists]

    # Flatten the lists into one
    return list(itertools.chain.from_iterable(permuted_lists))


def find_list_of_dicts_entries_with_same_values_for_inner_key(
        data: List[Dict[Any, Any]],
        key: Any,
        value: Any
) -> List[int]:
    """
    Find the indices of all dictionaries in a list where the value of a given
    key matches a specified value.

    Parameters
    ----------
    data : List[Dict[Any, Any]]
        The list of dictionaries to search through.

    key : Any
        The key to check in each dictionary.

    value :Any
        The value to match for the specified key.

    Returns
    -------
    List[int]
        A list of indices of dictionaries that match the condition.

    """

    return [index + 1 for index, entry in enumerate(data) if entry.get(key) ==
            value]


def to_strings(lst: List[Any]) \
        -> List[str]:
    """
    Converts a list of elements of any type into a list of strings.

    This function takes any list of elements and converts each element
    to its string representation using the `str()` function.

    Parameters
    ----------
    lst : List[Any]
        A list of elements of any type to be converted into a list of strings.

    Returns
    -------
    List[str]
        A list containing the string representations of the elements
        in the input list.

    """

    return [str(el) for el in lst]


def to_dict_with_str_keys(lst: [List[Any]], start_key: int = 0) \
        -> Dict[str, Any]:
    """
    Converts a list of elements into a dictionary with string keys.

    Converts a list of elements into a dictionary with string keys derived from
    the integer indices of the original list.


    Parameters
    ----------
    lst : [List[Any]]
        A list of elements to be converted into a dictionary with string keys.

    start_key : int
        The starting integer key to use for the dictionary keys. Defaults to 0.

    Returns
    -------
    Dict[str, Any]
        A dictionary with string keys derived from the integer indices of the
        original list.

    """

    return {str(start_key + index): item for index, item in enumerate(lst)}
