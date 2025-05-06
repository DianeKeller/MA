"""
settings.py
-----------
Version 1.0, updated on 2025-05-01

This module defines the settings used throughout the project, e.g.
    - Data file types and their
        - Storage locations ('PATH')
        - File extensions ('EXTENSION')
        - Test file names ('TEST FILE')

Usage
-----
Get a project setting anywhere in the project using the function
    >>> get_setting(setting_category, setting_name)

For example, to get the path for CSV files, you can use:
    >>> get_setting(SettingCategories.CSV, 'PATH')

"""

import logging
import os
import sys
from enum import Enum, auto
from typing import TypedDict, Dict

# Custom Enum to define file extension types
from src.serialization.file_extension import FileExtension


class SettingCategories(Enum):
    """
    Enumerates categories to organize the different settings for this project.

    The Enum type is used for easy access and modification.

    Attributes
    ----------
    CSV : Enum
        Small dataframes (DataFrame).
    XLS : Enum
        Small dataframes (DataFrame) (only for reading data).

    JSON : Enum
        Data from Dict.
    JSONL : Enum
        Data from Dict.
    PKL : Enum
        Big dataframes (DataFrame).
    TXT : Enum
        Content of string variables.
    NUM : int

    """

    # Data file types for the storage of data coming from different data types.
    CSV = auto()  # Small dataframes (DataFrame).
    XLS = auto()  # Small dataframes (DataFrame).
    XLSX = auto()  # Small dataframes (DataFrame).
    JSON = auto()  # Data from Dict.
    JSONL = auto()  # Data from Dict.
    PKL = auto()  # Big dataframes (DataFrame).
    TXT = auto()  # Content of string variables.

    # Logging parameters
    LOG = auto()

    # Numeric constants (int)
    NUM = auto()

    # String constants (str)
    STR = auto()

    # (Pandas) Data types
    DTYPE = auto()


class SettingValue(TypedDict, total=False):
    """
    Explicitly set the types of the setting values to ensure type safety.
    """
    PATH: str
    SEPARATOR: str
    EXTENSION: FileExtension
    STRATEGY: str
    SIZE: int
    NR_BACKUPS: int
    LEVEL: int
    FIRST_ID: int
    MAX_ITEMS: int
    MAX_STRING_LENGTH: int
    INFINITY: int
    DEFAULT_LENGTH: int
    BPE_MERGES: int
    BIG_DATA_THRESHOLD: int
    INT_NONE: int
    FLOAT: str
    INT: str
    DEFAULT_LANGUAGE: str


SettingsDict = Dict[SettingCategories, SettingValue]

# Root directory of the project, derived from the absolute path of this
# settings file.
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(ROOT, 'data')
LOG_ROOT = os.path.join(ROOT, 'log')

# Set DEBUG_MODE to 'False' in production!
DEBUG_MODE = True

# Set the log level
# Decide which messages to show in the console
LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO

# Add the string identifier of a message you want to switch off to the list:
DISALLOWED_MESSAGES = [
    'no_file_name',
    'set_index_manually',
    'log_info_before_saving',
    'log_info_after_saving',
    'Prompt successfully validated',
    'Validating next prompt',
    'Validating prompt',
    'Using cached data',
    'PromptsProvider using strategy nr',
]

