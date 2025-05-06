"""
sys_utils
---------
Version 1.0, validated on 2024-12-18

This module provides functions to analyze system conditions like program
versions, environment variables, available memory etc.

Functions
---------
check_virtual_environment() -> None:
    Checks if the Python interpreter is running inside a virtual environment.

print_all_sys_info() -> None:
    Directly or indirectly executes all functions of this module.

print_huggingface_cache_path() -> None:
    Prints the Hugging Face cache path.

print_memory_info() -> None:
    Prints all memory-related information in a box.

print_packages_path() -> None:
    Prints the path(s) of the Python packages.

print_pagefile_size() -> None:
    Prints the pagefile/swap size detailing total, used, and free swap memory.

print_python_info() -> None:
    Prints all python-related information in a box.

print_python_version() -> None:
    Prints the current Python version.

print_ram():
    Prints the current available RAM in MB and GB and additional information.

print_sphinx_version() -> None:
    Prints the version of Sphinx installed in the current Python environment.

show_sys_modules():
    Prints all the currently loaded Python modules (i.e., 'sys.modules').

"""

import site
import sys

import psutil
import sphinx
from datasets import config

from src.utils.print_utils import print_in_box, print_header, print_sep


def print_python_info() \
        -> None:
    """
    Prints all python-related information in a box.

    Executes all python-related functions in this module and prints the
    result in a box.

    """

    print_header("Python")
    check_virtual_environment()
    print_python_version()
    print_packages_path()
    print_sep()

    # Warning: Generates long output
    show_sys_modules()


def print_memory_info() \
        -> None:
    """
        Prints all memory-related information in a box.

        Executes all memory-related functions in this module and prints the
        result in a box.

    """

    print_header("Memory")
    print_ram()
    print_pagefile_size()
    print_sep()


def print_python_version() \
        -> None:
    """
    Prints the current Python version.
    """

    version = sys.version
    print(f"\nPython version: {version}")


def check_virtual_environment() \
        -> None:
    """
    Checks if the Python interpreter is running inside a virtual environment.

    Checks if the Python interpreter is running inside a virtual environment
    and prints the result.

    Additionally, prints the current Python interpreter path.

    Returns
    -------

    """
    if hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("\nInside a virtual environment")

    else:
        print("\nNot inside a virtual environment")

    print(f"Current Python interpreter: {sys.executable}")


def print_packages_path() \
        -> None:
    """
    Prints the path(s) of the Python packages.
    """

    print(f"\nPackages path: {site.getsitepackages()}")


def print_sphinx_version() \
        -> None:
    """
    Prints the version of Sphinx installed in the current Python environment.
    """

    print(f"\nSphinx version: {sphinx.__version__}")


def show_sys_modules():
    """
       Prints all the currently loaded Python modules (i.e., 'sys.modules').
    """

    title = "Python modules"
    body = sys.modules

    print_in_box(title, body)


def print_huggingface_cache_path() \
        -> None:
    """
    Prints the Hugging Face cache path.
    """

    print(f"\nHugging Face Cache: {config.HF_DATASETS_CACHE}")


def print_ram():
    """
    Prints the current available RAM in MB and GB and additional information.

    Prints the current available RAM in MB and GB and additional
    memory information.

    """

    memory_info = psutil.virtual_memory()
    available_mb = memory_info.available / (1024 ** 2)
    available_gb = available_mb / 1000
    print(f"\nAvailable RAM: {available_mb:.0f} MB / {available_gb:.2f} GB")
    print(memory_info)


def print_pagefile_size() \
        -> None:
    """
    Prints the pagefile/swap size detailing total, used, and free swap memory.
    """

    swap_info = psutil.swap_memory()
    total_swap_mb = swap_info.total / (1024 ** 2)
    used_swap_mb = swap_info.used / (1024 ** 2)
    free_swap_mb = swap_info.free / (1024 ** 2)

    total_swap_gb = total_swap_mb / 1000
    used_swap_gb = used_swap_mb / 1000
    free_swap_gb = free_swap_mb / 1000

    print(f"\nTotal Swap: {total_swap_mb:.0f} MB / {total_swap_gb:.2f} GB")
    print(f"Used Swap: {used_swap_mb:.0f} MB / {used_swap_gb:.2f} GB")
    print(f"Free Swap: {free_swap_mb:.0f} MB / {free_swap_gb:.2f} GB")

    print(swap_info)


def print_all_sys_info() \
        -> None:
    """
    Directly or indirectly executes all functions of this module.

    Notes
    -----
    The memory- and python-related functions are called via the
    print_memory_info and the print_python_info functions.

    """

    print_memory_info()

    print_sphinx_version()
    print_huggingface_cache_path()

    print_python_info()


if __name__ == '__main__':
    """
    Prints all system information made available in this module.
    
    Usage
    -----
    From a command line in the SentimenAnalysis directory:

    >>> python -m src.utils.sys_utils

    """

    print_all_sys_info()
