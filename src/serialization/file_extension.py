"""
file_extension.py
-----------------
Version 1.0, validated on 2024-09-10

This module provides an exhaustive list of file extensions that this project
knows to handle. It is mainly called by the settings and the file and
serialization classes. Add more extensions to the list, as you add new classes
and methods to support more extensions within the project.

"""

from __future__ import annotations

from enum import StrEnum


class FileExtension(StrEnum):
    """
    FileExtension class.

    This class provides string constants (str) for file extensions.

    """

    CSV = ".csv"
    JSON = ".json"
    JSONL = ".jsonl"
    LOG = ".log"
    PKL = ".pkl"
    TXT = ".txt"
    XLS = ".xls"
    XLSX = ".xlsx"
