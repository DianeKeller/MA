"""
data_check_decorators.py
------------------------
Version 1.0, updated on 2024-12-17

This module contains decorators for validating inputs, outputs, and class
properties. It includes mechanisms for logging and handling empty or None
values in method calls.

"""

import inspect
from functools import wraps
from typing import Any, Tuple, Dict, Callable

from logger import Logger
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty, is_empty

logger = Logger(__name__).get_logger()
log = LoggingMixin().log


# region --- Decorators

def input_not_none_or_empty(what: str):
    """
    Decorator to check if the first input parameter is empty.

    This decorator checks if the first input parameter of the decorated method
    is empty. If so, it logs a message and raises a ValueError.

    Parameters
    ----------
    what : str
        A format string describing the context of the input being checked,
        which can be formatted using '*args' and '**kwargs' from the method.

    Returns
    -------
    Callable
        A decorator that can be applied to a method to ensure the first
        parameter of the decorated method is set and not empty.

    Raises
    ------
    ValueError
        If the first parameter is empty.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
            input_value = _get_input_value(args)

            # Check if the input is None or empty
            if is_none_or_empty(input_value):
                msg = f'{what} not found or empty!'
                _log_msg(self, msg, 'error', args)

                raise ValueError(msg)

            # Call the original function with the original arguments
            return operation(self, *args, **kwargs)

        return wrapper

    return decorator


def parameters_not_empty(*param_names: str):
    """
    Decorator to ensure specified parameters are not None or empty.

    This decorator ensures specified parameters passed to the decorated
    function are not None or empty. If no parameter names are specified,
    all parameters are checked.

    Parameters
    ----------
    param_names : str
        Names of the parameters to check. If empty, all parameters (excluding
        'self' and 'cls') are checked.

    Returns
    -------
    Callable
        A decorator that can be applied to a method to ensure specified
        parameters are not None or empty.

    Raises
    ------
    CriticalException
        If a parameter is None or empty.
        
    Notes
    -----
    'Self' and 'cls' parameters of the decorated function are automatically
    excluded from the check, as they are always automatically set.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
            # Get the function's signature to map args and kwargs to parameter
            # names
            sig = inspect.signature(operation)
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()

            # Determine parameters to check
            params_to_check = param_names if param_names \
                else bound_args.arguments.keys()

            # Exclude 'self' and 'cls' from the parameters to check
            params_to_check = [
                param for param in params_to_check
                if param not in {'self', 'cls'}
            ]

            for param in params_to_check:
                if param in bound_args.arguments:
                    value = bound_args.arguments[param]
                    if is_none_or_empty(value):
                        raise CriticalException(
                            logger,
                            (
                                f"Parameter '{param}' cannot be "
                                f"None or empty!"
                            )
                        )

            # Call the original function
            return operation(*args, **kwargs)

        return wrapper

    return decorator


def requires_property(*attrs: str):
    """
    Decorator ensuring that the current object has the specified properties.

    Ensures the required properties of the calling object are set and
    not empty before the decorated method is executed. If the required
    properties are None or empty, a ValueError is raised and the decorated
    method is not executed.

    Parameters
    ----------
    attrs : str
        Names of one or more attributes/properties that must be set and not
        empty.

    Returns
    -------
    Callable
        A decorator that can be applied to a method to enforce the presence of
        the specified properties.

    Raises
    ------
    ValueError
        If any of the required properties is empty or not set.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[str, ...], **kwargs: Dict[str, Any]):
            for attr in attrs:
                value = getattr(self, attr, None)
                if is_none_or_empty(value):
                    msg = ("%s is not set. Cannot proceed." %
                           attr.capitalize())
                    _log_msg(self, msg, 'error', args)

                    raise ValueError(msg)
            return operation(self, *args, **kwargs)

        return wrapper

    return decorator


def info_requires_property(*attrs: str, default_value: Any = None):
    """
    Decorator ensuring that the current object has the specified properties.

    Checks whether the required properties of the calling object are set and
    not empty before the decorated method is executed. If a required
    property is None or empty, the decorator sets it to a default value and
    logs an informational message.

    Parameters
    ----------
    default_value : Any
        The value to set for any property that is found to be None or empty.

    attrs : str
        Names of one or more attributes/properties that are required for the
        execution of the decorated method.

    Returns
    -------
    Callable
        A decorator that can be applied to a method to enforce the presence of
        the specified properties, setting default values where necessary.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[str, ...], **kwargs: Dict[str, Any]):
            for attr in attrs:
                # Make the type of attr recognizable for type checkers
                attr: str

                value = getattr(self, attr, None)
                if is_none_or_empty(value):
                    msg = ("%s is not set. Returning default value." %
                           attr.capitalize())
                    _log_msg(self, msg, 'info', args)

                    return default_value

            return operation(self, *args, **kwargs)

        return wrapper

    return decorator


