"""
pkl_strategy.py
---------------
Version 1.0, updated on 2025-05-01

"""

import pandas as pd
from pandas import DataFrame

from settings import SettingCategories
from src.data_structures.my_data_frame import MyDataFrame
from src.serialization.file import File
from src.serialization.serialization_strategy import SerializationStrategy


class PklStrategy(SerializationStrategy):
    """
    PklStrategy.

    This class is a concrete implementation of the SerializationStrategy
    interface for handling PKL (pickle) files. This strategy is used for the
    serialization and deserialization of pandas DataFrames to and from the
    pickle format.

    Using the pickle file format to serialize and deserialize large dataframes
    offers significantly better performance compared to the csv format. Note
    that unlike csv, pickle files are binary and, therefore, cannot be
    opened or read with a text editor.

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
        the pickle file to be serialized or deserialized.


    Methods
    -------
    _add(data: DataFrame | MyDataFrame) -> None:
        Saves data to an existing PKL file. If a MyDataFrame object is
        given, the dataframe inside the MyDataFrame is added to the PKL file.

    _load() -> DataFrame:
        Deserializes and loads data from a PKL file into a DataFrame. If
        the file does not exist, returns None.

    _save(data: DataFrame | MyDataFrame) -> None:
        Serializes and saves a DataFrame to a PKL file. If a MyDataFrame object
        is given, the dataframe inside the MyDataFrame is saved.



    Notes
    -----
    - The path where the pickle file is saved or loaded from is determined by
      settings specific to the PKL strategy.

    - Deserialize pickle files only if you have serialized them yourself or
      if they come from a trusted source, as pickle files can contain
      executable code that may be malicious.

    """

    DATA_STRUCTURE = "DataFrame"
    FILE_TYPE = "PKL"

    def __init__(
            self,
            file: File | None = None
    ) -> None:
        """
        Initializes a new instance of the PklStrategy class.

        Sets the file path to use, retrieving it from the application settings.

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

        if self.file is not None:
            self.set_file_path(SettingCategories.PKL)

    def _save(self, data: DataFrame | MyDataFrame) \
            -> None:
        """
        Attempts to save the given data to a PKL (pickle) file.

        Parameters
        ----------
        data : DataFrame | MyDataFrame
            The data to be serialized and saved to a PKL file.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        df = data.df if isinstance(data, MyDataFrame) else data

        df.to_pickle(self.file.full_path)

    def _add(self, data: DataFrame | MyDataFrame) \
            -> None:
        """
        Attempts to add the given dataframe to an existing file.

        Parameters
        ----------
        data : DataFrame | MyDataFrame
            The DataFrame to be serialized and saved to a file.

        """

        raise NotImplementedError

    def _load(self) \
            -> DataFrame | None:
        """
        Attempts to load data from a PKL (pickle) file into a DataFrame.

        Returns
        -------
        DataFrame | None
            The deserialized DataFrame if the file exists; otherwise, None.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        return pd.read_pickle(self.file.full_path)