# Define the settings for each category
SETTINGS: SettingsDict = {
    SettingCategories.CSV: {
        'PATH': os.path.join(DATA_ROOT, 'csv'),
        'SEPARATOR': ';',
        'EXTENSION': FileExtension.CSV,
        'STRATEGY': 'CsvStrategy'
    },
    SettingCategories.XLS: {
        'PATH': os.path.join(DATA_ROOT, 'xls'),
        'EXTENSION': FileExtension.XLS,
        'STRATEGY': 'XlsStrategy'
    },
    SettingCategories.XLSX: {
        'PATH': os.path.join(DATA_ROOT, 'xlsx'),
        'EXTENSION': FileExtension.XLSX,
        'STRATEGY': 'XlsxStrategy'
    },
    SettingCategories.TXT: {
        'PATH': os.path.join(DATA_ROOT, 'txt'),
        'EXTENSION': FileExtension.TXT,
        'STRATEGY': 'TxtStrategy'
    },
    SettingCategories.JSON: {
        'PATH': os.path.join(DATA_ROOT, 'json'),
        'EXTENSION': FileExtension.JSON,
        'STRATEGY': 'JsonStrategy'
    },
    SettingCategories.JSONL: {
        'PATH': os.path.join(DATA_ROOT, 'jsonl'),
        'EXTENSION': FileExtension.JSONL,
        'STRATEGY': 'JsonlStrategy'
    },
    SettingCategories.PKL: {
        'PATH': os.path.join(DATA_ROOT, 'pkl'),
        'EXTENSION': FileExtension.PKL,
        'STRATEGY': 'PklStrategy'
    },
    SettingCategories.LOG: {
        'SIZE': 1048576,
        'NR_BACKUPS': 5,
        'LEVEL': LOG_LEVEL,
        'EXTENSION': FileExtension.LOG
    },
    SettingCategories.NUM: {
        'FIRST_ID': 0,
        'MAX_ITEMS': 3,
        'MAX_STRING_LENGTH': 100,
        'INFINITY': sys.maxsize,
        'DEFAULT_LENGTH': 250,
        'BPE_MERGES': 50000,
        'BIG_DATA_THRESHOLD': 300000,
        'INT_NONE': -9999999999
    },
    SettingCategories.STR: {
        'DEFAULT_LANGUAGE': 'en'
    },
    SettingCategories.DTYPE: {
        'INT': 'Int64',
        'FLOAT': 'Float64',
    }
}


def get_setting(setting_category: SettingCategories, setting_name: str) \
        -> str | int | FileExtension:
    """
    Retrieves the value of a specific setting within a given category.

    Parameters
    ----------
    setting_category : SettingCategories
        The category of the setting to retrieve.

    setting_name : str
        The name of the setting within the category to retrieve.

    Returns
    -------
    str | int | FileExtension
        The value of the requested setting, which can be of type string or
        FileExtension).

    Raises
    ------
    KeyError
        If setting_category or setting_name does not exist.

    Examples
    --------

    To get the path for CSV files, you can use:

    .. code-block:: python

        >>>    get_setting(SettingCategories.CSV, 'PATH')

    """

    # Check the input variables.

    # Catches inputs with wrong data types such as strings, for example:
    # get_setting('BAT', 'EXTENSION'). Trying to call the function with a
    # non-existing attribute of SettingCategories will throw an
    # AttributeError even before the function is entered, for example:
    # get_setting(SettingCategories.BAT, 'EXTENSION').

    if setting_category not in SETTINGS:
        raise KeyError(f"There is no category {setting_category} in the "
                       f"settings.")

    category_settings = SETTINGS[setting_category]

    if setting_name not in category_settings:
        raise KeyError(f"There is no setting {setting_name} in the setting "
                       f"category {setting_category.name}.")

    # Mypy complains here about the "setting_name" variable not being a string
    # literal but this cannot be helped in this dynamic approach, and it does
    # not prevent the code from working as wished.
    return category_settings[setting_name]


def get_settings_category_from_string(category_name: str) \
        -> SettingCategories:
    """
    Convert the input string to a SettingCategories enum member

    Parameters
    ----------
    category_name : str
        The category name to convert into a SettingCategories enum member.

    Returns
    -------
    SettingCategories
        The requested SettingCategories enum member.

    """

    try:
        category = next(cat for cat in SettingCategories if
                        cat.name == category_name.upper())
    except StopIteration as err:
        msg = "No matching category for name '%s'." % category_name
        raise ValueError(msg) from err

    return category

# If you want to define settings which are based on other settings defined
# in the SETTINGS dictionary, place them here:
