"""
trace_decorators.py
"""

import inspect
from functools import wraps
from typing import Callable


def trace_method_calls(method: Callable):
    """
    Traces the calls to the decorated instance method.

    Parameters
    ----------
    method : Callable

    Returns
    -------

    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):

        # Get the name of the method being called
        method_name = method.__name__

        # Get the caller method name
        frame = inspect.currentframe().f_back
        caller_name = frame.f_code.co_name

        class_name = self.__class__.__name__

        # Log the information
        msg = (
            f"Method '{method_name}' called from '{caller_name}'"
            f" in class '{class_name}' with args: {args} and kwargs: {kwargs}"
        )

        # Ensure that the output works with and without a _log method:
        # Fallback to printing if no _log method is available.
        if hasattr(self, '_log'):
            self._log(msg, 'info')
        else:
            print(msg)

        # Call the original method
        return method(self, *args, **kwargs)

    return wrapper
