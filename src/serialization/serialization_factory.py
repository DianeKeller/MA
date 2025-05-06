"""
serialization_factory.py
------------------------
Version 1.0, updated on 2024-09-19

This module provides a function to create a serializer with a specified
file name for a specified file type.

Functions
---------
get_serializer(file_type: str, file_name: str) -> Serializer:
    Creates a Serializer instance based on the specified file type.

"""

from settings import get_setting, get_settings_category_from_string
from src.logging_mixin import LoggingMixin
from src.serialization.file import File
from src.serialization.file_extension import FileExtension
from src.serialization.serialization_strategy import SerializationStrategy
from src.serialization.serializer import Serializer
from src.utils.class_utils import instantiate_class_from_module_name
from src.utils.data_utils import is_none_or_empty
from src.utils.string_utils import StringUtils

log = LoggingMixin().log


def get_serializer(file_type: str, file_name: str) \
        -> Serializer:
    """
    Creates a Serializer instance based on the specified file type.

    Dynamically creates and returns an instance of the Serializer
    class using the serialization strategy that corresponds to the specified
    file type.

    Logs an informational message if no file name was provided and a default
    file name was set.

    Parameters
    ----------
    file_type : str
        A string designing the file type. This is supposed to be the first
        part of the name of the serialization strategy to use, e.g. 'csv',
        'pkl', 'json', 'txt'. If it None or empty, it is set
        to 'csv' by default.

    file_name : str
        The name of the file that is to be used for the serialization,
        without the file extension.

    Returns
    -------
    Serializer
        An instance of the Serializer class that uses the serialization
        strategy that corresponds to the specified file type.

    """

    # Handle missing file name gracefully by defaulting to 'file':
    if is_none_or_empty(file_name):
        msg = "No file name given. Using 'file' by default."
        log(msg, 'info', 'no_file_name')
        file_name = 'file'

    strategy = _get_serialization_strategy(file_type, file_name)

    return Serializer(strategy)


def _get_serialization_strategy(file_type: str, file_name: str) \
        -> SerializationStrategy:
    """
    Creates a SerializationStrategy instance based on the specified file type.

    Dynamically creates and returns an instance of the serialization
    strategy that corresponds to the specified file type.

    Parameters
    ----------
    file_type : str
        A string designing the file type. This is supposed to be the first
        part of the name of the serialization strategy to use, e.g. 'csv',
        'pkl', 'json', 'txt'. If it None or empty, it is set
        to 'csv' by default.

    file_name : str
        The name of the file that is to be used for the serialization,
        without the file extension.

    Returns
    -------
    An instance of the specified strategy class.

    """

    # Handle missing file type gracefully by defaulting to 'csv':
    if not file_type:
        file_type = 'csv'

    strategy_name = file_type.lower().capitalize() + "Strategy"
    converted_name = StringUtils.convert_class_name_into_module_name(
        strategy_name
    )

    module_name = (f"src.serialization."
                   f"{converted_name}")

    settings_category = get_settings_category_from_string(file_type)
    extension = FileExtension(str(get_setting(
        settings_category, 'EXTENSION'
    )))
    file = File(file_name, extension)

    return instantiate_class_from_module_name(
        module_name, strategy_name, file
    )
