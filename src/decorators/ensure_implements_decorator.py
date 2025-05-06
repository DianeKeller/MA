"""
ensure_implements_decorator.py
------------------------------
Version 1.0, updated on 2024-12-17

This module contains the ensure_implements decorator used to ensure that the
class where the decorator is used conforms to a specified protocol.

"""

from functools import wraps
from typing import Type, Tuple, Any, Dict, Callable


def ensure_implements(protocol: Type):

    """
    Decorator that ensures a class implements a specific protocol.

    This decorator checks if the class instance where the decorated method
    is used implements a specified protocol (interface). If the class does
    not implement the protocol, a 'TypeError' is raised.

    Parameters
    ----------
    protocol : Type
        The protocol or interface that the decorated method's class must
        implement.

    Returns
    -------
    Callable
        A decorator that validates the protocol implementation.

    Raises
    ------
    TypeError
        If the class instance invoking the method does not implement the
        specified protocol.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
            if not isinstance(self, protocol):
                raise TypeError("The %s protocol must be implemented." %
                                protocol.__name__)
            return operation(self, *args, **kwargs)

        return wrapper

    return decorator
