"""
object_checking_decorators.py
-----------------------------
Version 1.0, updated on 2024-12-04

"""

import inspect
from functools import wraps
from typing import Callable, TypeVar, cast, Tuple, Any, Dict

from logger import Logger
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty

T = TypeVar('T', bound=Callable)


def requires_file(operation: T) \
        -> T:
    """
    This decorator ensures a file is set when executing a given
    operation.

    The decorator wraps the given operation and raises a ValueError if the
    file is not set.

    """

    @wraps(operation)
    def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        if not self.file:
            raise CriticalException(
                Logger(
                    f"{inspect.currentframe().f_code.co_name}"
                ).get_logger(),
                'The file is not set! Cannot proceed without a file.'
            )

        return operation(self, *args, **kwargs)

    # Ensure Mypy can recognize the type of the wrapper by casting it to T.
    return cast(T, wrapper)


def requires_data(operation: T) \
        -> T:
    """
    This decorator makes sure data exist when executing a given
    operation.

    The decorator wraps the given operation and emits a warning if the data is
    empty.

    """

    @wraps(operation)
    def wrapper(self, data, *args, **kwargs):
        if is_none_or_empty(data):
            msg = 'The data is empty! Nothing to save.'
            self.log(msg, 'warning')
            return T()
        return operation(self, data, *args, **kwargs)

    # Ensure Mypy can recognize the type of the wrapper by casting it to T.
    return cast(T, wrapper)
