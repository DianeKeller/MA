"""
data_frame_column_operations.py
-------------------------------
Version 1.0, updated on 2025-01-25

"""

from __future__ import annotations

from typing import List, Any, TYPE_CHECKING, Dict, cast
from natsort import natsorted

import numpy as np
import pandas as pd
from pandas import DataFrame

from src.data_structures.str_series import StrSeries
from src.data_structures.data_frame_operations import DataFrameOperations
from src.decorators.attribute_chain_decorators import (
    self_attribute_chain_not_none
)
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.late_imports import LateImports

if TYPE_CHECKING:
    from src.data_structures.my_data_frame import MyDataFrame
    from src.sentiment_analysis.chunk import Chunk


class DataFrameColumnOperations(DataFrameOperations):
    """
    DataFrameColumnOperations class.

    Provides column-specific operations for a MyDataFrame instance.

    This class extends DataFrameOperations to include methods that perform
    operations specifically on the columns of a MyDataFrame object. It
    allows for the addition, removal and modification of DataFrame columns.

    Inherited Parameters
    --------------------
    my_df : MyDataFrame
        An instance of MyDataFrame on which column operations will be
        performed. This parameter is inherited from the DataFrameOperations
        base class.

    Methods
    -------
    add_column(data: DataFrame | dict | list | None = None,
               col_name: str = '') -> None:
        Adds a new column to the DataFrame with the specified data.

    add_empty_bool_cols(col_names: list[str]) -> None:
        Adds empty boolean columns to the DataFrame.

    add_empty_float_cols(col_names: list[str]) -> None:
        Adds empty floating-point columns to the DataFrame in the
        MyDataFrame object.

    add_empty_int_cols(col_names: list[str]) -> None:
        Adds empty integer columns to the DataFrame wrapped in the
        MyDataFrame object.

    add_empty_str_cols(col_names: list[str]) -> None:
        Adds empty string columns to the DataFrame.

    are_cols_identical(col_name: str, other: MyDataFrame, other_col_name: str)
            -> bool:
        Checks if a column in other data is identical with the current data.

    drop_column(col_name: str) -> None:
        Removes a single column from the DataFrame.

    drop_columns(col_names: List[str]) -> None:
        Removes multiple columns from the DataFrame.

    extract_columns(col_names: List[str]) -> DataFrame:
        Extracts a DataFrame with the specified columns.

    extract_columns_by_name_substring(substring: str) -> DataFrame:
        Extracts the columns whose names contain the specified substring.

    find_identical_cols(other: DataFrame) -> List[str]:
        Finds columns in two DataFrames that have identical values in all rows.

    get_col_index_by_col_name(col_name: str) -> int:
        Returns the index of the specified column by its name.

    get_col_name_by_col_index(col_index: int) -> str:
        Returns the name of the column at the specified index.

    get_col_names_by_substring(substring: str) -> List[str]:
        Returns the column names that contain the given substring.

    get_col_type(col_name: str) -> np.dtype:
        Returns the data type of the specified column.

    def get_unique_values_by_col_name(col_name: str) -> List[Any]:
        Returns the unique values of a given column in the DataFrame.

    merge(other: MyDataFrame | DataFrame | Chunk) -> None:
        Adds the columns of another DataFrame to the current DataFrame.

    merge_transposed(other: MyDataFrame) -> None:
        Merges two transposed DataFrames.


    See Also
    --------
    DataFrameRowOperations
        Provides row-specific operations for a MyDataFrame instance.

    DataFrameFieldOperations
        Provides field-specific operations for a MyDataFrame instance.

    DataFrameOperations
        Base class providing common MyDataFrame operations.


    Examples
    --------
    >>> my_df_instance = MyDataFrame()
    >>> column_operations = DataFrameColumnOperations(my_df_instance)
    >>> column_operations.add_empty_int_cols(['age', 'year'])
    Adds empty integer columns named 'age' and 'year' to my_df_instance.

    """

    # region --- Public Methods

    def get_col_type(self, col_name: str) \
            -> np.dtype:
        """
        Returns the data type of the specified column.

        Parameters
        ----------
        col_name : str
            The name of the column whose data type is requested.

        Returns
        -------
        np.dtype
            The data type of the specified column.

        """

        return self.my_df.df[col_name].dtypes

    def get_col_index_by_col_name(self, col_name: str) \
            -> int:
        """
        Gets the index number of the specified column.

        Parameters
        ----------
        col_name : str
            The name of the column whose index number is requested.

        Returns
        -------
        int
            The index number of the row.

        Raises
        ------
        KeyError
            If the column name is not found in the dataframe.

        """

        if self.my_df.df is None:
            msg = "The dataframe is empty. Cannot get the index number."
            self._log(msg, 'error')
            raise KeyError(msg)

        if self.my_df.n_cols <= 0 or not self.my_df.col_names:
            msg = "The dataframe has no columns. Cannot get the index number."
            self._log(msg, 'error')
            raise KeyError(msg)

        # Check if there is a column with the column name provided.
        if col_name not in self.my_df.col_names:
            msg = (f"The dataframe has no column named '{col_name}' Cannot "
                   f"get the index number.")
            self._log(msg, 'error')
            raise KeyError(msg)

        return self.my_df.df.columns.get_loc(col_name)

    def get_unique_values_by_col_name(
            self,
            col_name: str
    ) -> List[Any]:
        """
        Returns the unique values of a given column in the dataframe.

        Parameters
        ----------
        col_name : str
            Name of the column whose values are to be extracted. The name
            equals the category to which the prompt parts or ingredients
            belong.

        Returns
        -------
        List[Any]
            List of unique elements of the given column in the data.

        """

        # Extract the column's values from the data, storing them
        # in a StrSeries object
        values = StrSeries(
            self.my_df.df[col_name],
            name=col_name
        )
        # Reduce the number of occurrences of each value to 1 per result set:
        unique_values = values.distinct_elements

        return unique_values


    def add_empty_int_cols(self, col_names: list[str]) \
            -> None:
        """
        Adds empty columns to the dataframe that are designed to hold integer
        values to the dataframe.

        Parameters
        ----------
        col_names : list[str]
            The names of the columns to add.

        Notes
        -----
        The pandas dtype used is 'Int64' instead of 'int' because Int64 is a
        nullable object, which allows for missing values in the dataframe,
        whereas int64 switches to float64 if a value is NaN.

        """

        for col_name in col_names:
            self.my_df.df[col_name] = pd.Series(dtype='Int64')

    def add_empty_float_cols(self, col_names: list[str]) \
            -> None:
        """
         Adds empty columns to the dataframe that are designed to hold
         floating-point numbers.

         Parameters
         ----------
         col_names : list[str]
             The names of the columns to add.

         Notes
         -----
         The pandas dtype used is 'Float64' instead of 'float64' to conform
         with the add_empty_int_cols method.

         """

        for col_name in col_names:
            # Uses 'Float64' instead of 'float64' to conform with the
            # according int method.
            # Since NaN types default to float64, the dtype could also be
            # float64 to hold future float values.

            self.my_df.df[col_name] = pd.Series(dtype='Float64')

    def add_empty_str_cols(self, col_names: list[str]) \
            -> None:
        """
        Adds empty columns to the dataframe that are designed to hold string
        values.

        Parameters
        ----------
        col_names : list[str]
            List of names of the columns to add.

        Notes
        -----
        The newer 'string' dtype is used instead of 'str', which pandas
        traditionally stores as an object. 'String' has better string
        handling features, such as support of missing values.

        """

        for col_name in col_names:
            self.my_df.df[col_name] = pd.Series(dtype='string')

    def add_empty_bool_cols(self, col_names: list[str]) \
            -> None:
        """
        Adds empty columns designed to hold boolean values to the
        dataframe.

        Parameters
        ----------
        col_names : list[str]
           The names of the columns to add.

        """

        for col_name in col_names:
            # Uses 'boolean' for nullable boolean support
            self.my_df.df[col_name] = pd.Series(dtype='boolean')

    def add_sums(
            self,
            col_name: str = 'Sum',
            sort: bool = False
    ) -> None:
        """
        Adds a sum column to the DataFrame.

        Parameters
        ----------
        col_name: str
            The name of the sum column. Default to 'Sum'

        sort: bool
            If True, the sum column is sorted in descending order. Defaults to
            False.

        Notes
        -----
        The DataFrame is modified in place.

        """

        # Add the sum column
        self.my_df.df[col_name] = self.my_df.df.sum(axis=1)

        if sort:
            # Reset index temporarily to treat the index as a column
            df_reset = self.my_df.df.reset_index()

            # Sort by 'Sum' (descending)
            df_reset = df_reset.sort_values(by=col_name, ascending=False)

            # Apply natural sorting to the 'index' within groups of the same 'Sum'

            sorted_indices = natsorted(
                df_reset['index'].tolist(),
                key=lambda x: (
                    0 if df_reset.loc[
                             df_reset['index'] == x,
                             col_name
                         ].values[0] >= 99 else 1,
                    -df_reset.loc[
                        df_reset['index'] == x,
                        col_name
                    ].values[0], x
                )
            )

            # Reorder the DataFrame using the sorted index
            df_reset = df_reset.set_index('index').loc[
                sorted_indices].reset_index()

            # Restore the index
            self.my_df.df = df_reset.set_index('index')


    def add_column(
            self,
            data: Any | None = None,
            col_name: str = ''
    ) -> None:
        """
        Add a column to the DataFrame.

        If the column comes in a DataFrame format, its indices are checked
        to ensure the column can be safely added to the DataFrame.

        Parameters
        ----------
        data : Any | None
            The column data to add to the DataFrame. Defaults to None.

        col_name: str
            The name of the new column. If it is not provided, the number of
            existing columns increased by 1 is appended to the string
            "Column_" to get a new column name. Default is None.

        Raises
        ------
        CriticalException
            If the index of the column and the index of the DataFrame are
            incompatible and cannot be merged.

        Notes
        -----
        - If data is not provided, the new column contains nothing but None
          values.

        - If 'data' is a data structure that can be mapped to the fields of
          the column like a DataFrame, a Series, a dictionary or a list, it
          is supposed to contain the different values of the fields in the new
          column. For this, its length must be the same as the number of rows
          in the DataFrame.

        - If 'data' is not a data structure that can be mapped to the fields
          of the column, all fields in the new column will be set to the
          value of 'data'.

        - if the column DataFrame and the current DataFrame have different
          indices, the indices are checked if they can be merged.

        """

        if not col_name:
            col_name = f"Column_{self.my_df.n_cols + 1}"
            msg = "Column name was not provided. Set to '%s'." % col_name
            self._log(msg, 'info')

        if data is None:
            data = [None] * self.my_df.df.index.size

        # If the new column comes as a DataFrame, verify that the indices
        # are compatible with the current DataFrame.
        if isinstance(data, DataFrame):
            if self._check_indices(data):
                self.my_df.df = pd.concat([self.my_df.df, data], axis=1)
            else:
                raise CriticalException(
                    self.logger,
                    (
                        "There is a problem with the original DataFrame's and "
                        "the new column's indices. Cannot merge them."
                    )
                )
        else:
            # Simply create the corresponding column in the DataFrame and
            # insert the data
            self.my_df.df[col_name] = data

    def are_cols_identical(
            self,
            col_name: str,
            other: MyDataFrame,
            other_col_name: str
    ) -> bool:
        """
        Checks if a column in other data is identical with the current data.

        Checks if the specified column in the current data and in the other
        data structure are identical.

        Parameters
        ----------
        col_name : str
            The name of the column in the current data.

        other : MyDataFrame
            The other data structure to compare with.

        other_col_name : str
            The name of the column in the other strategy.

        Returns
        -------
        bool
            True if the columns are identical, False otherwise.

        """

        return (
                self.my_df.df[col_name] == other.df[other_col_name]
        ).all()

    def assign_dtypes(self, col_type_map: Dict[str, type]) \
            -> None:
        """
        Assigns specified dtypes to the columns in the current DataFrame.

        Assignes the dtypes provided in the column type map to the
        DataFrame columns specified in the map.

        Parameters
        ----------
        col_type_map: Dict[str, type]
            A dictionary mapping column names to their respective data types
            (e.g., INT, FLOAT), where the keys are the column names and the
            values the dtypes to assign to the respective columns.

        Notes
        -----
        This method does not return the modified DataFrame. Instead The column
        types of the DataFrame are changed in place.

        """

        df = self.my_df.df

        for col, dtype in col_type_map.items():

            # Check if the column exists in the DataFrame
            if col in df.columns:
                # Cast the column to the specified data type
                df[col] = df[col].astype(dtype)

        self.my_df.df = df

    def merge(self, other: MyDataFrame | DataFrame | Chunk) \
            -> None:
        """
        Adds the columns of another DataFrame to the current DataFrame.

        This method adds the columns of the DataFrame in a data structure
        compatible to the current MyDataFrame (MyDataFrame, DataFrame,
        Chunk) to the columns of the DataFrame wrapped in the
        current MyDataFrame instance, aligning the rows based on their
        indexes.

        Parameters
        ----------
        other : MyDataFrame | DataFrame | Chunk
           The other data structure to merge with. The DataFrame in this
           data structure should have the same index structure as the
           calling MyDataFrame.

        Raises
        ------
        TypeError
           If the 'other' parameter is not an instance of MyDataFrame.

        Notes
        -----
        - If 'other' is a mere DataFrame, it is used to build a MyDataFrame
           object so that it can also be merged with the current MyDataFrame.

        - The merge is done using pandas' 'merge' function with 'left_index'
         and 'right_index' set to True, performing a SQL-like left join.

        - If there are overlapping columns, the values from the other
         MyDataFrame will be used.

        - The merged DataFrame replaces the current DataFrame in this
         MyDataFrame instance.

        """

        if isinstance(other, DataFrame):
            # Prevent circular imports
            my_dataframe_factory_cls = (
                LateImports.get_my_dataframe_factory_class()
            )

            other = my_dataframe_factory_cls().create(other)

        # Prevent circular imports
        my_data_frame_cls = LateImports.get_my_dataframe_class()

        if not isinstance(other, my_data_frame_cls):
            msg = "Merge needs another MyDataFrame. Got %s" % type(other)
            self._log(msg, 'error')
            raise TypeError(msg)

        self.my_df.data = pd.merge(
            self.my_df.data,
            cast(my_data_frame_cls, other).data,
            on=None,
            how='inner',
            validate='many_to_many',
            left_index=True,
            right_index=True
        )

    @self_attribute_chain_not_none('my_df.data')
    def merge_transposed(self, other: MyDataFrame) \
            -> None:
        """
        Merges two transposed DataFrames.

        Merges the current MyDataFrame with another MyDataFrame switching
        their rows to columns.
        The columns of the other DataFrame are added to the columns of the
        DataFrame wrapped in the current MyDataFrame instance.

        Parameters
        ----------
        other : MyDataFrame
           The other MyDataFrame to merge with. This MyDataFrame should
           have the same index structure as the calling MyDataFrame.

        Raises
        ------
        TypeError
           If the 'other' parameter is not an instance of MyDataFrame.

        Notes
        -----
        - The merge is done using pandas' 'merge' function with 'left_index'
         and 'right_index' set to True, performing a SQL-like left join.

        - If there are overlapping columns, the values from the other
         MyDataFrame will be used.

        - The merged DataFrame replaces the current DataFrame in this
         MyDataFrame instance.

        - Re-transposing the result of the merge would equal to adding the
          rows of the other DataFrame to the rows of the current original
          DataFrame.

        """

        if not isinstance(other, MyDataFrame):
            raise TypeError(f"Merge_transposed needs another MyDataFrame. "
                            f"Got {type(other)}")

        # Use default 'on', 'how' and 'validate' parameters
        self.my_df.data = pd.merge(
            self.my_df.data.T,
            other.data.T,
            on=None,
            how='inner',
            validate='many_to_many',
            left_index=True,
            right_index=True
        )

    def find_identical_cols(self, other: DataFrame) \
            -> List[str]:
        """
        Finds columns in two DataFrames that have identical values in all rows.

        Returns
        -------
        List[str]
            A list of the names of the columns that have identical values
            in all rows.

        """

        df1 = self.my_df.df
        df2 = other

        return df1.columns[df1.eq(df2).all()]

    def drop_column(self, col_name: str) \
            -> None:
        """
        Removes single column from dataframe.

        Parameters
        ----------
        col_name: str
            The name of the column to remove.

        """
        self.my_df.df.drop(columns=[col_name], inplace=True)

    def drop_columns(self, col_names: List[str]) \
            -> None:
        """
        Removes several columns from dataframe.

        Parameters
        ----------
        col_names: List[str]
            List of names of the columns to remove.

        """

        df = self.my_df.df
        self.my_df.df = df.drop(columns=col_names)

    def extract_columns(self, col_names: List[str]) \
            -> DataFrame:
        """
        Extracts a DataFrame with the specified columns.

        Extracts a DataFrame with the specified columns from the current
        MyDataFrame.

        Parameters
        ----------
        col_names : List[str]
            The names of the columns to extract.

        Returns
        -------
        DataFrame
            A DataFrame with the specified columns.

        """

        return self.my_df.df[col_names]

    def extract_columns_by_name_substring(self, substring: str) \
            -> DataFrame:
        """
        Extracts the columns whose names contain the specified substring.

        Extracts a DataFrame with the columns from the current MyDataFrame
        whose names contain the specified substring.

        Parameters
        ----------
        substring : str
            The substring the column names need to contain for the column to
            be extracted.

        Returns
        -------
        DataFrame
            A DataFrame with the extracted columns.

        """

        return self.extract_columns(self.get_col_names_by_substring(substring))

    def get_col_name_by_col_index(self, col_index: int) \
            -> str:
        """
        Returns the name of the column at the specified index.

        Parameters
        ----------
        col_index : int
            The index of the column to get the name of.

        Returns
        -------
        str
            The name of the column at the specified index.

        """

        return self.my_df.df.columns[col_index]

    def get_col_names_by_substring(self, substring: str) \
            -> List[str]:
        """
        Returns the column names that contain the given substring.

        Returns the column names from the current MyDataFrame that contain the
        given substring.

        Parameters
        ----------
        substring : str
            The substring the returned column names must contain.

        Returns
        -------
        List[str]
            The list of column names from the current MyDataFrame that contain
            the substring.

        """

        return [col for col in self.my_df.df.columns if substring in col]

    # endregion --- Public Methods

    # region --- Protected Methods

    def _check_indices(self, other: DataFrame) \
            -> bool:
        """
        Checks if the indices of the two DataFrames are compatible.

        Checks if the two DataFrames have the same indices or if they are
        safe to be merged.

        Parameters
        ----------
        other : DataFrame
            The other DataFrame to compare with.

        Returns
        -------
        bool
            True if the two DataFrames have the same index, False otherwise.

        Raises
        ------
        CriticalException
            If the two DataFrames have incompatible indices:

            - same number of indices but different names
            - different number of indices but no intersection of indices.

        """

        return self.my_df.do_with_row("check_indices", other=other)

    # endregion --- Protected Methods
