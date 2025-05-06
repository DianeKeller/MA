"""
print_utils.py
--------------
Version 1.0, updated on 2025-05-01

This module provides formatting and printing utilities. It contains two
singledispatch mechanisms, 'examples' and 'restrict_length' that mainly
serve to format outputs, and various printing functions providing formatted
output elements like white lines, separators, headers, and the output in a
box with title header and body.

Functions
---------
examples(my_iterable: Iterable[Any]) -> Iterable[Any]:
    Generic function to extract a couple of examples from the given iterable.

restrict_length(_my_iterable: Iterable[Any], _max_length: int = 3) -> None:
    Generic function to restrict the length of the given iterable to the
    specified maximum length.

print_box_start() -> None:
    Prints a white line and a separator as the beginning of a box.

print_double_line() -> None:
    Prints a line of equal signs as a text separator.

print_header(title: str) -> None:
    Formats and prints a header with the specified title.

print_in_box(title: str = '', body: Any = '', subtitle: str = '') -> None:
    Prints a title, subtitle and body in a box in the console.

print_sep() -> None:
    Prints a line of hyphens as a text separator.

print_subsep() -> None:
    Prints a line of hyphens separated by blanks as a text separator.

print_wline() -> None:
    Prints an empty line as a text separator.

"""

import re
from functools import singledispatch
from pprint import pprint
from typing import Dict, List, Any

from constants import MAX_ITEMS, MAX_STRING_LENGTH
from src.utils.data_utils import is_none_or_empty
from type_aliases import ExamplesType, DictKeyType

WHITE_SPACE = ' '
DOUBLE_LINE = '========================================================\n'
SEPARATOR = '--------------------------------------------------------\n'
SUBSEPARATOR = '- - - - - - - - - - - - - - - - - - - - - - - - - - - - \n'
WHITE_LINE = '\n'


def print_sep() \
        -> None:
    """
    Prints a line of hyphens as a text separator.
    """

    print(SEPARATOR)


def print_double_line() \
        -> None:
    """
    Prints a line of equal signs as a text separator.
    """

    print(DOUBLE_LINE)


def print_subsep() \
        -> None:
    """
    Prints a line of hyphens separated by blanks as a text separator.
    """

    print(SUBSEPARATOR)


def print_wline() \
        -> None:
    """
    Prints an empty line as a text separator.
    """

    print(WHITE_LINE)


def print_header(title: str) \
        -> None:
    """
    Formats and prints a header with the specified title.

    The title is preceded by box start lines, which are defined in the
    print_box_start function, and followed by a line of equal signs.

    Parameters
    ----------
    title : str
        The title of the header.

    """

    print_box_start()
    print(title)
    print_double_line()


def print_box_start() \
        -> None:
    """
    Prints a white line and a separator as the beginning of a box.

    For the concrete form of the separator string, see the print_sep()
    function and the SEPARATOR constant.

    """

    print_wline()
    print_sep()


def print_in_box(title: str = '', body: Any = '', subtitle: str = '') \
        -> None:
    """
    Prints a title, subtitle and body in a box in the console.

    Parameters
    ----------
    title : str
        The title of the box, printed in its header. If the title is an
        empty string, the header of the box will be omitted.

    body : Any
        The body of the box. If it has another data type than a string,
        it will be pretty-printed so that the content of, e.g., a list or
        a dictionary is displayed as a multi-line list. Defaults to an empty
        string.

    subtitle : str
        An optional subtitle, which will be displayed in a separate line at
        the beginning of the body section of the box. Defaults to an empty
        string.

    """

    if title:
        print_header(title)
    else:
        print_box_start()

    if not is_none_or_empty(subtitle):
        print(f"{subtitle}{WHITE_LINE}")

    if isinstance(body, str):
        print(body)
    else:
        pprint(body)
    print_sep()


# region --- Restrict_length Singledispatch Mechanisme

@singledispatch
def restrict_length(
        _my_iterable: ExamplesType,
        _max_length: int = MAX_ITEMS
) -> None:
    """
    Generic function to restrict the length of the given iterable to the
    specified maximum length. This function serves as the entry point for the
    singledispatch mechanism, which, based on the concrete type of the
    iterable, dynamically selects which of the following implementations
    needs to be executed.

    By default, this base function raises a NotImplementedError indicating
    that the implementation for the specific iterable type is missing and
    should be added and registered.

    Parameters
    ----------
    _my_iterable: ExamplesType
        The iterable whose length needs to be restricted.

    _max_length: int
        The maximum length of the iterable.

    Raises
    ------
    NotImplementedError
        If the implementation for the specific iterable type is missing
        and should be added and registered.

    Examples
    --------

    .. code-block:: python

        >>> restrict_length([1, 2, 3, 4, 5], 3)
        [1, 2, 3]

    """
    msg = ("Found no implementation for the provided iterable type %s."
           % type(_my_iterable))
    raise NotImplementedError(msg)


