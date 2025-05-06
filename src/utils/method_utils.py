"""
method_utils.py
---------------
Version 1.0, updated on 2025-05-01

This module provides functions to analyze and handle methods and functions.

Functions
---------
dynamic_import(module_name: str):
    Dynamically imports a module given its module name as a string.

extract_method_names(module_name: str) -> List[str]:
    Extracts all method names from a given module.

find_unused_methods_in_project(module_name: str, project_path: str)
        -> List[str]:
    Finds unused methods in the specified module.

get_module_file_path(module_name: str) -> str:
    Dynamically retrieves the file path of a module from its module name.

search_method_in_project(method_name: str, project_path: str,
        exclude_module: str) -> bool:
    Searches usages of the specified method in the files of the project path.

"""
import abc
import importlib
import inspect
import os
import re
from types import ModuleType
from typing import List, Dict, Tuple, Callable

from logger import Logger
from src.logging_mixin import LoggingMixin
from src.utils.string_utils import StringUtils

logger = Logger(__name__).get_logger()
log = LoggingMixin().log


def dynamic_import(module_name: str) \
        -> ModuleType | None:
    """
    Dynamically imports a module given its module name as a string.

    Parameters
    ----------
    module_name : str
        The full name of the module to import (e.g., 'src.utils.my_module').

    Returns
    -------
    module : ModuleType | None
        The imported module.

    """

    try:
        # Import the module dynamically
        module = importlib.import_module(module_name)
        return module

    except ImportError as e:
        print(f"Error importing module {module_name}: {e}")
        return None


def update_module(module: ModuleType) \
        -> None:
    """
    Updates the module in the cache to get up-to-date information.

    Parameters
    ----------
    module : ModuleType
        The module to update.

    """

    importlib.reload(module)


def extract_method_names(module_name: str) \
        -> List[str]:
    """
    Extracts all public method and function names from a given module.

    Parameters
    ----------
    module_name : str
        The name of the module to extract method names from.

    Returns
    -------
    List[str]
        A list of public method and function names found in the module.

    """

    # Import the module dynamically using importlib
    module = importlib.import_module(module_name)
    method_names = []

    # Extract module-level functions
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if func.__module__ == module.__name__ and not name.startswith('_'):
            method_names.append(name)

    # Extract methods from classes
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ == module.__name__:
            for name, method in inspect.getmembers(cls, inspect.isfunction):
                if not name.startswith('_'):  # Ensuring it's a public method
                    method_names.append(f"{name}")

    return method_names


def get_module_file_path(module_name: str) \
        -> str:
    """
    Dynamically retrieves the file path of a module from its module name.

    Parameters
    ----------
    module_name : str
        The name of the module (e.g., "src.utils.list_utils").

    Returns
    -------
    str
        The absolute file path of the module.

    """

    # Import the module dynamically using importlib
    module = importlib.import_module(module_name)

    # Get the file path of the module using the __file__ attribute
    module_file_path = module.__file__

    # Convert it to an absolute path for consistent comparison
    return os.path.abspath(module_file_path)


def search_method_in_project(
        method_name: str,
        project_path: str,
        exclude_module: str
) -> bool:
    """
    Searches usages of the specified method in the files of the project path.

    Searches for a method name in all Python files within the project
    directory, excluding the file where the method is implemented.

    Parameters
    ----------
    method_name : str
        The name of the method to search for.

    project_path : str
        The path to the root directory of the project.

    exclude_module : str
        The name of the module where the method is implemented. It is
        excluded from the search.

    Returns
    -------
    bool
        True if the method is found somewhere in the project, False otherwise.

    """

    # Define a regex pattern to match the method name
    pattern = re.compile(rf'\b{method_name}\b')
    exclude_file = get_module_file_path(exclude_module)

    # Traverse the entire project directory to search for the method
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):  # Only search Python files
                file_path = os.path.join(root, file)
                test_path = os.path.join(root, 'test')
                x_path = os.path.join(root, 'x_')

                # Skip the file where the method is implemented
                if (
                        file_path.startswith(test_path)
                        or file_path.startswith(x_path)
                        or file_path == exclude_file
                ):
                    continue

                # Search the method name in the content of the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # If the pattern is found in the file, return True
                    if re.search(pattern, content):
                        return True
    return False


def find_methods(cls: type) \
        -> Dict[str, Tuple[str, str]]:
    """
    Retrieves all public and abstract methods of a class, along with their
    signatures and descriptions.

    Parameters
    ----------
    cls : type
        The class from which to extract methods.

    Returns
    -------
    Dict[str, Tuple[str, str]]
        A dictionary where keys are method names and values are tuples
        containing the method signature and description.

    """

    methods = {}

    # Get public methods (excluding those starting with '_')
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            methods[name] = extract_method_info(method)

    # Get abstract methods (if applicable)
    if isinstance(cls, abc.ABCMeta):
        for name, method in inspect.getmembers(
            cls, predicate=inspect.isabstract
        ):
            # Add if not already present
            methods.setdefault(name, extract_method_info(method))

    return methods


def extract_method_info(method: Callable) \
        -> Tuple[str, str]:
    """
    Extracts the method signature and description.

    Parameters
    ----------
    method : Callable
        The method from which to extract the signature and description.

    Returns
    -------
    Tuple[str, str]
        A tuple containing the method signature and the first sentence of
        the description.

    """

    signature = str(inspect.signature(method))
    doc = inspect.getdoc(method)
    description = StringUtils.get_first_sentence(doc) if doc \
        else "No description available."
    return signature, description


def find_unused_methods_in_project(
        module_name: str,
        project_path: str
) -> List[str]:
    """
    Finds unused methods in the specified module.

    Finds methods in the specified module that are not used anywhere else
    in the project.

    Parameters
    ----------
    module_name : str
        The name of the module to extract method names from.

    project_path : str
        The path to the root directory of the project.

    Returns
    -------
    List[str]
        A list of method names that are not found anywhere else in the project.

    """

    unused_methods = []
    method_names = extract_method_names(module_name)

    for method in method_names:
        if not search_method_in_project(method, project_path, module_name):
            unused_methods.append(method)

    return unused_methods
