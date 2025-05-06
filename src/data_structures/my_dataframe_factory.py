"""
my_dataframe_factory.py
-----------------------
Version 1.0, updated on 2024-09-10

"""

from typing import Any

from src.data_structures.data_frame_factory import DataFrameFactory
from src.data_structures.my_data_frame import MyDataFrame
from src.sentiment_analysis.chunk import Chunk


class MyDataFrameFactory:
    """
    MyDataFrameFactory class.

    This class provides factory methods to create MyDataFrame instances and
    instances of MyDataFrame child classes like Chunk.

    Methods
    -------
    create(
            data: Any | None,
            col_names: list[str] | None=None,
            index_column: str = '',
            name: str | None = None
    ) -> MyDataFrame:
        Factory method to create a MyDataFrame instance.

    create_chunk(
            data: Any | None,
            col_names: list[str] | None=None,
            index_column: str = '',
            name: str | None = None
    ) -> Chunk:
        Factory method to create a Chunk instance.

    """

    @staticmethod
    def create(
            data: Any | None = None,
            col_names: list[str] | None = None,
            row_names: list[str] | None = None,
            index_column: str | None = None,
            name: str = ''
    ) -> MyDataFrame:
        """
        Factory method to create a MyDataFrame instance.

        This method calls the DataFrameFactory to create the DataFrame
        instance which is wrapped in the MyDataFrame class instance.

        Parameters
        ----------
        data : Any | None
            The data to populate the DataFrame. The specific type of this
            argument determines which implementation of the create_dataframe
            function is called.

        col_names : list[str] | None
            A list of column names for the DataFrame. If provided, it
            overrides the column names in the given data. Default is None.

        row_names : list[str] | None
            A list of row names for the DataFrame. Default is None.

        index_column : str | None
            The name of the column to set as the index of the DataFrame.
            Default is None.

        name : str
            The name for the DataFrame, used primarily for serialization
            purposes. Default is None.

        Returns
        -------
        MyDataFrame
            An instance of MyDataFrame populated with the provided data.

        """

        df = DataFrameFactory.create(data, col_names, row_names, index_column)

        return MyDataFrame(data=df, name=name)

    @staticmethod
    def create_chunk(
            data: Any | None = None,
            col_names: list[str] | None = None,
            row_names: list[str] | None = None,
            index_column: str | None = None,
            name: str = ''
    ) -> Chunk:
        """
        Factory method to create a Chunk instance.

        This method calls the DataFrameFactory to create the DataFrame
        instance which is wrapped in the Chunk class instance.

        Parameters
        ----------
        data : Any | None
            The data to populate the DataFrame. The specific type of this
            argument determines which implementation of the create_dataframe
            function is called.

        col_names : list[str] | None
            A list of column names for the DataFrame. If provided, it
            overrides the column names in the given data. Default is None.

        row_names : list[str] | None
            A list of row names for the DataFrame. Default is None.

        index_column : str | None
            The name of the column to set as the index of the DataFrame.
            Default is None.

        name : str
            The name for the DataFrame, used primarily for serialization
            purposes. Default is None.

        Returns
        -------
        Chunk
            An instance of Chunk populated with the provided data.

        """

        df = DataFrameFactory.create(data, col_names, row_names, index_column)

        return Chunk(data=df, name=name)
