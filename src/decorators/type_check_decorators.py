"""
type_check_decorators.py
------------------------
Version 1.0, updated on 2024-12-02

"""

import inspect
from functools import wraps
from typing import get_type_hints, Tuple, Any, Dict, Callable, get_origin, \
    Union, get_args, TypeVar, ForwardRef

from pandas import DataFrame

from src.data_structures.data_collection import DataCollection
from src.data_structures.my_data_frame import MyDataFrame

D = TypeVar('D', bound='DataCollection')

namespace = {
    'DataCollection': DataCollection,
    'MyDataFrame': MyDataFrame,
    'D': D,
    'DataFrame': DataFrame
}


# region --- Public Functions

def enforce_input_types(operation: Callable):
    """
    Ensures that the input parameters actually have the correct data types.

    Ensures that the input parameters actually have the type specified in
    the type hints.

    """

    @wraps(operation)
    def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        # Merge function arguments with the provided type hints
        all_args = _merge_args_with_hints(operation, (self,) + args, kwargs)
        _validate_args_types(operation, all_args)
        return operation(self, *args, **kwargs)

    return wrapper


def enforce_output_types(operation: Callable):
    """
    Enforces the correct type of the return value.

    Ensures that the return value actually has the type specified in the
    corresponding type hint.

    """

    @wraps(operation)
    def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        result = operation(self, *args, **kwargs)
        _validate_return_type(operation, result)
        return result

    return wrapper


def resolve_typevar_bound(type_var):
    """
    Resolves a TypeVar bound, handling forward references if necessary.

    """

    bound = type_var.__bound__

    if isinstance(bound, ForwardRef):
        # Define a dummy function with 'bound' as the parameter annotation
        def dummy_func(): pass

        # Resolve the forward reference using get_type_hints on the dummy
        # function
        bound = get_type_hints(dummy_func, globalns=namespace)['param']

    return bound


def log_error(message: str):
    """
    Logs an error message.
    """

    # Placeholder for logging functionality
    print(message)  # Replace with actual logging method


# region --- Public Functions

# region --- Protected Functions

def _get_operation_name(operation: Callable):
    """
    Retrieves the qualified name of an operation if available.

    Otherwise, returns its basic name.

    """

    return getattr(operation, "__qualname__", operation.__name__)


def _merge_args_with_hints(operation: Callable, args, kwargs):
    """
    Merges args and kwargs into a single dictionary with respect to the
    operation's signature.
    """

    signature = inspect.signature(operation)
    bound_args = signature.bind_partial(*args, **kwargs)
    bound_args.apply_defaults()
    return bound_args.arguments


def _validate_args_types(operation: Callable, all_args):
    """
    Validates types of all arguments based on the type hints.
    """

    hints = get_type_hints(operation, globalns=namespace, localns=namespace)
    for arg_name, arg_value in all_args.items():
        if arg_name in hints:
            expected_type = hints[arg_name]
            _check_arg_type(operation, arg_name, arg_value, expected_type)


def _validate_return_type(operation: Callable, result):
    """
    Validates the type of the return value based on the type hints.
    """

    hints = get_type_hints(operation, globalns=namespace, localns=namespace)
    return_type_hint = hints.get('return')

    if return_type_hint is not None:
        _check_return_type(operation, result, return_type_hint)


def _check_arg_type(operation: Callable, arg_name, arg_value, expected_type):
    """
    Checks if the argument matches the expected type, including generics.
    """

    # Handle special cases for None
    if _is_none_type(expected_type):
        _check_none_type(operation, arg_name, arg_value, expected_type)
        return

    # Handle Unions
    if _is_union_type(expected_type):
        _check_union_type(operation, arg_name, arg_value, expected_type)
        return

    # Handle generic types like List[int], Dict[str, str]
    if _is_generic_type(expected_type):
        _check_generic_type(operation, arg_name, arg_value, expected_type)
        return

    # Handle TypeVars with bounds
    if isinstance(expected_type, TypeVar):
        _check_typevar_bound(operation, arg_name, arg_value, expected_type)
        return

    # Handle regular types
    _check_regular_type(operation, arg_name, arg_value, expected_type)


# Sub-functions for type-checking logic
def _is_none_type(expected_type):
    return expected_type is None or expected_type is type(None)


def _check_none_type(operation, arg_name, arg_value, expected_type):
    if arg_value is not None:
        _raise_type_error(operation, arg_name, expected_type, arg_value)


def _is_union_type(expected_type):
    return get_origin(expected_type) is Union


