"""
type_utils.py
-------------
Version 1.0, validated on 2024-09-10

This method provides utility functions for type checks and, potentially,
conversions.

Functions
---------
is_int(data: Any) -> bool:
    Checks whether data is an integer.

"""

from typing import Any


def is_int(data: Any) \
        -> bool:
    """
    Checks whether data is an integer.

    Returns
    -------
    bool
        True if the data is an integer, False otherwise.

    """

    return isinstance(data, int)
