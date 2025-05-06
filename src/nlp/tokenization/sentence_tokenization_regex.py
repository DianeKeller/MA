"""
sentence_tokenization_regex.py
------------------------------
Version 1.0, updated on 2024-09-17

This module provides regular expressions that can be used for different
sentence tokenization strategies.

Functions
---------
regex_with_colons() -> Pattern[str]:
    Regex for identifying sentences by end-of-sentence characters or colons.

"""

import re
from re import Pattern


def regex_with_colons() \
        -> Pattern[str]:
    """
    Regex for identifying sentences by end-of-sentence characters or colons.

    This regex considers colons as end-of-sentence characters.

    Returns
    -------
    Pattern[str]
        Compiled regex pattern for sentence tokenization.

    Notes
    -----
    Explanation of the regex per line:

    [1] Set x flag to allow comments at the end of the lines.
    [2] At least one character that is not an end-of-sentence character.
    [3] Optionally followed by one or more dots without whitespace.
    [4] [2]-[3] must be found at least once.
    [5] Followed by any number of any end-of-sentence characters, followed
        optionally by any number of white spaces, or the end of the string.

    """
    regex = r'''(?x)       # [1]
        (
            [^.:!?]+              # [2] 
            ([.]+[\S])*           # [3]
        )+                        # [4] 
        ([.:!?]+\s*|\Z)           # [5]
    '''
    return re.compile(regex)
