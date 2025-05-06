"""
time_decorators.py
------------------
Version 1.0, updated on 2024-08-12

This module contains decorators for measuring time durations.


"""
from typing import Callable

from src.utils.time_utils import begin, trace, end


def duration(operation: Callable):
    """
    Monitors the execution time of the decorated function or method.

    Parameters
    ----------
    operation : Callable
        The function or method to be decorated.

    Returns
    -------
    callable
        The decorated operation which logs its execution time.

    """

    def decorated_function(*data, **kwargs):

        try:
            start = begin(f'{data[0].__class__.__name__}: {data[0].name}')
        except AttributeError:
            start = begin(f'{data[0].__class__.__name__}')

        trace()

        result = operation(*data, **kwargs)
        end(start)
        return result

    return decorated_function
