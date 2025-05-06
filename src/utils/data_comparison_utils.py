"""
data_comparison_utils.py
------------------------
Version 1.0, updated on 2024-12-04

This module contains a singledispatch mechanism to check whether two data
structures are identical.

Functions
---------
are_equal(data: T, other: T) -> bool:
    Compares two data structures of the same type to decide whether their
    contents are identical.

"""

from __future__ import annotations

from functools import singledispatch
from typing import TypeVar

from datasets import DatasetDict
from pandas import DataFrame, Series
from pandas._testing import assert_frame_equal, assert_series_equal

from src.data_structures.my_ordered_dict import MyOrderedDict
from src.logging_mixin import LoggingMixin

T = TypeVar('T')

log = LoggingMixin().log


@singledispatch
def are_equal(data: T, other: T) \
        -> bool:
    """
    Generic function to check if two objects are equal.

    This singledispatch mechanism provides custom comparison functionality
    for data types that do not allow for a simple equality check with the
    '==' operator.

    Parameters
    ----------
    data : T
        The data to compare to other data

    other : T
        Other data to compare with the data

    Returns
    -------
    bool
        'True' if the data and the other data are equal. 'False' otherwise.

    Raises
    ------
    NotImplementedError
        If the data type of the provided parameters is not covered by one of
        the registered functions of this singledispatch mechanism.

    Notes
    -----
    This function defines the singledispatch mechanism that delegates the
    equality checks to the registered specialized function that covers the
    the respective type of the input values. If there is no special function
    for the data type of the input values, this function serves as a
    "catch-all" function, returning a NotImplementedError.

    """

    msg = "No equality check implemented for type %s" % type(data)

    # Dummy conditional so that a dummy return value can be defined to satisfy
    # code linters that expect a return value.
    if msg:
        log(msg, "error")
        raise NotImplementedError(msg)

    return False


@are_equal.register
def _(data: MyOrderedDict, other: MyOrderedDict) \
        -> bool:
    """
    Check whether two MyOrderedDicts are equal.

    Check whether OrderedDicts wrapped in the MyOrderedDicts contain the
    same elementes and whether they are sorted in the same order.

    Parameters
    ----------
    data : MyOrderedDict
        The first MyOrderedDict to be compared.

    other : MyOrderedDict
        The second MyOrderedDict to be comparedl.

    Returns
    -------
    bool
        True if the MyOrderedDicts are equal, False otherwise.

    """
    if data.my_dict == other.my_dict:
        if data.first == other.first and \
                data.last == other.last:
            return True
        return False
    return False


@are_equal.register
def _(data: DatasetDict, other: DatasetDict) \
        -> bool:
    """
    Check whether two DatasetDicts are equal.

    Check whether two DatasetDicts contain the same number of subsets and
    whether these are identical.

    Parameters
    ----------
    data : DatasetDict
        The first DatasetDict to be compared.

    other : DatasetDict
        The second DatasetDict to be comparedl.

    Returns
    -------
    bool
        True if the DatasetDict objects are equal, False otherwise.

    Examples
    --------

    .. code-block:: python

        >>> ex_data = DatasetDict({
        ...     "train": [1, 2, 3],
        ...     "test": [4, 5, 6]
        ... })
        >>> ex_other = DatasetDict({
        ...     "train": [1, 2, 3],
        ...     "test": [4, 5, 6]
        ... })
        >>> are_equal(ex_data, ex_other)
        True

        >>> ex_data = DatasetDict({
        ...     "train": [1, 2, 3],
        ...     "test": [4, 5, 6]
        ... })
        >>> ex_other = DatasetDict({
        ...     "train": [1, 2, 3],
        ...     "test": [4, 5, 7]
        ... })
        >>> are_equal(ex_data, ex_other)
        False

    """

    if len(data) != len(other):
        return False

    if data.keys() != other.keys():
        return False

    # Deep check of all elements:
    for key in data.keys():

        # Convert datasets to a dictionary of tuples for comparison.
        data1 = data[key].to_dict()
        other1 = other[key].to_dict()

        # An equality check of dictionaries compares all elements recursively,
        # including their types:
        if data1 != other1:
            print(f"Mismatch found in subset: {key}")
            return False

    return True


@are_equal.register
def _(data: DataFrame, other: DataFrame) \
        -> bool:
    """
    Check whether two DataFrames are equal.

    Check whether two DataFrames are identical.

    Parameters
    ----------
    data : DataFrame
        The first DataFrame to be compared.

    other : DataFrame
        The second DataFrame to be comparedl.

    Returns
    -------
    bool
        True if the DataFrames are equal, False otherwise.

    """

    # Basic equality check
    if not data.equals(other):
        msg = "DataFrames are not equal: %s vs. %s" % (data, other)
        log(msg, 'info')
        return False

    # More fine-grained check including data types
    try:
        assert_frame_equal(data, other)
        msg = "DataFrames are identical"
        log(msg, 'info')
        return True

    except AssertionError as err:
        msg = "DataFrames differ: %s vs. %s (%s)" % (data, other, err)
        log(msg, 'info')
        return False


@are_equal.register
def _(data: Series, other: Series) \
        -> bool:
    """
    Check whether two Series are equal.

    Check whether two Series are identical.

    Parameters
    ----------
    data : Series
        The first Series to be compared.

    other : DataFrame
        The second Series to be compared.

    Returns
    -------
    bool
        True if the Series are equal, False otherwise.

    """

    # Basic equality check
    if not data.equals(other):
        msg = "Series are not equal: %s vs. %s" % (data, other)
        log(msg, 'info')
        return False

    # More fine-grained check including data types
    try:
        assert_series_equal(data, other, check_names=False)
        msg = "Series are identical"
        log(msg, 'info')
        return True

    except AssertionError as err:
        msg = "Series differ: %s vs. %s (%s)" % (data, other, err)
        log(msg, 'info')
        return False
