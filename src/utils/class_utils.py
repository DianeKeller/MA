"""
class_utils.py
--------------
Version 1.0, updated on 2025-02-05

This module provides utility functions working with Python classes, namely
dynamic class instantiation and retrieval of the method resolution order (MRO)
of a given class.

Functions
---------
extract_attr_type_and_description(
        attr: Any, cls: type, name: str, is_property: bool = False
) -> Tuple[str, str]
    Extracts the type hint and description from an attribute or property.

find_attributes(cls: type) -> Dict[str, Tuple[str, str]]
    Retrieves all attributes and properties of a class, along with their type
    hints and descriptions.

instantiate_class_from_module_name(
        module_name: str, class_name: str, *args, **kwargs
) -> Any:
    Dynamically instantiates a class from a specified module by name.

get_method_resolution_order(cls: type) -> List[type]:
    Retrieves the method resolution order (MRO) of a given class.

print_method_resolution_order(cls: type) -> None:
    Prints the method resolution order (MRO) of a given class.

"""

import importlib
import inspect
from typing import Any, List, Dict, Tuple

from src.logging_mixin import LoggingMixin
from src.utils.print_utils import print_in_box
from src.utils.string_utils import StringUtils

log = LoggingMixin().log


def instantiate_class_from_module_name(
        module_name: str,
        class_name: str,
        *args, **kwargs
) -> Any:
    """
    Dynamically instantiates a class from a specified module by name.

    Parameters
    ----------
    class_name : str
        The name of the class to instantiate.

    module_name : str
        The name of the class's module.

    args : Any
        The arguments needed for the instantiation of the given class.

    kwargs : Any
        Any keyword arguments to pass to the constructor of the class that is
        to be instantiated.


    Returns
    -------
    Any
        The instantiated class.


    Raises
    ------
    ImportError
        If the specified module could not be imported.

    AttributeError
        If the specified class was not found in the module.

    """

    try:
        # Dynamically import the module that contains the class.
        module = importlib.import_module(module_name)

    except ImportError as err:
        msg = "Module %s not found: %s" % (module_name, err)
        log(msg, 'error')
        raise ImportError(msg) from err

    try:
        # Get the class from the module
        cls = getattr(module, class_name)

    except AttributeError as err:
        msg = "Class %s not found in module %s: %s" % (
            class_name, module_name, err
        )
        log(msg, 'error')
        raise AttributeError(msg) from err

    # Instantiate the class
    return cls(*args, **kwargs)


def get_method_resolution_order(cls: type) \
        -> List[type]:
    """
    Retrieves the method resolution order (MRO) of a given class.

    Parameters
    ----------
    cls : type
        The class for which the method resolution order is to be retrieved.

    Returns
    -------
    List[type]
        A list of classes called by the given class, in the order they are
        called.

    """

    return cls.mro()


def print_method_resolution_order(cls: type) \
        -> None:
    """
    Prints the method resolution order (MRO) of the given class.

    Parameters
    ----------
    cls : type
        The class for which the method resolution order is to be printed.

    """

    title = 'MRO'
    body = get_method_resolution_order(cls)

    print_in_box(title, body)


def find_attributes(cls: type) \
        -> Dict[str, Tuple[str, str]]:
    """
    Retrieves all attributes and properties of a class, including descriptions.

    Retrieves all attributes and properties of a class, along with their type
    hints and descriptions.

    Parameters
    ----------
    cls : type
        The class from which to extract attributes and properties.

    Returns
    -------
    Dict[str, Tuple[str, str]]
        A dictionary where keys are attribute names and values are tuples
        containing the type hint and description.

    """

    attributes: Dict[str, Tuple[str, str]] = {}

    for name, obj in inspect.getmembers(
            cls, lambda x: not callable(x) and not inspect.isroutine(x)
    ):
        if not name.startswith('_'):  # Skip private and protected attributes
            if isinstance(obj, property):
                # For properties, use the getter method (obj.fget)
                attributes[name] = extract_attr_type_and_description(
                    obj.fget, cls,
                    name,
                    is_property=True
                )
            else:
                # For regular attributes
                attributes[name] = extract_attr_type_and_description(
                    obj, cls, name
                )

    return attributes


def extract_attr_type_and_description(
        attr: Any,
        cls: type,
        name: str,
        is_property: bool = False
) -> Tuple[str, str]:
    """
    Extracts the type hint and description from an attribute or property.

    Parameters
    ----------
    attr : Any
        The attribute or property from which to extract type information.

    cls : type
        The class to which the attribute belongs.

    name : str
        The name of the attribute or property.

    is_property : bool
        Whether the attribute is a property. Default is False.

    Returns
    -------
    Tuple[str, str]
        A tuple containing the type hint as a string and the first sentence
        of the description.

    """

    # Get type hint
    if is_property:
        # For properties, get type hint from the property's getter method
        type_hint = inspect.signature(attr).return_annotation
    else:
        # For regular attributes, get from __annotations__
        type_hint = cls.__annotations__.get(name, 'No type hint available')

    if type_hint is inspect.Signature.empty:
        type_hint = 'No type hint available'
    elif isinstance(type_hint, type):
        type_hint = type_hint.__name__
    else:
        type_hint = str(type_hint).replace(
            "<class '", ""
        ).replace("'>", "")

    # Get the docstring (description)
    doc = inspect.getdoc(attr) or getattr(cls, name).__doc__
    description = StringUtils.get_first_sentence(doc) if doc \
        else "No description available."

    return type_hint, description