def output_not_none_or_empty(what: str):
    """
    Decorator that ensures that the output of a method is not None or empty.

    Decorator that checks if the output of a method is None or empty and
    raises an error if so.

    Parameters
    ----------
    what : str
        A format string used to describe the context of the operation in error
        messages.

    Returns
    -------
    Callable
        A decorator function that can be applied to methods to enforce that
        their output is neither None nor empty.

    Raises
    ------
    ValueError
        If the output is empty or not set.

    Notes
    -----
    This decorator rejects empty outputs like empty strings or empty
    lists as well as 'None' outputs. If empty outputs are acceptable, though,
    use the 'output_not_none' decorator instead.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[str, ...], **kwargs: Dict[str, Any]):
            return_value = operation(self, *args, **kwargs)
            if is_none_or_empty(return_value):
                params = _prepare_params(
                    self, operation, what, *args, **kwargs
                )

                msg = '%s not found or empty!' % params
                _log_msg(self, msg, 'error', args)

                raise ValueError(msg)

            return return_value

        return wrapper

    return decorator


def output_not_none(what: str):
    """
    Decorator that ensures that the output of a method is not None.

    Decorator that checks if the output of a method is None and raises an
    error if so.

    Parameters
    ----------
    what : str
        A format string used to describe the context of the operation in error
        messages.

    Returns
    -------
    Callable
        A decorator function that can be applied to methods to enforce that
        their output is not None.

    Notes
    -----
    This decorator does accept empty outputs like empty strings or empty
    lists. If you need to exclude those as well as 'None' outputs, use the
    'output_not_none_or_empty' decorator.

    Raises
    ------
    ValueError
        If the output is None.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[str, ...], **kwargs: Dict[str, Any]):
            return_value = operation(self, *args, **kwargs)
            if return_value is None:
                params = _prepare_params(
                    self, operation, what, *args, **kwargs
                )

                msg = '%s is None!' % params
                _log_msg(self, msg, 'error', args)

                raise ValueError(msg)

            return return_value

        return wrapper

    return decorator


