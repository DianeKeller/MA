"""
json_strategy.py
------------------------
Version 1.0, updated on 2025-05-01

"""

import json
from typing import Dict, List, Any

from pandas import DataFrame

from settings import SettingCategories
from src.serialization.file import File
from src.serialization.serialization_strategy import SerializationStrategy
from type_aliases import Serializable


class JsonlStrategy(SerializationStrategy):
    """
    This class is a concrete implementation of the SerializationStrategy
    interface for handling JSON Lines files. It is used for the serialization
    and deserialization of dictionaries to and from JSON Lines format.

    Attributes
    ----------
    file : File | None
        Inherited from the SerializationStrategy interface. Represents
        the JSON Lines file to be serialized or deserialized.

    Methods
    -------
    _add(data: Serializable) -> None:
        Saves data to an existing file.

    _load() -> DataFrame | str | Dict | List[List[Any]] | None:
        Deserializes and loads data from a JSON Lines file into a complex data
        structure. If the file does not exist, returns None.

    _save(data: Serializable) -> None:
        Serializes and saves a dictionary to a JSON Lines file.

    """

    DATA_STRUCTURE = "dictionary"
    FILE_TYPE = "JSONL"

    def __init__(
            self,
            file: File | None = None
    ) -> None:
        """
        Initializes a new instance of the CsvStrategy class.

        Sets the file path to use, retrieving it from the application settings.

        Parameters
        ----------
        file : File | None
            Custom 'File' object used for saving or loading data or removing a
            file from the file system. The 'File' object holds
            attributes detailing the name and extension of the file which
            is concerned by the intended file operations. If not provided,
            operations will require a file to be set later, including its
            path property.

        Notes
        -----
        To initialize the serialization strategy, the serialization factory
        method 'get_serialization_strategy' should be used. It ensures that
        the file parameter is not None.

        """

        super().__init__(file)

        if self.file is not None:
            self.set_file_path(SettingCategories.JSONL)

    def _save(self, data: Serializable) \
            -> None:
        """
        Attempts to save the given dictionary to a JSON Lines file.

        Parameters
        ----------
        data : Serializable
            The dictionary to be serialized and saved to a JSON Lines file.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        with open(
            self.file.full_path,
            'w',
            encoding='utf_8'
        ) as fp:
            json.dump(data, fp)

    def _add(self, data: Serializable) \
            -> None:
        """
        Attempts to add the given data to an existing file.

        Parameters
        ----------
        data : Serializable
            The dictionary to be serialized and saved to a JSON Lines file.

        """

        raise NotImplementedError

    def _load(self) \
            -> DataFrame | str | Dict | List[List[Any]] | None:
        """
        Attempts to load data from a JSON file into a complex data structure.

        Logs the attempt and re-raises any exceptions encountered to allow
        for error handling by the serializer.

        Returns
        -------
        DataFrame | str | Dict | List[List[Any]] | None
            The loaded data if the file exists; otherwise, None.

        Raises
        ------
        CriticalException
            If the file is not set.

        Exception
            For any error that occurs during the load operation.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        with open(
            self.file.full_path,
            'r',
            encoding='utf_8'
        ) as file:
            data = DataFrame([json.loads(line)
                              for line in file.read().splitlines()])

        return data
