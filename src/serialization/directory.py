"""
directory.py
------------
Version 1.0, updated on 2025-05-01

"""

from pathlib import Path
from typing import List

from src.decorators.data_check_decorators import requires_property


class Directory:
    """
    Directory class.

    This class provides properties and methods for accessing a specified
    directory and the files its contains.


    Attributes
    ----------
    file_names : List[str]
        All file_names in the directory.

    path : Path
        The path of the directory, including the directory's name.


    Methods
    -------
    get_file_names_by_string(string: str) -> List[str]:
        Returns file names in the directory that contain the given string.

    """

    def __init__(self, path: str):
        """
        Constructor.

        Initializes the Directory class with a given path.

        Parameters
        ----------
        path : str
            The directory's path as a string.

        """

        self._file_names: List[str] | None = None
        self._path = Path(path)

    # region --- Properties

    @property
    def path(self) \
            -> Path:
        """
        Gets the path of the directory, including the directory's name.

        Returns
        -------
        Path
            The directory's path.

        """

        return self._path

    @path.setter
    def path(self, path: Path) \
            -> None:
        """
        Sets the path of the directory, including the directory's name.
        """

        self._path = Path(path)

    @property
    def file_names(self) \
            -> List[str]:
        """
        Returns all file_names in the directory.

        Returns
        -------
        List[str]
            A list of all file names in the directory.

        """

        if not self._file_names:
            self.__set_file_names()

        assert isinstance(self._file_names, list)

        return self._file_names

    @file_names.setter
    def file_names(self, file_names: List[str]) \
            -> None:
        """
        Sets the file_names in the directory.

        Parameters
        ----------
        List[str]
            The list of file names.

        """

        self._file_names = file_names

    # endregion --- Properties

    # region --- Public Methods
    def get_file_names_by_string(self, string: str) \
            -> List[str]:
        """
        Returns file names in the directory that contain the given string.

        Parameters
        ----------
        string : str
            The string the file names must contain.

        Returns
        -------
        List[str]
            A list of file names that contain the specified string.

        """

        selected_file_names = []
        for file_name in self.file_names:
            if string in file_name:
                selected_file_names.append(file_name)

        return selected_file_names

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods

    # region --- Private Methods

    @requires_property('path')
    def __set_file_names(self) \
            -> None:
        """
        Retrieves the file names from the path to set the file_names property.

        Ensures that the directory's path is set, retrieves the file names
        from it and sets the file_names property.

        """

        self.file_names = [
            file.name for file in self.path.iterdir() if file.is_file()
        ]

    # endregion --- Private Methods