def info_input_empty(what: str, on_empty: Callable = lambda *a, **kw: None):
    """
    Decorator that executes a function if the first input parameter is empty.

    Checks if the first input parameter of the decorated method is empty. If
    so, it logs a message and executes a specified function to potentially
    remedy the situation. The decorated method is then called with the new
    or existing input.

    Parameters
    ----------
    what : str
        A format string describing the context of the input being checked,
        which can be formatted using '\\*args' and '\\*\\*kwargs' from the
        method.

    on_empty : Callable
        A function to execute if the input is empty. It receives the 'self'
        instance and the empty value as parameters. It typically sets the
        required value of the first input parameter so that this is not
        empty anymore.

    Returns
    -------
    Callable
        A decorator that can be applied to methods to enforce the presence of a
        non-empty first argument.

    Usage
    -----

    .. code-block:: python

        class DataProcessor:
            def log_info(self, message):
               print(message)  # Logging to console or elsewhere

            @info_input_empty(
                'Processing input for user {user_id}',
                on_empty=lambda self, input: self.log_info("Input was empty!")
            )
            def process_data(self, data, user_id):
                # Method implementation...
                pass

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[str, ...], **kwargs: Dict[str, Any]):
            # Check the input value for emptiness
            input_value = _get_input_value(args)

            if is_empty(input_value):

                formatted_what = what.format(*args, **kwargs)
                msg = f"Value is empty! {formatted_what}"
                _log_msg(self, msg, 'info', args)

                new_input_value = on_empty(self, input_value)

                if not is_none_or_empty(new_input_value):
                    args = (new_input_value,) + args[1:]

            return operation(self, *args, **kwargs)

        return wrapper

    return decorator


def info_output_empty(what, on_empty=lambda *a, **kw: None):
    """
    Decorator that executes a function if the output is empty.

    Checks if the output  of the decorated method is empty. If so, it logs a
    message and executes a specified function.

    Parameters
    ----------
    what : str
        A format string describing the context of the input being checked,
        which can be formatted using '*args' and '**kwargs' from the method.

    on_empty : callable
        A function to execute if the output is empty. It receives the 'self'
        instance and the output value as parameters.

    Returns
    -------
    Callable
        A decorator that can be applied to methods to enforce the presence of a
        non-empty output.

    """

    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[str, ...], **kwargs: Dict[str, Any]):
            return_value = operation(self, *args, **kwargs)
            if is_empty(return_value):
                params = _prepare_params(
                    self, operation, what, *args, **kwargs
                )

                msg = 'Return value is empty! %s' % params
                _log_msg(self, msg, 'info', args)

                # Pass return_value to the on_empty function
                on_empty(self, return_value, *args, **kwargs)

            return return_value

        return wrapper

    return decorator


# endregion --- Decorators


# region --- Protected Functions
def _get_input_value(args: Tuple[Any, ...]) \
        -> Any | None:
    """
    Determines the input value depending on the operation type.

    Determines which argument represents the input type depending on the
    type of the decorated operation: Instance and class methods provide a
    "self" or "cls" parameter, while static or standalone methods do not.

    Parameters
    ----------
    args : Tuple[Any, ...]
        Positional arguments passed to the decorated method.

    Returns
    -------
    Any
        The input value, if found, None otherwise.

    """
    if len(args) > 1:
        # Supposing args[0] is the reference to the caller's class and args[1]
        # contains the input value
        return args[1]

    if len(args) == 1:
        return args[0]

    return None


def _log_msg(self, msg: str, level: str, *args: Tuple[Any, ...]) \
        -> None:
    """
    Logs a message using the provided logging mechanism.

    Depending on the context of the method call, this function determines
    whether to use the instance's logger or a default logger. It supports
    various logging levels such as 'info', 'warning', and 'error'.

    Parameters
    ----------
    self : Any
        The instance from which the log is triggered.

    msg : str
        The message to be logged.

    level : str
        The severity level of the log message ('info', 'warning', 'error').

    *args : Tuple[Any, ...]
        Additional arguments that may include an object with its own log
        method.

    Notes
    -----
    - If the first argument in `args` has a `log` method, it is used.
    - If `self` has a `log` method, it is used.
    - If neither condition is met, the module-level logger is used.

    """

    # Log or print the message
    if args and hasattr(args[0], 'log'):
        # If it's an instance method with logging
        args[0].log(msg, level)
    elif hasattr(self, 'log'):
        self.log(msg, level)
    else:
        # Static method
        log(msg, level)


def _prepare_params(
        self,
        operation: Callable,
        what: str,
        *args: Tuple[Any, ...],
        **kwargs: Dict[str, Any]
):
    """
    Helper function to format parameters for logging and error messages.

    This function prepares a dictionary (context) containing references to
    the 'self' instance, positional arguments (args), and keyword arguments
    (kwargs). It then uses this dictionary to replace placeholders in the
    'what' format string, returning the resulting formatted string.

    Parameters
    ----------
    self :
        The instance of the class that contains the method being decorated.

    operation : Callable
        The method being decorated.

    what : str
        A format string that describes the context of the operation being
        performed.

    args : Tuple[Any, ...]
        Positional arguments passed to the decorated method.

    kwargs : Dict[str, Any]
        Keyword arguments passed to the decorated method.

    Returns
    -------
    formatted_params : str
        A string where placeholders in 'what' have been replaced with the
        corresponding values from self, args, and kwargs.

    """

    # Prepare context with self and other params for string formatting
    context = {'self': self}
    # Add keyword arguments
    context.update(kwargs)

    # Retrieve the parameter names from the function signature
    param_names = operation.__code__.co_varnames[
                  :operation.__code__.co_argcount
                  ]

    for i, arg in enumerate(args):
        context[param_names[i + 1]] = arg

    # Use context for formatting
    formatted_params = what.format(**context)
    return formatted_params

# endregion --- Protected Functions
