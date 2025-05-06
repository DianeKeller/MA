"""
object_checking_decorators.py
-----------------------------
Version 1.0, updated on 2024-12-17

This module contains decorators for ensuring the 'data' property is set in
the class where the decorator is used.

"""

import inspect
from functools import wraps
from typing import Any, Tuple, Dict, Callable

from logger import Logger
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty

# Error message
MSG: str = 'The data is empty!'


def requires_data(operation: Callable):
    """
    This decorator makes sure the data property of the class is set when
    executing a given operation.

    The decorator wraps the given operation and raises a ValueError if the data
    is empty.

    Returns
    -------
    A decorator that can be applied to a method to ensure the 'data'
    property is set.

    Raises
    ------
    CriticalException
        If the 'data' property is not set or empty

    """

    @wraps(operation)
    def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        if is_none_or_empty(self.data):
            raise CriticalException(
                Logger(
                    f"{inspect.currentframe().f_code.co_name}"
                ).get_logger(),
                '%s Cannot execute the operation.' % MSG
            )

        return operation(self, *args, **kwargs)

    return wrapper


def info_requires_data(default_value: Any = None):
    """
    Checks if self.data is set before proceeding.

    If self.data is empty or None, logs an informational message and returns a
    default value.

    Parameters
    ----------
    default_value : any
        The value to return if self.data is found to be empty or None.

    Examples
    --------

    .. code-block:: python

        class DataHandler:
            def __init__(self, data):
                self.data = data

            def log(self, message, level):
                print(f"{level.upper()}: {message}")

            @info_requires_data()
            def process_data(self, default_value=None):
                # Assuming some processing logic here
                return "Data processed successfully!"

            @info_requires_data()
            def _get_n_rows(self, default_value=0) -> int:
                return self.n_rows

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
            if is_none_or_empty(self.data):
                msg = '%s Returning default value.' % MSG
                self.log(msg, 'info')

                return default_value

            return operation(self, *args, **kwargs)

        return wrapper

    return decorator
