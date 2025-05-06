"""
string_search_utils.py
----------------------
Version 1.0, validated on 2025-05-01

This module provides utilities for searching strings using regular expressions.
It contains functions to search for single or multiple matches with or
without verbosity, and to filter or analyze the matches found within a given
string.

Functions
---------
find_all_matches(string: str, regex: re.Pattern[str], name: str = '',
        verbose: bool = False)
        -> Tuple[List[Dict[str, Sequence[object]]], List[Sequence[object]]]:
    Searches for occurrences of the specified regex pattern.

"""

import re
from re import Pattern
from typing import Dict, List, Tuple, Sequence

from src.nlp.results.dict_list_result import DictListResult
from src.nlp.results.result import print_results
from src.nlp.results.string_result import StringResult


# region --- Public Functions

def find_all_matches(
        string: str,
        regex: Pattern[str],
        name: str = '',
        verbose: bool = False
) -> Tuple[List[Dict[str, Sequence[object]]], List[Sequence[object]]]:
    """
    Searches for occurrences of the specified regex pattern.

    Uses the _search function to find occurrences of the specified regex
    pattern within the given string and their positions.

    Offers the possibility to print the search result using the given name
    in the title of the output.

    Parameters
    ----------
    string : str
        The string to search within.

    regex : Pattern[str]
        The compiled regular expression pattern to search for.

    name : str, optional
        The name of the string, used for printing purposes. Defaults to a
        substring of the input.

    verbose : bool, optional
        Whether to print each match. Defaults to False.

    Returns
    -------
    Tuple[List[Dict[str, str]], List[str]]
        A tuple containing the match details and the matches themselves.

    Examples
    --------

    .. code-block:: python

        >>> text = "Collect all the words and their positions."
        >>> regex = re.compile(r'\\b\\w+\\b')
        >>> match_details, all_matches = find_all_matches(
        ...     text, regex, "ExampleText", True
        ... )
        >>> match_details[:1]
        [{'pos': (0, 7), 'match': 'Collect'}]
        >>> all_matches[:1]
        ['Collect']

    """

    # If the name is None, use the first 10 characters of the given string.
    if not name:
        name = string[:10] + '...' if len(string) > 10 else string

    results, matches = _search(string, regex)

    if verbose:
        title = f'Occurrences of "{regex}" found in {name}'
        descr = f'Found {str(len(results))} matches:'

        # Do not try to print results if there aren't any:
        if results:
            print_results(
                DictListResult(results),
                title,
                descr
            )
        else:
            print_results(StringResult(''), title, descr)
    return results, matches


# endregion --- Public Functions

# region --- Protected Functions

def _search(
        string: str,
        regex: Pattern[str]
) -> Tuple[List[Dict[str, Sequence[object]]], List[Sequence[object]]]:
    """
    Searches for occurrences of the regex pattern in the given string.

    Searches for occurrences of the specified regex pattern within the given
    string. Ensures that the matches are stripped of whitespace from both
    sides and returns them with their positions.

    Parameters
    ----------
    string : str
        The string to search within.

    regex : Pattern[str]
        The compiled regular expression pattern to search for.

    Returns
    -------
    Tuple[List[Dict[str, Sequence[object]]], List[Sequence[object]]]
        A tuple containing two elements:

        - A list of dictionaries, each representing a match.

          Each dictionary contains:
            - 'pos`: a tuple indicating the start and end positions of the
              match.
            - 'match': the matched string, stripped of whitespace, represented
              as a sequence of objects (typically a single string)

        - A list of sequences, where each sequence represents the matched
        strings, stripped of whitespace.

    Examples
    --------

    >>> import re
    >>> ex_text = "This is a very short but nice little text. It contains " \
    ... "but 2 sentences."
    >>> ex_pattern = re.compile(r'\\b\\w+\\b')  # Matches whole words
    >>> ex_matches_and_positions, ex_matches = _search(
    ...     ex_text, ex_pattern
    ... )
    >>> # Show the first 3 matches and their positions:
    >>> ex_matches_and_positions[:3]
    [{'pos': (0, 4), 'match': 'This'}, {'pos': (5, 7), 'match': 'is'},
    {'pos': (8, 9), 'match': 'a'}]
    >>> ex_matches[:3]  # Show the first 3 matches
    ['This', 'is', 'a']

    >>> ex_text = "Example text with some words."
    >>> ex_regex = re.compile(r'\\b\\w+\\b')  # Intended to match whole words
    >>> ex_matches_and_positions, ex_matches = _search(
    ...     ex_text, ex_regex
    ... )
    >>> ex_matches_and_positions[:1]
    [{'pos': (0, 7), 'match': 'Example'}]
    >>> ex_matches[:1]
    ['Example']

    """

    matches_and_positions = [
        {"pos": match.span(), "match": match.group().strip()}
        for match in re.finditer(regex, string)
    ]

    # Extracting just the matches into a separate list
    matches = [match["match"] for match in matches_and_positions]

    return matches_and_positions, matches

# endregion --- Protected Functions
