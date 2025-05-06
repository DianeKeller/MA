"""
constants.py
------------
Version 1.0, updated on 2024-10-31

"""

from enum import StrEnum
from typing import cast

from settings import get_setting, SettingCategories

FIRST_ID: int = cast(int, get_setting(
    SettingCategories.NUM, 'FIRST_ID'
))
MAX_ITEMS: int = cast(int, get_setting(
    SettingCategories.NUM, 'MAX_ITEMS'
))
MAX_STRING_LENGTH: int = cast(int, get_setting(
    SettingCategories.NUM,
    'MAX_STRING_LENGTH'
))
INFINITY: int = cast(int, get_setting(
    SettingCategories.NUM, 'INFINITY'
))
DEFAULT_LENGTH: int = cast(int, get_setting(
    SettingCategories.NUM,
    'DEFAULT_LENGTH'
))
BPE_MERGES: int = cast(int, get_setting(
    SettingCategories.NUM, 'BPE_MERGES'
))
BIG_DATA_THRESHOLD: int = cast(int, get_setting(
    SettingCategories.NUM,
    'BIG_DATA_THRESHOLD'
))
INT_NONE: int = cast(int, get_setting(
    SettingCategories.NUM, 'INT_NONE'
))

# Data types
INT: int = cast(int, get_setting(SettingCategories.DTYPE, 'INT'))
FLOAT: int = cast(int, get_setting(
    SettingCategories.DTYPE, 'FLOAT'
))

# Default language
DEFAULT_LANGUAGE: str = cast(str, get_setting(
    SettingCategories.STR, 'DEFAULT_LANGUAGE'
))


class Language(StrEnum):
    """
    Language class.

    This class provides string constants (str) for language codes.

    """

    DE: str = 'de'
    EN: str = 'en'
    ES: str = 'es'
    FR: str = 'fr'
    IT: str = 'it'
    NL: str = 'nl'
    PT: str = 'pt'
    RO: str = 'ro'
