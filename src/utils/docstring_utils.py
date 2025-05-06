"""
docstring_utils.py
------------------
Version 1.0, updated on 2024-12-19

This module provides utility functions to help automate the generation of
docstrings.

Functions
---------
add_attributes_to_class_docstring(module_name: str) -> None:
    Retrieves information about the attributes in the given module.

add_methods_to_class_docstring(module_name: str) -> None:
    Retrieves information about the methods in the given module.

find_attributes_and_modules(module: str):
    Calls the methods to add information to docstrings and find_unused methods.

find_unused(module_name: str):
    Finds unused methods in the module.

update_attributes_section(module: Callable, content: str) -> str
    Suggests updates for the attributes section of class docstrings within a
    module.

update_methods_section(module: Callable, content: str) -> str
    Suggests updates for the 'Methods' or 'Functions' section of a
    class or module
    docstring.

Usage
-----
Insert the lines between the double hyphen lines in the class docstring
of a module you intend to provide with information about attributes and
methods. Then run the find_attributes_and_modules method.

=============================================
Attributes
----------
### Start A ###
### End A ###

Methods
-------
### Start ###
### End ###
=============================================

"""

import importlib
import inspect
import re
import sys
from types import ModuleType

import settings
from logger import Logger
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.class_utils import find_attributes
from src.utils.method_utils import (
    find_methods,
    update_module,
    dynamic_import,
    find_unused_methods_in_project
)
from src.utils.string_utils import StringUtils
from src.utils.print_utils import print_in_box


# region --- Public Functions

def update_attributes_section(module: ModuleType, content: str) \
        -> str:
    """
    Suggests updates for the attributes section of class docstrings.

    Suggests updates for the attributes section of class docstrings within
    modules.

    Returns a list of the given module's attributes with type hints and
    short descriptions to be inserted in the 'Attributes' section of the
    module or class docstring of the module.

    The attribute details (names, types, and descriptions) are derived from
    the attributes and properties of the class contained in the given module.

    Parameters
    ----------
    module : MaduleType
        The module containing the classes.

    content : str
        The content of the module file as a string.

    Returns
    -------
    str
        The content to insert in the 'Attributes' section of the class
        docstring.

    """

    update_module(module)

    start_marker = "### Start A ###"
    end_marker = "### End A ###"

    # Iterate through classes defined in the module
    for name, cls in inspect.getmembers(
            module,
            lambda x: inspect.isclass(x) and x.__module__ == module.__name__
    ):
        # Find the attribute markers in the content
        start_index = content.find(start_marker)
        end_index = content.find(end_marker, start_index)

        if start_index != -1 and end_index != -1:
            # Extract and format the class attributes
            attributes_info = find_attributes(cls)
            formatted_attributes = []

            for attr_name, (type_hint, description) in sorted(
                    attributes_info.items()
            ):
                # Clean up type hints and descriptions
                type_hint = type_hint.replace('typing.', '')
                description = re.sub(
                    r'\bReturns the\b|\bGets the\b',
                    'The',
                    description
                )

                # Handle 'Optional' type hints
                if type_hint.startswith('Optional'):
                    types = re.findall(r'\[(.*?)\]', type_hint)
                    type_hint = ' | '.join(types) + ' | None'

                # Format the attribute line
                formatted_attributes.append(
                    f"{attr_name} : {type_hint}\n    {description}\n"
                )

            # Replace the attribute section in the content
            attributes_section = "\n".join(formatted_attributes)
            content = "\n" + attributes_section + "\n"

    return content


def update_methods_section(module: ModuleType, content: str) -> str:
    """
    Suggests updates for the 'Methods' or 'Functions' section of a docstring.

    Suggests updates for the 'Methods' or 'Functions' section of a class or
    module docstring.

    This function finds all module-level functions and class methods,
    then formats and inserts their signatures and descriptions between
    the specified markers in the content.

    Parameters
    ----------
    module : ModuleType
        The module in which the functions or methods are defined.

    content : str
        The content of the file/module as a string.

    Returns
    -------
    str
        The content to insert in the 'Methods' or "Functions" section of the
        class or module docstring.
    """
    update_module(module)
    importlib.reload(module)

    start_marker = "### Start ###"
    end_marker = "### End ###"

    # Find the method markers in the content
    start_index = content.find(start_marker)
    end_index = content.find(end_marker, start_index)

    if start_index == -1 or end_index == -1:
        raise CriticalException(
            Logger(f"{inspect.currentframe().f_code.co_name}").get_logger(),
            "Start or end marker not found in content."
        )

    formatted_functions = []

    # Process module-level functions
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if func.__module__ == module.__name__:
            # Extract the function signature and description
            signature = str(inspect.signature(func))
            doc = inspect.getdoc(func) or "No description available."
            description = StringUtils.get_first_sentence(doc)
            formatted_functions.append(
                f"{name}{signature}:\n    {description}\n"
            )

    # Process methods inside classes in the module
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ == module.__name__:
            methods_info = find_methods(cls)
            for method_name, (signature, description) in sorted(
                    methods_info.items()
            ):
                formatted_functions.append(
                    f"{method_name}{signature}:\n    {description}\n"
                )

    # Join the formatted function/method list and replace the content
    functions_section = "\n".join(formatted_functions)
    updated_content = functions_section

    return updated_content


def find_unused(module_name: str):
    module_name = f"src.{module_name}"
    project_path = settings.ROOT

    unused_methods = find_unused_methods_in_project(module_name, project_path)

    title = f"Unused methods in {module_name}"
    body = unused_methods

    print_in_box(title, body)


def add_methods_to_class_docstring(module_name: str) \
        -> None:
    """
    Retrieves information about the attributes in the given module.

    Parameters
    ----------
    module_name : str
        The name of the module in which to search for attributes.

    """

    my_module = dynamic_import(module_name)

    # Load the module's content from the file (as an example, replace with
    # actual file path)
    with open(my_module.__file__, 'r') as file:
        module_content = file.read()

    # Update the content with function signatures and first docstring sentences
    updated_content = update_methods_section(
        my_module,
        module_content
    )

    # Output the updated content (or write it back to a file)
    print(updated_content)


def add_attributes_to_class_docstring(module_name: str) \
        -> None:
    """
    Retrieves information about the attributes in the given module.

    Dynamically retrieves information about the attributes in the given module
    that can be used to update the class docstring in the module.

    Parameters
    ----------
    module_name : str
        The name of the module to import and inspect.

    """

    my_module = dynamic_import(module_name)

    # Load the module's content from the file (as an example, replace with
    # actual file path)
    with open(my_module.__file__, 'r') as file:
        module_content = file.read()

    # Update the content with function signatures and first docstring sentences
    updated_content = update_attributes_section(
        my_module,
        module_content
    )

    # Output the updated content (or write it back to a file)
    print(updated_content)


def find_attributes_and_modules(module: str):
    """
    Calls the methods to add information to docstrings and find_unused methods.

    Calls the methods to add attributes and methods to docstrings and the
    find_unused method.

    Parameters
    ----------
    module : str
        The name of the module in which to search for attributes and methods.

    Returns
    -------

    """
    add_attributes_to_class_docstring(module)
    add_methods_to_class_docstring(module)

    find_unused(module)

# endregion --- Public Functions

# region --- Protected Functions

# endregion --- Protected Functions
