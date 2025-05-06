"""
data_utils.py
-------------
Version 1.0, updated on 2024-09-10

This module provides functions that check whether a given data structure is
None or empty. It consists of the is_none_or_empty singledispatch mechanism
that dynamically decides how to check the given data depending on the type of
the data structure, and the is_empty function that uses the is_none_or_empty
mechanism to decide wether data that is not None is empty. The
singledispatch mechanism includes some protected utility functions that are
internally used by some of the singledispatch implementation functions.

Functions
---------
is_empty(data: Any) -> bool:
    Checks whether data is not None, but empty.

is_none_or_empty(data: Any) -> bool:
    Checks whether data is None or empty.

"""

from __future__ import annotations

from collections.abc import Mapping
from functools import singledispatch
from pathlib import Path
from typing import Any, TypeVar, cast

from pandas import DataFrame

from src.logging_mixin import LoggingMixin
from src.utils.late_imports import LateImports

T = TypeVar('T')

log = LoggingMixin().log


# region --- Is_none_or_empty

@singledispatch
def is_none_or_empty(data: Any) \
        -> bool:
    """
    Generic function to check if data of various types is None or empty.

    This function is the entry point for the singledispatch
    mechanism, which, based on the type of 'data', dynamically
    selects which of the following implementations to execute.

    Types that are not handled in the different singledispatch
    implementations are handled here. This is specifically the case for
    custom objects like MyDataFrame whose module import would cause circular
    imports across the project.

    Parameters
    ----------
    data : Any
        The data to check.

    Returns
    -------
    bool
        'True' if the data is None or empty. 'False' otherwise.

    Notes
    -----
    This singledispatch mechanism primarily checks the content of data
    structures. If other objects need to be checked for None or empty and are
    passed to this mechanism and are not None, they are checked with the
    'has_none_attributes' function for custom attributes that are not set.

    """
    if data is None:
        return True

    if hasattr(data, 'data'):
        return is_none_or_empty(data.data)

    my_data_frame_cls = LateImports.get_my_dataframe_class()

    if isinstance(data, my_data_frame_cls):
        return is_none_or_empty(cast(my_data_frame_cls, data).df)

    return _has_none_attributes(data)


def _has_none_attributes(obj: Any) \
        -> bool:
    """
    Checks if an object has any attributes set to None.

    Parameters
    ----------
    obj : Any
        The object to check.

    Returns
    -------
    bool
        'True' if the object has any None attributes. 'False' otherwise.

    Notes
    -----
    The function checks only those attributes that already exist and have
    already been calculated, avoiding lengthy computations of values which
    are not actually needed.

    """

    attributes = vars(obj)

    for attr in _get_custom_object_attributes(obj):
        if attributes.get(attr) is None:
            return True
    return False


def _get_custom_object_attributes(obj: Any) \
        -> list:
    """
    Gets all public custom attributes of an object.

    Gets all attributes that are not callable or start with an underscore,
    i.e. all public attributes that are no functions or methods.

    Parameters
    ----------
    obj : Any
        The object to get the attributes from.

    Returns
    -------
    list
        A list of all public custom attributes of the object.

    Notes
    -----
    The function accesses only those attributes that already exist and have
    already been calculated, avoiding lengthy computations of values which
    are not actually needed.


    """

    attrs = [attr for attr in vars(obj) if
             not callable(getattr(obj, attr)) and not attr.startswith("_")]
    return attrs


@is_none_or_empty.register
def _(data: list) \
        -> bool:
    """
    Implementation for data lists.

    Parameters
    ----------
    data : list
        Data list to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return len(data) == 0


@is_none_or_empty.register
def _(data: dict) \
        -> bool:
    """
    Implementation for data dictionaries.

    Parameters
    ----------
    data : dict
        Data dictionary to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return len(data) == 0


@is_none_or_empty.register
def _(data: str) \
        -> bool:
    """
    Implementation for data strings.

    Parameters
    ----------
    data : str
        Data string to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return len(data.strip()) == 0


@is_none_or_empty.register
def _(data: bytes) \
        -> bool:
    """
    Implementation for data bytes.

    Parameters
    ----------
    data : bytes
        Data bytes to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return len(data) == 0


@is_none_or_empty.register
def _(data: set) \
        -> bool:
    """
    Implementation for data sets.

    Parameters
    ----------
    data : set
        Data set to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """
    return len(data) == 0


@is_none_or_empty.register
def _(data: tuple) \
        -> bool:
    """
    Implementation for data tuples.

    Parameters
    ----------
    data : tuple
        Data tuple to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """
    return len(data) == 0


@is_none_or_empty.register
def _(data: Mapping) \
        -> bool:
    """
    Implementation for data Mappings.

    Parameters
    ----------
    data : Mapping
        Data Mappings to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return not bool(data)


@is_none_or_empty.register
def _(data: range) \
        -> bool:
    """
    Implementation for data ranges.

    Parameters
    ----------
    data : range
        Data range to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return len(list(data)) == 0


@is_none_or_empty.register
def _(data: int) \
        -> bool:
    """
    Implementation for integer values.

    Parameters
    ----------
    data : int
        Integer value to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return data == 0


@is_none_or_empty.register
def _(data: float) \
        -> bool:
    """
    Implementation for float values.

    Parameters
    ----------
    data : float
        Float value to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return data == 0


@is_none_or_empty.register
def _(data: DataFrame) \
        -> bool:
    """
    Implementation for DataFrames.

    Parameters
    ----------
    data : DataFrame
        The DataFrame to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return data.empty


@is_none_or_empty.register
def _(data: Path) \
        -> bool:
    """
    Implementation for paths.

    Parameters
    ----------
    data : Path
        The path to check.

    Returns
    -------
    See generic is_none_or_empty function.

    """

    return data is None


# endregion --- Is_none_or_empty

def is_empty(data: Any) \
        -> bool:
    """
    Checks whether data is not None, but empty.

    Parameters
    ----------
    data : Any
        The data to check.

    Returns
    -------
    bool
        True if the data is not Nune, but empty, False otherwise.

    """

    return data is not None and is_none_or_empty(data)