@restrict_length.register(list)
def _restrict_list_length(
        my_list: List,
        max_items: int = MAX_ITEMS
) -> List[Any]:
    max_items = min(len(my_list), max_items)
    return my_list[:max_items]


@restrict_length.register(dict)
def _restrict_dict_length(
        my_dict: Dict,
        max_items: int = MAX_ITEMS
) -> Dict[DictKeyType, Any]:
    results = {}
    max_items = min(len(my_dict), max_items)
    for i in range(0, max_items):
        results[list(my_dict.keys())[i]] = list(my_dict.values())[i]
    return results


@restrict_length.register(str)
def _restrict_string_length(
        string: str,
        max_length: int = MAX_STRING_LENGTH
) -> str:
    """
    Formats a string by splitting it into lines of the specified maximum
    length.

    Inserts a line break each time a line would exceed the maximum length if
    continued.

    Attempts to break at whitespace, hyphen or underscore to avoid breaking
    a line in the middle of words.

    Parameters
    ----------
    string : str
       The input string to be formatted.

    max_length : int, optional
       The maximum allowed line length of the output string (default is
       MAX_STRING_LENGTH).

    Returns
    -------
    str
       The formatted string.

    Examples
    --------

    .. code-block:: python

        >>> _restrict_string_length("hello world", 7)
        'hello \nworld'

        >>> _restrict_string_length("hello-world", 10)
        'hello-\nworld'

        >>> _restrict_string_length("hello_world", 5)
        'hello_\nworld'

    """

    if len(string) <= max_length:
        return string

    new_string = ''
    regex = r'[\s\-_]+'

    while string:
        # If the string is shorter than max_length, append it directly
        if len(string) <= max_length:
            new_string += string
            break

        # Find the last whitespace or break character before max_length
        break_match = list(re.finditer(regex, string[:max_length]))
        if break_match:
            # If a break character is found, break at the last one
            last_break = break_match[-1].end()
            new_string += string[:last_break] + '\n'
            string = string[last_break:]
        else:
            # If no break character is found, break at max_length
            # and include trailing whitespaces if any
            slice_end = max_length
            while slice_end < len(string) and string[slice_end].isspace():
                slice_end += 1  # Extend slice to include trailing whitespaces
            new_string += string[:slice_end] + '\n'
            string = string[slice_end:]

    return new_string


# endregion --- Restrict_length Singledispatch Mechanisme

# region --- Examples Singledispatch Mechanism

@singledispatch
def examples(my_iterable: ExamplesType) \
        -> ExamplesType:
    """
    Generic function to extract a couple of examples from the given
    iterable. This function
    serves as the entry point for the
    singledispatch mechanism, which, based on the concrete type of the
    iterable, dynamically selects which of the following implementations
    needs to be executed.

    By default, this base function raises a NotImplementedError indicating
    that the implementation for the specific iterable type is missing and
    should be added and registered.

    Parameters
    ----------
    my_iterable: ExamplesType
        The iterable from which the examples will be taken.

    Returns
    -------
    ExamplesType
        A new iterable containing the examples.

    Raises
    ------
    NotImplementedError
        If the implementation for the specific iterable type is missing
        and should be added and registered.

    Notes
    -----
    - The number of examples to extract from the iterable is fixed by the
      global MAX_ITEMS constant, which is specified in the NUM category section
      in the settings file.

    - While the return types of the different implementations are subtypes of
      Iterable, the type checker does not seem to understand this. Therefore,
      type checking is disabled for the return types.

    """

    msg = ("Found no implementation for the provided iterable type %s."
           % type(my_iterable))
    if msg:
        raise NotImplementedError(msg)

    return my_iterable


@examples.register(dict)
def _dict_examples(my_dict: Dict) \
        -> Dict[DictKeyType, Any]:
    """
    Extracts a couple of examples from the given dictionary.

    Parameters
    ----------
    my_dict: Dict
        The dictionary from which the examples will be taken.

    Returns
    -------
    Dict[DictKeyType, Any]
        A new dictionary containing the examples.

    Notes
    -----
    - The number of examples to extract from the dictionary is fixed by the
      global MAX_ITEMS constant, which is specified in the NUM category section
      in the settings file.

    - While dict is a subtype of Iterable, the type checker does not seem to
      understand this. Therefore, type checking is disabled for the return
      type.

    """

    return restrict_length(my_dict, MAX_ITEMS)  # type: ignore


@examples.register(list)
def _list_examples(my_list: List[Any]) \
        -> List[Any]:
    """
    Extracts a couple of examples from the given list.

    Parameters
    ----------
    my_list: List
        The list from which the examples will be taken.

    Returns
    -------
    List[Any]
        A new list containing the examples.

    Notes
    -----
    - The number of examples to extract from the list is fixed by the
      global MAX_ITEMS constant, which is specified in the NUM category section
      in the settings file.

    - While List is a subtype of Iterable, the type checker does not seem to
      understand this. Therefore, type checking is disabled for the return
      type.

    """

    return restrict_length(my_list, MAX_ITEMS)  # type: ignore

# endregion --- Examples Singledispatch Mechanism
