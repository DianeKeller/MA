"""
serializer.py
-------------
Version 1.0, updated on 2025-05-01

"""

import os
from typing import List, Any

from logger import Logger
from src.decorators.error_handling_decorators import (
    save_error_handling,
    load_error_handling,
    delete_error_handling
)
from src.logging_mixin import LoggingMixin
from src.serialization.csv_strategy import CsvStrategy
from src.serialization.file import File
from src.serialization.serialization_strategy import SerializationStrategy
from type_aliases import Serializable


class Serializer(LoggingMixin):
    """
    This class serves as the context in a strategy pattern, which allows you to
    dynamically choose a serialization strategy at runtime.

    The class works with any of the serialization strategies that implement the
    SerializationStrategy interface. It gives access to the
    serialization methods such as saving, loading and deleting data
    of the given serialization strategy.

    Attributes
    ----------
    file : File | None
        The 'File' object.

    logger : Logger
        Overrides the default logger of the 'LoggingMixin' class.

    strategy : SerializationStrategy
        The current serialization strategy in use.

    Methods
    -------
    add_or_save(data: Serializable) -> None:
        Adds the data to an existing file or saves the data in a new file.

    default_strategy() -> SerializationStrategy:
        Static method to return the default serialization strategy.

    delete() -> None:
        Deletes a locally stored file using the current serialization strategy.

    does_path_exist() -> bool:
        Checks if the directory for the file exists.

    load() -> Serializable | List[List[Any]] | None:
        Attempts to load data from a locally stored file.

    save(data: Serializable) -> None:
        Attempts to save data using the current serialization strategy.

    """

    def __init__(self, my_strategy: SerializationStrategy | None = None) \
            -> None:
        """
        Constructor.

        Sets the serialization strategy which is supposed to be used for
        serialization operations. If no strategy is specified when the
        serializer is called, a default serialization strategy is used.

        Parameters
        ----------
        my_strategy : SerializationStrategy | None
            The serialization strategy to be used. Default value: None.

        """

        # Override the default logger of the 'LoggingMixin' class.
        self.logger: Logger = Logger(self.__class__.__name__).get_logger()

        self._strategy = my_strategy or self.default_strategy()

        self.__file = self.strategy.file
        self.__directory = self.__file.path

    # region --- Properties

    @property
    def strategy(self) -> SerializationStrategy:
        """
        Gets the current serialization strategy.

        Returns
        -------
        SerializationStrategy
            The serialization strategy currently in use.

        """

        return self._strategy

    @strategy.setter
    def strategy(self, strategy: SerializationStrategy) \
            -> None:
        """
        Sets the serialization strategy to be used.

        The strategy can be changed at runtime.

        Parameters
        ----------
        strategy : SerializationStrategy
            The serialization strategy to be used for serialization operations.

        """

        self._strategy = strategy

    @property
    def file(self) \
            -> File | None:
        """
        Gets the 'File' object.

        Returns
        -------
        File
            The 'File' object with which the specific serialisation strategy
            is concerned.

        Notes
        -----
        As the 'File' object might not have been provided at the moment of
        the initialization of the strategy, it might have defaulted to None.
        Therefore, this method might return None.

        """

        return self.__file

    # endregion --- Properties

    # region --- Methods

    def does_path_exist(self) \
            -> bool:
        """
        Checks if the directory for the file exists.

        Returns
        -------
        bool
            True if the directory exists, False otherwise.

        """

        return self.strategy.does_path_exist()

    @save_error_handling
    def save(self, data: Serializable) \
            -> None:
        """
        Attempts to save data using the current serialization strategy.

        Logs the attempt and any exceptions encountered in the process.

        Parameters
        ----------
        data : Serializable
            The data to be saved.

        Raises
        ------
        FileNotFoundError
            If the directory for the file does not exist or is invalid.

        PermissionError
            If there are insufficient permissions to open the file for writing.

        IsADirectoryError
            If the targeted file is a directory, not a file.

        Exception
            For any other unexpected errors.

        """
        strategy = self.strategy

        self._enforce_directory_path_exists()

        strategy.save(data)

    @save_error_handling
    def add_or_save(self, data: Serializable) \
            -> None:
        """
        Adds the data to an existing file or saves the data in a new file.

        Ensures the directory where the file is supposed to be stored exists
        by calling the _enforce_directory_path_exists method. Checks whether
        the file to save the data to exists already. If so, the data is
        added to the data existing in the file. Otherwise, a new file is
        created to save the data.

        Parameters
        ----------
        data : Serializable
            The data to save in a file.

        """

        strategy = self.strategy

        self._enforce_directory_path_exists()

        if os.path.exists(self.file.full_path):
            strategy.add(data)
        else:
            strategy.save(data)

    @load_error_handling
    def load(self) \
            -> Serializable | List[List[Any]] | None:
        """
        Attempts to load data from a locally stored file.

        Logs the attempt and any exceptions encountered in the process.
        Uses the current serialization strategy.

        Returns
        -------
        Serializable | List[List[Any]] | None
            The loaded data. Its concrete data type depends on the
            serialization strategy used.

        Raises
        ------
        FileNotFoundError
            If the targeted file does not exist.

        PermissionError
            If there are insufficient permissions to open the file for reading.

        IsADirectoryError
            If the targeted file is a directory, not a file.

        pd.errors.EmptyDataError
            If the targeted file is empty.

        pd.errors.ParserError
            If pandas fails to parse the content of the file.

        Exception
            For any other unexpected errors.

        """

        strategy = self.strategy

        return strategy.load()

    @delete_error_handling
    def delete(self) \
            -> None:
        """
        Deletes a locally stored file using the current serialization strategy.

        Returns
        -------
        str
            A message indicating success or failure of the deletion.

            A message indicating the outcome of the delete operation. If the
            file does not exist, a failure message is returned, otherwise,
            a success message.


        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        PermissionError
            If there are insufficient permissions to delete the file.
        IsADirectoryError
            If the path is a directory, not a file.
        OSError
            For other OS-related errors, such as the directory not being empty.
        Exception
            For any other unexpected errors.

        """

        self.strategy.delete()

    # endregion --- Methods

    # region --- Static Methods

    @staticmethod
    def default_strategy() \
            -> SerializationStrategy:
        """
        Returns the default serialization strategy.

        As default, the csv serialization strategy is used. The csv format
        should work for most data structures.

        Returns
        -------
        SerializationStrategy
            The csv serialization strategy.

        Notes
        -----
        This method is used instead of a class constant to ensure lazy
        instantiation. This approach avoids the overhead of creating a default
        strategy object until it is actually needed.

        """

        return CsvStrategy(None)

    # endregion --- StaticMethods

    # region --- Protected Methods

    def _enforce_directory_path_exists(self) \
            -> None:
        """
        Creates the directory if it does not exist yet.
        """

        if not os.path.exists(self.__directory):
            msg = f"Directory {self.__directory} does not exist."
            self._log(msg, 'info')

            os.makedirs(self.__directory)

            msg = f"Directory created: {self.__directory}"
            self._log(msg, 'info')

    # endregion --- Protected Methods
