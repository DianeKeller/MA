"""
file.py
-------
Version 1.0, updated on 2025-05-01

"""

import os

from logger import Logger
from src.serialization.file_extension import FileExtension
from src.utils.data_utils import is_none_or_empty


class File:
    """
    File class.

    This class provides an object containing the details of a file.

    To initialize the File object, you need to specify the file's name and
    extension.

    Attributes
    ----------
    file_name : str
        The name of the file without its extension and path.

    extension : FileExtension
        The extension of the file (an enum value from a list of possible
        extensions).

    path : str
        The absolute path to the file. In contrast to the full_path, the path
        does not include the file's name and extension.

    full_path : str
        The full absolute path of the file, consisting of the path property
        value and the file's name and extension.

    Notes
    -----
    The path, defined as the directory's absolute path containing the file, is
    not initially set to allow for dynamic assignment based on varying
    conditions. Once the path is established, the object offers a method to
    retrieve the complete file path, incorporating both the file name and its
    extension.

    Implementation Details
    ----------------------
    The class uses a logger for logging warnings and errors related to file
    path operations.

    """

    def __init__(
            self,
            file_name: str,
            extension: FileExtension
    ) -> None:
        """
        Constructor.

        Initializes the File with the given parameters.

        Parameters
        ----------
        file_name : str
            The name of the file without its extension and path.

        extension : FileExtension
            The extension of the file as an enum value from the list of
            possible extensions enumerated in the FileExtension class).

        """

        self.__full_path: str = ''
        self.__path: str = ''
        self.__file_name: str = ''
        self.__extension: FileExtension = extension

        # Set the file name using the setter to ensure the validity of the
        # name.
        self.file_name = file_name

        self.logger = Logger(self.__class__.__name__).get_logger()

    # region --- Properties

    @property
    def file_name(self) \
            -> str:
        """
        Gets the name of the file.
        """

        return self.__file_name

    @file_name.setter
    def file_name(self, file_name: str) \
            -> None:
        """
        Sets the file name and resets the full path property.

        Parameters
        ----------
        file_name : str
            The name of the file, without the extension.

        Notes
        -----
        - If the file name contains the extension that isset in the extension
          property, it is removed from the file name, so that duplicate file
          extensions, e.g. '.txt.txt', cannot occur.

        - Different file extensions in a file name are allowed, however,
          e.g., '.csv.txt', making it possible to indicate with the file
          name that the file originally had another format and is now saved
          in a new format.

        - The full path property is reset to an empty string, in order to
          allow for dynamic assignment based on varying conditions.

        """

        file_name = self._remove_extension(file_name)

        self.__file_name = file_name
        self.__full_path = ''

    @property
    def extension(self) \
            -> FileExtension:
        """
        Returns the extension of the file.
        """

        return self.__extension

    @extension.setter
    def extension(self, extension: FileExtension) \
            -> None:
        """
        Sets the extension of the file

        Parameters
        ----------
        extension : FileExtension
            The file extension to use.

        """

        self.__extension = extension

    @property
    def path(self) \
            -> str:
        """
        Returns the path of the file.

        Returns
        -------
        self.__path : str
            The path of the file

        Notes
        -----
        The path might not be set, so that this getter might return an
        empty string. It is up to the calling method to check if the return
        value is valid.

        """
        return self.__path

    @path.setter
    def path(self, path: str) \
            -> None:
        """
        Sets the path of the file.

        If the path is set anew, the full_path property is reset so that it
        gets recomposed the next time the full path is requested.

        Parameters
        ----------
        path : str

        """

        self.__path = path
        self.__full_path = ''

    @property
    def full_path(self) \
            -> str:
        """
        Returns the full path of the file.

        The full path consists of the path, the file's name
        and extension.

        Returns
        -------
        self.__full_path : str
            The full path of the file

        Notes
        -----
        If the __compose_full_path method fails, this getter will fail
        gracefully, returning None. The calling method will have to check
        whether the full path returned actually has a value.

        """

        if is_none_or_empty(self.__full_path):
            self.__compose_full_path()
        return self.__full_path

    @full_path.setter
    def full_path(self, full_path: str) \
            -> None:
        """
        Sets the full path of the file.
        """

        self.__full_path = full_path

    # endregion --- Properties

    # region --- Protected Methods

    def _remove_extension(self, file_name: str) \
            -> str:
        """
        Removes the defined extension from the file name.

        Removes the extension defined in the extension property from the
        file name.

        Parameters
        ----------
        file_name : str
            The name of the file.

        Returns
        -------
        str
            The name of the file without the extension.

        Notes
        -----
        If the extension is an empty string, the file name is
        returned unchanged.

        """

        extension = str(self.extension.value)

        if len(extension) > 0 and file_name.endswith(extension):
            # Do not execute this with an empty extension string!
            # It would make the method return an empty string.
            file_name = file_name[:-len(extension)]

        return file_name

    # endregion --- Protected Methods

    # region --- Private Methods

    def __compose_full_path(self) \
            -> None:
        """
        Composes the file's absolute path.

        Composes and sets the full path from the file's directory, file name
        and extension, provided that the path property is set. This is a
        private method that should not be called from outside this class.

        """

        if is_none_or_empty(self.__path):
            self.logger.warning(
                "Full path requested but no path given. File: %s, "
                "extension: %s.",
                self.file_name, self.extension
            )
            return

        file_extension = self.extension.value \
            if hasattr(self.extension, "value") \
            else str(self.extension)

        self.full_path = os.path.join(
            self.path,
            f"{self.file_name}{file_extension}"
        )

    # endregion --- Private Methods