def _check_union_type(operation, arg_name, arg_value, expected_type):
    """
    Checks if a value matches any of the types in a Union.
    """

    valid = False
    for t in get_args(expected_type):
        if isinstance(t, TypeVar):
            bound = _resolve_typevar_bound(t, recursive_guard=frozenset())
            if bound and isinstance(arg_value, bound):
                valid = True
                break
        elif isinstance(arg_value,
                        t if not isinstance(t, TypeVar) else object):
            valid = True
            break
    if not valid:
        _raise_type_error(operation, arg_name, expected_type, arg_value)


def _is_instance_of_union(arg_value, union_member_type):
    """
    Helper to check if a value matches one of the types in a Union.

    """

    origin = get_origin(union_member_type)

    # Handle TypeVars (e.g., ~D)
    if isinstance(union_member_type, TypeVar):
        bound = _resolve_typevar_bound(
            union_member_type, recursive_guard=frozenset()
        )
        # If the bound is None or invalid, treat it as matching all types
        if bound is None:
            return True
        # Ensure the bound is a valid type before using isinstance
        if isinstance(bound, type):
            return isinstance(arg_value, bound)
        return False  # Invalid TypeVar bound

    # Handle generic origins
    if origin:
        return isinstance(arg_value, origin) and all(
            _is_instance_of_union(arg_value, arg) for arg in
            get_args(union_member_type)
        )

    # Fallback for regular types
    try:
        return isinstance(arg_value, union_member_type)
    except TypeError:
        # If isinstance fails, treat as incompatible
        return False


def _is_generic_type(expected_type):
    return get_origin(expected_type) is not None


def _check_generic_type(operation, arg_name, arg_value, expected_type):
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # Check if the value matches the generic base type
    if not isinstance(arg_value, origin):
        _raise_type_error(operation, arg_name, expected_type, arg_value)

    # Further check the type arguments for generic containers
    if origin in (list, tuple):
        _check_list_or_tuple_items(operation, arg_name, arg_value, args[0])
    elif origin == dict:
        _check_dict_items(operation, arg_name, arg_value, args)


def _check_list_or_tuple_items(operation, arg_name, arg_value, item_type):
    for item in arg_value:
        if not isinstance(item, item_type):
            _raise_type_error(
                operation,
                arg_name,
                f"list[{item_type}]",
                arg_value
            )


def _check_dict_items(operation, arg_name, arg_value, args):
    key_type, value_type = args
    for key, value in arg_value.items():
        if not isinstance(key, key_type) or not isinstance(value, value_type):
            _raise_type_error(
                operation,
                arg_name,
                f"dict[{key_type}, {value_type}]",
                arg_value
            )


def _check_typevar_bound(operation, arg_name, arg_value, type_var):
    """
    Checks if a value matches the bound of a TypeVar.
    """

    bound = _resolve_typevar_bound(type_var, recursive_guard=frozenset())
    if not (bound is None or isinstance(arg_value, bound)):
        _raise_type_error(operation, arg_name, type_var, arg_value)


def _resolve_typevar_bound(type_var, recursive_guard=None):
    """
    Resolves the bound for a TypeVar, if present.
    """

    if recursive_guard is None:
        recursive_guard = frozenset()

    bound = type_var.__bound__

    if isinstance(bound, ForwardRef):  # If the bound is a forward reference
        # Resolve the forward reference using the namespace and recursive_guard
        bound = bound._evaluate(
            globalns=namespace,
            localns=namespace,
            recursive_guard=recursive_guard | frozenset({type_var.__name__}),
        )

    # Default to object if no bound
    return bound if bound is not None else object


def _check_regular_type(operation, arg_name, arg_value, expected_type):
    if not isinstance(arg_value, expected_type):
        _raise_type_error(operation, arg_name, expected_type, arg_value)


def _raise_type_error(operation: Callable, arg_name, expected_type,
                      arg_value):
    """
    Raises a TypeError with a descriptive message.
    """

    op_name = _get_operation_name(operation)
    msg = _construct_type_error_message(op_name, arg_name, expected_type,
                                        arg_value)
    log_error(msg)
    raise TypeError(msg)


def _construct_type_error_message(op_name, arg_name, expected_type, arg_value):
    """
    Constructs an error message for type mismatch.
    """

    return (f"Unexpected data type in '{op_name}'. '{arg_name}' must be "
            f"{expected_type}, got {type(arg_value).__name__} instead.")


def _check_return_type(operation: Callable, result, expected_type):
    """
    Checks if the return value matches the expected type.

    Raises
    ------
    TypeError
        If the return value does not match the expected type.

    """

    if not isinstance(result, expected_type):
        op_name = _get_operation_name(operation)
        msg = (f"Unexpected return type of '{op_name}'. Must be"
               f" {expected_type}, "
               f"got {type(result).__name__} instead.")
        log_error(msg)  # Assume this function logs and raises the error
        raise TypeError(msg)

# endregion --- Protected Functions
