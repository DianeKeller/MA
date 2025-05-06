"""
execution_time_decorator.py
"""
import inspect
from functools import wraps
from time import time
from typing import Callable, TypeVar, Any

from src.logging_mixin import LoggingMixin
from src.utils.time_utils import time_in_hours_minutes_and_seconds

T = TypeVar('T', bound=Callable[..., Any])


def execution_time(operation: T) \
        -> T:
    """
    A decorator for calculating the execution time of a function.

    The decorator wraps the given operation and logs the execution time.

    """

    @wraps(operation)
    def wrapper(*args, **kwargs) \
            -> Any:
        # Initialize the log function
        log = None

        instance_or_class = None

        # Ensure the logger is usable with class methods as well as functions
        # and static methods.

        if args:
            # Get the 'self' or 'cls' from args, which is the first argument
            # for methods.
            instance_or_class = args[0]

        # Check if this is being called on an instance or class that has the
        # _log method
        if hasattr(instance_or_class, '_log'):
            log = instance_or_class.log

        # This handles the case for classmethods where instance_or_class is
        # actually 'cls'
        elif hasattr(instance_or_class.__class__, '_log'):
            log = instance_or_class.__class__.log

        # Fallback logger if _log is not available: Default to using the
        # mixin's logger
        if log is None:
            log = LoggingMixin().log

        start = time()
        result = operation(*args, **kwargs)
        end = time()
        duration = end - start
        duration_str = time_in_hours_minutes_and_seconds(duration)

        # Determine if operation is bound to a class
        if inspect.ismethod(operation):
            class_name = (
                args[0].__class__.__name__
                if args
                else operation.__module__
            )
        else:
            class_name = operation.__module__

        msg = '%s.%s took %s.' % (class_name, operation.__name__, duration_str)
        log(msg, 'info')

        return result

    return wrapper
