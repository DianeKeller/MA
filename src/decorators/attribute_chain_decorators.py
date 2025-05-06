"""
attribute_chain_decorators.py
-----------------------------
Version 1.0, updated on 2024-12-04

"""

import inspect
from functools import wraps
from typing import Callable, Any, Tuple, Dict

from logger import Logger
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)


def _check_attribute_chain(
        obj: object,
        attribute_chain: str,
        error_prefix: str
) -> bool:
    """
    Checks if the given object has a valid attribute chain.

    Parameters
    ----------
    obj : object
        The object to check the attribute chain on.

    attribute_chain : str
        The chain of attributes to check.

    error_prefix : str
        The prefix for the error message.

    logger : Logger
            A logger instance.

    Returns
    -------
    bool
        True if the attribute chain is valid.

    Raises
    ------
    CriticalException
        If the attribute chain is invalid.

    Notes
    -----
    This function never returns False as it raises an exception if the check
    of the attribute chain fails.

    Examples
    --------

    .. code-block:: python

        >>> class C:
        ...     def __init__(self):
        ...         self.c = 1

        >>> class B:
        ...     def __init__(self):
        ...         self.b = C()

        >>> class MyObject:
        ...     def __init__(self):
        ...         self.a = B()

        >>> obj = MyObject()

        # Checking a valid attribute chain:
        >>> ok = _check_attribute_chain(
        ...     obj,
        ...     'a.b.c',
        ...     'Attribute chain is not valid'
        ... )
        True

        # Checking an invalid attribute chain:
        >>> ok = _check_attribute_chain(
        ...     obj,
        ...     'a.b.x',
        ...     'Attribute chain is not valid'
        ... )
        Traceback (most recent call last):
          ...
        ValueError: Attribute chain is not valid. Attribute 'x' of chain 'a.b.x'
        is missing or None.

    """

    logger = Logger(f"{inspect.currentframe().f_code.co_name}").get_logger()

    attributes = attribute_chain.split('.')
    current_obj = obj

    for attr in attributes:
        if (
                not hasattr(current_obj, attr) or
                getattr(current_obj, attr) is None
        ):
            raise CriticalException(
                logger=logger,
                msg=(
                    f"{error_prefix} Attribute '{attr}' of chain "
                    f"'{attribute_chain}' is missing or None."
                )
            )

        current_obj = getattr(current_obj, attr)

    return True


def _generic_attribute_chain_not_none(
        what: str,
        attribute_chain: str,
        target: str = 'output'
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator factory to create decorators that ensure the presence and
    non-None value of an attribute chain either on the input object or the
    output object of a method.

    Parameters
    ----------
    what : str
        Description of the object or value being checked, formatted dynamically
        using the parameters of the method it decorates.

    attribute_chain : str
        The attribute chain to validate, specified as a dot-separated string.

    target : str
        Specifies whether the 'input' or 'output' object is being validated.
        Default is 'output'.

    Returns
    -------
    Callable[[Callable[..., Any]], Callable[..., Any]]
        A decorator that applies the attribute chain validation to the method's
        input or output.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
            if target == 'input':
                # Assuming the input object is always the first positional
                # argument
                obj = args[0] if args else None
            else:
                obj = operation(self, *args, **kwargs)

            formatted_what = what.format(*args, **kwargs)
            error_prefix = f"{formatted_what}"

            _check_attribute_chain(obj, attribute_chain, error_prefix)

            if target != 'input':
                return obj

            return operation(self, *args, **kwargs)

        return wrapper

    return decorator


# Usage for checking output attributes
def output_attribute_chain_not_none(what: str, attribute_chain: str) \
        -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Checks the given attribute_chain on the output object.

    Parameters
    ----------
    what : str
        The format string to be used in the error message.

    attribute_chain : str
        The attribute_chain to be validated on the output object.

    Returns
    -------
    Callable[[Callable[..., Any]], Callable[..., Any]]
        A decorator that validates the attribute chain on the output object.

    """

    return _generic_attribute_chain_not_none(
        what,
        attribute_chain,
        target='output'
    )


def input_attribute_chain_not_none(what: str, attribute_chain: str) \
        -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Checks the given attribute_chain on the input object.

    Parameters
    ----------
    what : str
        The format string to be used in the error message.

    attribute_chain : str
        The attribute chain to be validated on the input object.

    Returns
    -------
    Callable[[Callable[..., Any]], Callable[..., Any]]
        A decorator that validates the attribute chain on the input object.

    """

    return _generic_attribute_chain_not_none(
        what,
        attribute_chain,
        target='input'
    )


def self_attribute_chain_not_none(attribute_chain: str) \
        -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Ensures attributes in self before method execution.

    Ensures that attributes on the `self` object of a method contain a
    valid and non-None attribute chain before method execution.

    Parameters
    ----------
    attribute_chain : str
       The attribute chain to be validated on the `self` object.

    Returns
    -------
    Callable[[Callable[..., Any]], Callable[..., Any]]
        A decorator that checks the attribute chain on the `self` object
        before executing the method.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
            _check_attribute_chain(
                self,
                attribute_chain,
                f"Required attribute '{attribute_chain}' "
                f"is missing or None. Cannot proceed with "
                f"{operation.__name__}."
            )
            return operation(self, *args, **kwargs)

        return wrapper

    return decorator
