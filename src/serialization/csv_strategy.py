"""
csv_strategy.py
---------------
Version 1.0, updated on 2025-05-01

"""

import pandas as pd
from pandas import DataFrame

from settings import get_setting, SettingCategories
from src.serialization.file import File
from src.serialization.serialization_strategy import SerializationStrategy


class CsvStrategy(SerializationStrategy):
    """
    This class is a concrete implementation of the SerializationStrategy
    interface for handling CSV files. It is used for the serialization and
    deserialization of pandas DataFrames to and from CSV format.

    Attributes
    ----------
    DATA_STRUCTURE : str
        The data structure type this strategy can serialize and
        deserialize.

    FILE_TYPE : str
        The file type this strategy uses to serialize and deserialize data.
        This string is used in log messages.

    file : File | None
        Inherited from the SerializationStrategy interface. Represents
        the CSV file to be serialized or deserialized.

    separator : str
        The delimiter to use in the CSV file. This is configurable through
        settings.


    Methods
    -------
    _add(data: DataFrame) -> None:
        Saves data to an existing file.

    _load() -> DataFrame:
        Deserializes and loads data from a CSV file into a DataFrame. If
        the file does not exist, returns None.

    _save(data: DataFrame) -> None:
        Serializes and saves a DataFrame to a CSV file.


    Notes
    -----
    - The path where the CSV file is saved or loaded from is determined by
      settings specific to the CSV strategy.

    - The separator used in the CSV file can also be configured through
      settings, allowing for flexibility in handling different CSV formats.

    """

    DATA_STRUCTURE = "DataFrame"
    FILE_TYPE = "CSV"

    def __init__(
            self,
            file: File | None = None
    ) -> None:
        """
        Initializes a new instance of the CsvStrategy class.

        Sets the file path and the separator to use, retrieving them from the
        application settings.

        Parameters
        ----------
        file : File | None
            Custom 'File' object used for saving or loading data or removing a
            file from the file system. The 'File' object holds
            attributes detailing the name and extension of the file which
            is concerned by the intended file operations. If not provided,
            operations will require a file to be set later.

        """

        super().__init__(file)

        self.__separator = ''

        if self.file is not None:
            self.set_file_path(SettingCategories.CSV)

        self.separator = str(get_setting(
            SettingCategories.CSV, 'SEPARATOR')
        )

    @property
    def separator(self) \
            -> str:
        """
        Gets the separator to be used in the CSV file.

        Returns
        -------
        str
           The delimiter to use in the CSV file.

        """

        return self.__separator

    @separator.setter
    def separator(self, separator: str) -> None:
        """
        Sets the separator to be used in the CSV file.

        Parameters
        ----------
        separator : str
           The delimiter to use in the CSV file.

        """

        self.__separator = separator

    def _save(self, data: DataFrame) \
            -> None:
        """
        Attempts to save the given dataframe to a CSV file.

        Parameters
        ----------
        data : DataFrame
            The DataFrame to be serialized and saved to a CSV file.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        data.to_csv(
            self.file.full_path,
            sep=self.separator,
            index=False,
            mode='w',
            header=True
        )

    def _add(self, data: DataFrame) \
            -> None:
        """
        Attempts to add the given dataframe to an existing CSV file.

        Parameters
        ----------
        data : DataFrame
            The DataFrame to be serialized and saved to a CSV file.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        data.to_csv(
            self.file.full_path,
            sep=self.separator,
            index=False,
            mode='a',
            header=False

        )

    def _load(self) \
            -> DataFrame | None:
        """
        Attempts to load data from a CSV file into a DataFrame.

        Returns
        -------
        DataFrame | None
            The deserialized DataFrame if the file exists; otherwise, None.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        return pd.read_csv(
            self.file.full_path,
            sep=self.separator
        )
