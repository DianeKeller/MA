"""
serialization_strategy.py
-------------------------
Version 1.0, updated on 2025-05-01

"""

import os
from abc import ABC, abstractmethod
from typing import no_type_check

from logger import Logger
from settings import SettingCategories, get_setting

from src.decorators.error_handling_decorators import (
    delete_error_handling,
    save_error_handling, load_error_handling
)
from src.decorators.object_checking_decorators import (
    requires_file,
    requires_data
)
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.serialization.file import File
from src.utils.data_utils import is_none_or_empty

from type_aliases import Serializable


class SerializationStrategy(ABC, LoggingMixin):
    """
    SerializationStrategy class.

    Abstract base class for all serialization strategies.

    This class serves as an interface that declares common operations
    for all supported file serialization strategies. Specifically,
    it defines the essential operations for saving, loading and deleting 
    data, which concrete strategies must implement. Within the framework of
    a strategy pattern, this design enables a dynamic change of serialization
    strategies according to the varying requirements of different data
    structures and file formats.


    Attributes 
    ---------- 
    DATA_STRUCTURE : str
        A string constant representing the data structure type, to be used
        in logging messages

    FILE_TYPE : str
        A string constant representing the file type, to be used in logging
        messages

    file : File | None
        The 'File' object to be serialized or deserialized.

    logger : Logger
        Overrides the default logger of the 'LoggingMixin' class.


    Methods
    -------
    add(data: Serializable) -> None:
        Saves data to an existing file.

    delete() -> str:
        Attempts to delete the file associated with this strategy.

    does_path_exist() -> bool:
        Checks if the path of the file associated with this strategy exists.

    load() -> Serializable | None:
        Loads and returns data from a file.

    save(data: Serializable) -> None:
        Saves data to a file.

    set_file_path(category: SettingCategories) -> None:
        Sets the file path.


    Abstract Methods
    ----------------
    _add(data: Serializable) -> None:
        Actual data adding logic, to be implemented by subclasses.

    _load() -> Serializable | None:
        Actual data loading logic, to be implemented by subclasses.

    _save(data: Serializable) -> None:
        Actual data saving logic, to be implemented by subclasses.




    Properties
    ----------
    file : File
        Gets or sets the 'File' object associated with this strategy. The
        'File' object contains details about the file name and extension,
        which are used in save, load and delete operations.

    Notes
    -----
    - Concrete strategy implementations must provide specific serialization
      and deserialization logic by overriding the 'save' and 'load' methods.

    - It is the responsibility of the concrete strategy to handle cases where
      'File' is not provided before an operation is attempted.

    - As the deletion of files works the same for all file formats,
      the deletion method provided here is specific so that the implementing
      strategies are spared the trouble of defining their own deletion methods.

    """

    # The following class constants should be overridden by the subclasses:

    # The data structure type, to be used in logging messages
    DATA_STRUCTURE: str = "Any data structure"

    # The file type, to be used in logging messages
    FILE_TYPE: str = "Any file type"

    def __init__(
            self,
            file: File | None = None
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the SerializationStrategy class.

        Parameters
        ----------
        file : File | None
            Custom 'File' object used for saving or loading data or
            for removing a file from the file system. The 'File' object
            contains attributes detailing the name and extension of the file
            involved in the intended file operations. If not provided,
            the concrete strategy implementations must ensure that a 'File'
            object is provided before attempting any file operation.

            In cases where a concrete serialization strategy involves
            storing data across several files, 'file' represents the directory
            where these files are located. Additionally, the file extension
            specified in the object indicates the file extension used by the
            files in the directory.

        """

        self.__file: File | None = file

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    # region --- Properties

    @property
    def file(self) \
            -> File | None:
        """
        Gets the 'File' object to be serialized or deserialized.

        Returns
        -------
        File
            The 'File' object with which the specific serialisation strategy
            is concerned.

        Notes
        -----
        As the 'File' object might not have been provided at the moment of
        the initialization of the class, it might have defaulted to None.
        Therefore, this method might return None.

        """

        return self.__file

    @file.setter
    def file(self, file: File) \
            -> None:
        """
        Sets the 'File' object to be serialized or deserialized.

        Parameters
        ----------
        file : File
            The 'File' object detailing the name and extension of the file
            to be operated on.

        """

        self.__file = file

    # endregion --- Properties

    # region --- Methods

    @requires_file
    def set_file_path(self, category: SettingCategories) \
            -> None:
        """
        Sets the file path.

        Sets the file path getting it from the settings corresponding to the
        settings category defined in the concrete serialization strategy.

        Parameters
        ----------
        category : SettingCategories
            The category of the settings corresponding to the serialization
            strategy used.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        self.file.path = str(get_setting(category, 'PATH'))

    @no_type_check
    @requires_file
    def does_path_exist(self) \
            -> bool:
        """
        Checks if the path of the file associated with this strategy exists.

        Returns
        -------
        bool
            True if the file path exists, False otherwise.

        """

        return os.path.exists(self.file.full_path)

    @requires_file
    @requires_data
    @save_error_handling
    def save(self, data: Serializable) \
            -> None:
        """
        Saves data to a file.

        Calls the abstract _save method, which must be implemented by each
        concrete strategy. Logs the attempt and re-raises any exceptions of the
        concrete strategy class.

        Parameters
        ----------
        data : Serializable
            The content to be saved. The type of this parameter depends on
            the format of the data and the serialization strategy chosen
            and has to be fixed by the concrete implementation.

        Raises
        ------
        Exception
            For any error that occurs during the save operation.

        """

        try:
            self._log_info_before_saving()
            self._save(data)
            self._log_info_after_saving()

        except Exception as err:
            self._log_error_after_saving(err)
            raise

    @requires_file
    @requires_data
    @save_error_handling
    def add(self, data: Serializable) \
            -> None:
        """
        Saves data to an existing file.

        Calls the abstract _add method, which must be implemented by each
        concrete strategy. Logs the attempt and re-raises any exceptions of the
        concrete strategy class.

        Parameters
        ----------
        data : Serializable
            The content to be added. The type of this parameter depends on
            the format of the data and the serialization strategy chosen
            and has to be fixed by the concrete implementation.

        Raises
        ------
        Exception
            For any error that occurs during the save operation.

        """

        try:
            self._log_info_before_saving()
            self._add(data)
            self._log_info_after_saving()

        except Exception as err:
            self._log_error_after_saving(err)
            raise

    @requires_file
    @load_error_handling
    def load(self) \
            -> Serializable | None:
        """
        Loads data from a file.

        Calls the abstract _load method, which must be implemented by each
        concrete strategy. Logs the attempt and re-raises any exceptions of the
        concrete strategy class.

        Returns
        -------
        Serializable | None
            The data extracted from the file. The type of this parameter
            depends on the format of the data and the (de-)serialization
            strategy chosen and has to be fixed by the concrete implementation.

        """

        try:
            self._log_info_before_loading()
            data = self._load()
            self._log_info_after_loading()

            if is_none_or_empty(data):
                raise CriticalException(
                    self.logger,
                    "No data loaded!"
                )

            return data

        except Exception as err:
            self._log_error_after_loading(err)
            raise

    @delete_error_handling
    def delete(self) \
            -> None:
        """
        Attempts to delete the file associated with this strategy.

        Attempts to delete the file with which this strategy is concerned
        from the filesystem. Logs the attempt and re-raises any exceptions
        encountered to allow for error handling by the serializer.

        Raises
        ------
        Exception
            For any error that occurs during the delete operation.

        """

        if not self.file or not self.file.path:
            raise CriticalException(self.logger, "File or path is missing.")

        if not self.file.full_path:
            raise CriticalException(self.logger, "Full path is missing.")

        msg = "Deleting file %s" % self.file.full_path
        self._log(msg, 'info')

        os.remove(self.file.full_path)

        msg = "File %s deleted!" % self.file.full_path
        self._log(msg, 'info')

    # endregion --- Methods

    # region --- Abstract Methods

    @abstractmethod
    def _save(self, data: Serializable) \
            -> None:
        """
        Actual data saving logic, to be implemented by subclasses.

        Parameters
        ----------
        data : Serializable
            The content to be saved. The type of this parameter depends on
            the format of the data and the serialization strategy chosen
            and has to be fixed by the concrete implementation.

        """

    @abstractmethod
    def _add(self, data: Serializable) \
            -> None:
        """
        Actual data adding logic, to be implemented by subclasses.

        Parameters
        ----------
        data : Serializable
            The content to be saved. The type of this parameter depends on
            the format of the data and the serialization strategy chosen
            and has to be fixed by the concrete implementation.

        """

    @abstractmethod
    def _load(self) \
            -> Serializable | None:
        """
        Actual data loading logic, to be implemented by subclasses.

        Returns
        -------
        Serializable | None
            The data extracted from the file. The type of this parameter
            depends on the format of the data and the (de-)serialization
            strategy chosen and has to be fixed by the concrete implementation.

        """

    # endregion --- Abstract Methods

    # region --- Protected Methods

    @no_type_check
    @requires_file
    def _log_info_before_saving(self):
        msg = (f"Saving {self.DATA_STRUCTURE} to"
               f" {self.FILE_TYPE} file"
               f" {self.file.full_path}.")
        self._log(msg, 'info', 'log_info_before_saving')

    def _log_info_after_saving(self):
        msg = (f"{self.DATA_STRUCTURE.capitalize()} saved "
               "successfully.")
        self._log(msg, 'info', 'log_info_after_saving')

    def _log_error_after_saving(self, err):
        msg = (f"{self.DATA_STRUCTURE.capitalize()} could "
               f"not be saved. Error: {err}")
        self._log(msg, 'error')

    @no_type_check
    @requires_file
    def _log_info_before_loading(self):
        msg = (f"Loading {self.DATA_STRUCTURE} from"
               f" {self.FILE_TYPE} file"
               f" {self.file.full_path}.")
        self._log(msg, 'info')

    def _log_info_after_loading(self):
        msg = (f"{self.DATA_STRUCTURE.capitalize()} loaded "
               "successfully.")
        self._log(msg, 'info')

    def _log_error_after_loading(self, err):
        msg = (f"{self.DATA_STRUCTURE.capitalize()} could "
               f"not be loaded. Error: {err}")
        self._log(msg, 'error')

    # endregion  --- ProtectedMethods
