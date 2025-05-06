"""
directory_factory.py
--------------------
Version 1.0, updated on 2024-09-19

This module provides a factory for creating and managing directories within the
project's data folder. It defines a 'DirectoryFactory' class that helps create
or initialize specific subdirectories for storing files, and ensures that these
directories exist in the file system. The module also includes a utility
function for path validation.

Classes
-------
DirectoryFactory(LoggingMixin)

"""

import os

import settings
from logger import Logger
from src.logging_mixin import LoggingMixin
from src.serialization.directory import Directory

logger = Logger(__name__).get_logger()
log = LoggingMixin().log


def check_path(path: str) \
        -> None:
    """
    Validates the existence of a given file path.

    This function checks whether a provided file path exists. If the path
    is invalid or does not exist, it logs an error message and raises a
    FileNotFoundError.

    Parameters
    ----------
    path : str
        The file path to validate.

    Raises
    ------
    FileNotFoundError
        If the specified path does not exist.

    """

    if not os.path.exists(path):
        msg = "Invalid path: %s" % path
        log(msg, 'error')
        raise FileNotFoundError(msg)


class DirectoryFactory(LoggingMixin):
    """
    DirectoryFactory class

    Factory class for creating and managing directory structures within the
    project's data folder. It provides static methods to create or initialize
    specific subdirectories and ensure their paths exist. The class utilizes
    the 'Directory' class to encapsulate directory details and operations.

    Inherits
    --------
    LoggingMixin : Mixin class to provide logging functionality.

    Methods
    -------
    create(file_extension: str, sub_dir_name: str) -> Directory:
        Creates and returns a 'Directory' instance for an existing
        subdirectory.

    make(file_extension: str, sub_dir_name: str) -> Directory:
        Creates the specified subdirectory in the file system and returns a
        'Directory' instance.

    """

    @staticmethod
    def create(file_extension: str, sub_dir_name: str) \
            -> Directory:
        """
        Creates a Directory instance for a subdirectory in the data directory.

        Creates a Directory instance for a subdirectory in the data
        directory of this project from a given file_extension and a
        subdirectory name.

        Ensures the path of the Directory exists by calling the
        check_path function, which will raise a FileNotFoundError if the
        path is incorrect.

        Parameters
        ----------
        file_extension : str
            The file extension of the files the directory is supposed to store.

        sub_dir_name : str
            The name of the subdirectory.

        Returns
        -------
        Directory
            An instance of the Directory class with the path property set.

        """

        path = os.path.join(settings.DATA_ROOT, file_extension, sub_dir_name)
        check_path(path)
        return Directory(path)

    @staticmethod
    def make(file_extension: str, sub_dir_name: str) \
            -> Directory:
        """
        Creates the specified data subdirectory.

        Creates the specified data subdirectory in the file system and creates
        a corresponding Directory instance. The directory path is composed
        of the DATA_ROOT specified in the settings, the file_extension
        serving as the data subfolder name and the sub_dir_name that is to be
        used for the subdirectory that is to bbe placed within this data
        subfolder.

        Ensures the path was successfully created by calling the
        check_path function, which will raise a FileNotFoundError if the
        path was not created.

        Parameters
        ----------
        file_extension : str
            The file extension of the files the directory is used to store.

        sub_dir_name : str
            The name of the subdirectory.

        Returns
        -------
        Directory
            An instance of the 'Directory' class representing the newly
            created subdirectory.

        """

        path = os.path.join(settings.DATA_ROOT, file_extension, sub_dir_name)
        os.makedirs(path)
        check_path(path)
        return Directory(path)
