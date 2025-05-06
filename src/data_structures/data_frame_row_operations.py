"""
data_frame_row_operations.py
----------------------------
Version 1.0, updated on 2024-12-28

"""

from __future__ import annotations

import operator
from typing import Any, Dict, List, Callable, cast
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from pandas import DataFrame, Series, Index

from src.data_structures.data_frame_factory import DataFrameFactory
from src.data_structures.data_frame_operations import DataFrameOperations
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException)
from src.utils.late_imports import LateImports
from src.utils.list_utils import is_flat, are_all_elements_included, is_subset
from type_aliases import DictOfLists

if TYPE_CHECKING:
    from src.data_structures.my_data_frame import MyDataFrame


class DataFrameRowOperations(DataFrameOperations):
    """
    DataFrameRowOperations class.

    Provides row-specific operations for a MyDataFrame instance.

    This class extends DataFrameOperations to include methods that perform
    operations specifically on the rows of a MyDataFrame object. It
    allows for adding, extracting, removing and shuffling rows in the
    contained DataFrame.

    Inherited Parameters
    --------------------
    my_df : MyDataFrame
        An instance of MyDataFrame on which row operations will be
        performed. This parameter is inherited from the DataFrameOperations
        base class.

    Methods
    -------
    add_empty_row() -> None:
        Adds an empty row to the DataFrame.

    add_rows(data: MyDataFrame | DataFrame | DictOfLists |
            List[List[int | float | str]] | List[Dict[str, int | float | str]]
            | List[int | float | str] | None = None,
            ignore_index: bool = True) -> None:
        Adds one or more rows with the given data to the DataFrame.

    check_indices(other: DataFrame) -> bool:
        Checks if the indices of the two DataFrames are compatible.

    drop_row_by_row_name(row_name: str) -> None:
        Drops a row from the DataFrame based on its row name.

    extract_rows_by_col_value(col_name: str, col_value: Any,
            op: Callable[[Any, Any], bool] = operator.eq -> DataFrame:
        Extracts rows where the specified column value fulfills a condition.

    extract_rows_by_other_indices(other: MyDataFrame) -> DataFrame:
        Extracts rows using the indices of another MyDataFrame.

    get_additional_row_indices(self, other: DataFrame) -> Index:
        Returns the additional row indices of the other DataFrame.

    get_missing_indices(self, other: DataFrame) -> Index:
        Returns the row indices that are missing in the other DataFrame.

    get_row_df_by_name(row_name: str) -> DataFrame:
        Gets a single row from the DataFrame based on its index name. The
        row is returned as a pandas DataFrame.

    get_row_df_by_index(row_index: int) -> DataFrame:
        Gets a single row from the DataFrame based on its integer index. The
        row is returned as a pandas DataFrame.

    get_row_series_by_name(row_name: str) -> Series:
        Gets a single row from the DataFrame based on its index name. The
        row is returned as a pandas Series.

    get_row_series_by_index(row_index: int) -> Series:
        Gets a single row from the DataFrame based on its integer index. The
        row is returned as a pandas Series.

    get_row_id_by_row_name(row_name: str) -> int | None:
        Searches the index of the row with the given name in the index column.

    get_row_name_by_row_id(id: int) -> str:
        Gets the row name corresponding to a given integer row index.

    has_rows_intersection_with(other: DataFrame) -> bool:
        Checks if the current DataFrame has an intersection with the other
        DataFrame.

    join(my_df_lst: List[MyDataFrame]) -> MyDataFrame:
        Joins the rows of several MyDataFrames in one MyDataFrame.

    reduce_n_rows(max_n_rows: int) -> DataFrame:
        Reduces the number of rows to the given maximimum number of rows.

    row_index_is_subset_of(self, other: DataFrame) -> bool:
        Checks if the current DataFrame is a subset of the other DataFrame.

    row_index_is_superset_of(self, other: DataFrame) -> bool:
        Checks if the current DataFrame is a superset of the other DataFrame.

    shuffle() -> DataFrame:
        Shuffles the rows of the DataFrame.

    """

    # region --- Public Methods

    def shuffle(self) \
            -> DataFrame:
        """
        Shuffles the rows of the DataFrame.

        Returns
        -------
        DataFrame
            The DataFrame with the rows in a new random order.

        """

        return self.my_df.df.sample(frac=1)

    def reduce_n_rows(self, max_n_rows: int) \
            -> DataFrame:
        """
        Reduces the number of rows to the given maximimum number of rows.

        Parameters
        ----------
        max_n_rows : int
           Maximum number of rows to return.

        Returns
        -------
        DataFrame
            The DataFrame with reduced number of rows.

        """

        return self.my_df.df[:max_n_rows]

    def drop_row_by_row_name(self, row_name: str) \
            -> None:
        """
        Drops a row from the DataFrame based on its row name.

        Parameters
        ----------
       row_name : str
            The name of the row to drop.

        """

        self.my_df.df.drop(row_name, inplace=True)

    def get_row_df_by_name(self, row_name: str) \
            -> DataFrame:
        """
        Gets a single row from the DataFrame based on its index name.

        This method can be used for DataFrames where the index consists of
        meaningful labels rather than row numbers.

        Parameters
        ----------
        row_name : str
           The index name of the row to retrieve.

        Returns
        -------
        DataFrame
           A pandas DataFrame containing the requested row. Note that the
           returned object is a DataFrame with a single row, not a Series,
           preserving the original DataFrame's column structure.

        Raises
        ------
        KeyError
            If the DataFrame wrapped in this class does not contain the
            given row name.

        Example
        -------
        The following example gets the row labeled "example_row" from the
        DataFrame, my_df being an instance of the MyDataFrame class:

        >>> single_row_df = my_df.do_with_row(
        ...     'get_row_df_by_name',
        ...     row_name='example_row'
        ... )

        Notes
        -----
        Row names are case-sensitive. Make sure the row name you provide is
        written exactly the same as the row name you are looking for in the
        DataFrame.

        """

        return self.my_df.df.loc[[row_name]]

    def get_row_series_by_name(self, row_name: str) \
            -> Series:
        """
        Gets a single row from the DataFrame based on its index name.

        This method can be used for DataFrames where the index consists of
        meaningful labels rather than row numbers.

        Parameters
        ----------
        row_name : str
           The index name of the row to retrieve.

        Returns
        -------
        Series
           A pandas Series containing the requested row.

        Raises
        ------
        KeyError
            If the DataFrame wrapped in this class does not contain the
            given row name.

        Example
        -------
        The following example gets the row labeled "example_row" from the
        DataFrame, my_df being an instance of the MyDataFrame class:

        >>> single_row_df = my_df.do_with_row(
        ...     'get_row_series_by_name',
        ...     row_name="example_row"
        ... )

        Notes
        -----
        Row names are case-sensitive. Make sure the row name you provide is
        written exactly the same as the row name you are looking for in the
        DataFrame.

        """

        return self.my_df.df.loc[row_name]

    def get_row_df_by_index(self, row_index: int) \
            -> DataFrame:
        """
        Gets a single row from the DataFrame based on its integer index.

        Parameters
        ----------
        row_index : int
            The integer index of the row to retrieve. Indexing starts at 0.

        Returns
        -------
        DataFrame
            A pandas DataFrame containing the requested row. Note that the
            returned object is a DataFrame with a single row, not a Series,
            preserving the original DataFrame's column structure.

        Raises
        ------
        IndexError
            If 'row_index' is out of bounds for the DataFrame.

        Example
        -------
        The following example gets the second row of the DataFrame,
        my_df being an instance of the MyDataFrame class:

        >>> single_row_df = my_df.do_with_row(
        ...     'get_row_df_by_index', row_index=1
        ... )

        """

        return self.my_df.df.iloc[[row_index]]

    def get_row_series_by_index(self, row_index: int) \
            -> Series:
        """
        Gets a single row from the DataFrame based on its integer index.

        Parameters
        ----------
        row_index : int
            The integer index of the row to retrieve. Indexing starts at 0.

        Returns
        -------
        Series
            A pandas Series containing the requested row.

        Raises
        ------
        IndexError
            If 'row_index' is out of bounds for the DataFrame.

        Example
        -------
        The following example gets the second row of the DataFrame,
        my_df being an instance of the MyDataFrame class:

        >>> single_row_df = my_df.do_with_row(
        ...     'get_row_series_by_index',
        ...     row_index=1
        ... )

        """

        return self.my_df.df.iloc[row_index]

    def extract_rows_by_col_value(
            self,
            col_name: str,
            col_value: Any,
            op: Callable[[Any, Any], bool] = operator.eq

    ) -> DataFrame:
        """
        Extracts rows where the specified column value fulfills a condition.

        Extracts rows from the DataFrame based on a condition concerning the
        value of a column.

        This method can be used to extract all rows in the DataFrame that
        fulfill the specified condition for the value in the given column.

        Parameters
        ----------
        col_name : str
            The name of the column to filter on.

        col_value : Any
            The value with which to compare the values on in the given column.

        op : Callable[[Any, Any], bool]
            The comparison operator to use for the filter ,  e.g.:
            - operator.lt for <,
            - operator.gt for >,
            - operator.le for <=,
            - operator.ne for !=,
            - operator.eq for ==,
            - operator.ge for >=.

            Defaults to operator.eq

        Returns
        -------
        DataFrame
            A pandas DataFrame containing the rows that fulfill the given
            condition in the given column.

        """

        condition = op(self.my_df.df[col_name], col_value)
        return self.my_df.df[condition]

    def extract_rows_by_other_indices(self, other: MyDataFrame) \
            -> DataFrame:
        """
        Extracts rows using the indices of another MyDataFrame.

        This method selects rows from the DataFrame based on the index values
        present in another MyDataFrame.

        Parameters
        ----------
        other : MyDataFrame
            The MyDataFrame object whose index values are used to filter the
            rows in the current DataFrame.

        Returns
        -------
        DataFrame
            A pandas DataFrame containing the rows whose indices match those
            in the other MyDataFrame.

        """

        return self.my_df.df.loc[other.df.index]

    def add_empty_row(self) \
            -> None:
        """
        Adds an empty row to the dataframe.

        Assigns NaN values to each field of the new row.

        Notes
        -----
        This method uses the 'loc' indexer to assign np.nan values to all
        fields of the new row, using pandas's ability to propagate a single
        value across multiple columns as an efficient way to add an
        empty row to the dataframe.

        """

        self.my_df.df.loc[len(self.my_df.df)] = np.nan

    def add_rows(
            self,
            data: MyDataFrame |
                  DataFrame |
                  DictOfLists |
                  List[List[int | float | str]] |
                  List[Dict[str, int | float | str]] |
                  List[int | float | str] |
                  None = None,
            ignore_index: bool = True
    ) -> None:

        """
        Adds one or more rows to the dataframe.

        If data is None, an empty row is directly added to the dataframe.

        Otherwise, before appending, the data undergoes validation checks for
        data types, column count, and column names to ensure compatibility
        with the existing dataframe structure. Upon passing these checks, the
        data is converted into a pandas DataFrame and appended.

        The supported data types for this method align with those with
        which the class's data can be initialized.

        Parameters
        ----------
        data :  MyDataFrame |
                DataFrame |
                DictOfLists |
                List[List[int | float | str]] |
                List[Dict[str, int | float | str]] |
                List[int | float | str] |
                None

            The data of the rows to be added to the dataframe. The supported
            structures are as follows:

            - MyDataFrame: Should wrap a DataFrame with a compatible, if not
              the same, structure as the class's dataframe.

            - DataFrame: Should have a compatible, if not the same, structure
              as the class's dataframe.

            - Dict: Maps column names (str) to lists of column values (int |
              float | str), representing one or more rows.

            - List[List[int | float | str]]: Each inner list represents a
              single row's values.

            - List[Dict[str, int | float | str]]: Each dictionary
              contained represents one or more rows, with keys as column names
              and values as lists of column values.

            - List[int | float | str]: Represents a single row's values
              across columns.

            - Non-flat lists or tuples can contain
                - either flat lists
                    representing the values of single rows,
                - or dictionaries
                    organized the way described above and representing the
                    data of one or more rows.

            Defaults to None.

        ignore_index : bool
            - Should be set to True if the row index is supposed to be
              reindexed so that the rows receive consecutive numbers.
            - Should be set to False if the different rows contain
              meaningful indices that should be preserved.
            - Defaults to True.


        Raises
        ------
        CriticalException
            Raised if the data fails validation checks, indicating that the
            columns of the row are incompatible with the target dataframe's
            structure.

            May occur in the following cases:

            - If the row contains columns that are not present in the target
              dataframe.

            - If the row's column names do not match the names in the target
              dataframe.

            - If the row's column data types do not match those of the target
              dataframe.

        """

        if data is None:
            self.add_empty_row()

        elif self._validate_new_row_data(data):

            my_data_frame_cls = LateImports.get_my_dataframe_class()

            if isinstance(data, (pd.DataFrame, my_data_frame_cls)):
                self._append_rows(data, ignore_index=ignore_index)
            else:
                self._append_rows(
                    DataFrameFactory.create(
                        data,
                        col_names=self.my_df.col_names
                    ),
                    ignore_index=ignore_index
                )
        else:

            raise CriticalException(
                self.logger,
                "The data contains columns that do not match the "
                "dataframe's columns. Cannot add the rows."
            )

    def join(self, my_df_lst: List[MyDataFrame]) \
            -> MyDataFrame:
        """
        Joins the rows of several MyDataFrames in one MyDataFrame.

        Parameters
        ----------
        my_df_lst : List[MyDataFrame]
            The list of MyDataFrame objects to join.

        Returns
        -------
        MyDataFrame
            The resulting MyDataFrame with the joined rows.

        """

        for my_df in my_df_lst:
            self.add_rows(my_df, False)
        return self.my_df

    def get_row_id_by_row_name(self, row_name: str) \
            -> int | None:
        """
        Searches the index of the row with the given name in the index column.

        Parameters
        ----------
        row_name : str
            The value to search for in the index column.

        Returns
        -------
        int | None
            The index number of the row, or None if not found.

        """

        if self.my_df.row_index is None:
            raise CriticalException(
                self.logger,
                "Index column not set. Cannot search for row name."
            )

        try:
            return self.my_df.df.index.get_loc(row_name)

        except KeyError:
            return None

    def get_row_name_by_row_id(self, row_id: int) \
            -> str:
        """
        Gets the row name corresponding to a given integer row index.

        Parameters
        ----------
        row_id : int
            The integer index of the row.

        Returns
        -------
        str | int
            The row name corresponding to the index.

        Raises
        ------
        IndexError
            If the row index is out of bounds.

        """

        df = self.my_df.df

        if not (0 <= row_id < len(df.index)):
            raise IndexError(
                f"Row index {row_id} is out of bounds. Valid range: 0 to "
                f"{len(df.index) - 1}"
            )

        return df.index[row_id]

    def check_indices(self, other: DataFrame) \
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

        if self.my_df.df.index.equals(other.index):
            return True

        if other.index.size == self.my_df.df.index.size:
            raise CriticalException(
                self.logger,
                "The two DataFrames have different indices. Cannot merge them."
            )

        if other.index.size != self.my_df.df.index.size:
            if self.row_index_is_subset_of(other):
                additional_ix = self.get_additional_row_indices(other)

                msg = (
                    f"The new column has additional row(s) {additional_ix}. "
                    f"The additional rows will be added to the original "
                    f"DataFrame...")
                self._log(msg, 'info')

                return True

            if self.row_index_is_superset_of(other):
                missing_ix = self.get_missing_indices(other)

                msg = (f"The new column has missing row(s) {missing_ix}. "
                       f"The missing rows will be added to the column...")
                self._log(msg, 'info')

                return True

            if self.has_rows_intersection_with(other):
                msg = ("The new column has an intersection with the "
                       "original DataFrame. The DataFrame will be extended "
                       "by the additional rows of the new column...")
                self._log(msg, 'info')

                return True

        return False

    def has_rows_intersection_with(self, other: DataFrame) \
            -> bool:
        """
        Checks if the DataFrame has an intersection with the other DataFrame.

        Checks if the current DataFrame has an intersection with the other
        DataFrame.

        Parameters
        ----------
        other : DataFrame
            The other DataFrame to compare with.

        Returns
        -------
        bool
            True if the two DataFrames have common rows, False otherwise.

        """

        missing = self.get_missing_indices(other)
        additional = self.get_additional_row_indices(other)

        if missing.size > 0 and additional.size > 0:
            return True

        return False

    def get_missing_indices(self, other: DataFrame) \
            -> Index:
        """
        Returns the row indices that are missing in the other DataFrame.

        Returns the row indices in the current DataFrame that are not
        present in the other DataFrame.

        Parameters
        ----------
        other : DataFrame
            The other DataFrame to compare with.

        Returns
        -------
        Index
            The row indices in the current DataFrame that are not present in
            the other DataFrame.

        """

        return self.my_df.df.index.difference(other.index)

    def get_additional_row_indices(self, other: DataFrame) \
            -> Index:
        """
        Returns the additional row indices of the other DataFrame.

        Returns the row indices in the other DataFrame that are not present in
        the current DataFrame.

        Parameters
        ----------
        other : DataFrame
            The other DataFrame to compare with.

        Returns
        -------
        Index
            The row indices in the other DataFrame that are not present in the
            current DataFrame.

        """

        return other.index.difference(self.my_df.df.index)

    def row_index_is_subset_of(self, other: DataFrame) \
            -> bool:
        """
        Checks if the current DataFrame is a subset of the other DataFrame.

        Parameters

        ----------
        other : DataFrame
            The other DataFrame to compare with.

        Returns
        -------
        bool
            True if the current DataFrame is a subset of the other DataFrame,
            False otherwise.

        """

        if self.my_df.df.index.isin(other.index).all():
            return True

        return False

    def row_index_is_superset_of(self, other: DataFrame) \
            -> bool:
        """
        Checks if the current DataFrame is a superset of the other DataFrame.

        In other words, checks if the other DataFrame is a subset of the
        current DataFrame.

        Parameters
        ----------
        other : DataFrame
            The other DataFrame to compare with.

        Returns
        -------
        bool
            True if the other DataFrame is a subset of the current DataFrame,
            False otherwise.

        """

        if other.index.isin(self.my_df.df.index).all():
            return True

        return False

    # endregion --- Public Methods

    # region --- Protected Methods
    def _append_rows(
            self,
            other: DataFrame | MyDataFrame,
            ignore_index: bool = True
    ) -> None:
        """
        Appends the rows of a DataFrame to the end of the DataFrame that is
        wrapped in this class.

        Parameters
        ----------
        other : DataFrame | MyDataFrame
            The DataFrame to append to the DataFrame object of this class.

        ignore_index : bool
            - Should be set to True if the row index is supposed to be
              reindexed so that the rows receive consecutive numbers.
            - Should be set to False if the different rows contain
              meaningful indices that should be preserved.
            - Defaults to True.

        Notes
        -----
        - Ensures compatibility between the DataFrame to be appended (`other`)
          and the DataFrame wrapped by this class in terms of column names,
          column order, and data types to prevent issues such as misaligned
          cols or data type mismatches.

        - The original index of 'other' will be ignored in favour of the target
          dataframe's index.

        - This method is resource-intensive when used frequently and/or with
          big DataFrames.

        """

        # If a MyDataFrame object was provided, use the DataFrame wrapped in
        # the object:
        if not isinstance(other, DataFrame):

            # Prevent circular imports
            my_data_frame_cls = LateImports.get_my_dataframe_class()

            if isinstance(other, my_data_frame_cls):
                other = cast(my_data_frame_cls, other).df
            else:
                msg = ("Expected DataFrame or MyDataFrame. Got %s instead" %
                       type(other))
                self._log(msg, 'error')
                raise TypeError(msg)

        # Copy the column names to ensure the column names of the two
        # dataframes match for the intended concat function to work smoothly,
        # since dataframes originating from lists or tuples do not contain
        # column names.
        other.columns = self.my_df.df.columns

        self.my_df.df = pd.concat(
            [self.my_df.df, other], ignore_index=ignore_index
        )

    def _validate_new_row_data(
            self,
            data: MyDataFrame | DataFrame | dict | list | tuple | None =
            None
    ) -> bool:
        """
        Validates the data against the DataFrame's schema.

        This includes checking for matching column names (keys) and compatible
        data types. Flat lists and tuples are directly checked for data types,
        while non-flat lists and tuples are assumed to represent multiple rows
        or complex structures that requires conversion to a DataFrame for
        comprehensive validation.

        Parameters
        ----------
        data : MyDataFrame | DataFrame | dict | list | tuple | None
            The data to be validated. Defaults to None.

        Returns
        -------
        bool
            True if the data passes the validation checks, False otherwise.

        Raises
        ------
        TypeError
            If an unsupported data type is provided.

        Notes
        -----
        Non-flat lists and tuples are more efficiently handled by the
        validation checks if previously converted to dataframes,
        allowing for leveraging pandas' sophisticated data handling
        approaches.

        """
        # Prevent circular imports
        my_data_frame_cls = LateImports.get_my_dataframe_class()

        if isinstance(data, my_data_frame_cls):
            return (
                    self._check_keys(cast(my_data_frame_cls, data).df) and
                    self._check_data_types(
                        cast(my_data_frame_cls, data).df
                    )
            )

        if isinstance(data, (DataFrame, dict)):
            return self._check_keys(data) and self._check_data_types(data)

        if isinstance(data, (list, tuple)):
            if is_flat(data):
                # For flat lists/tuples, only type checking is relevant
                return self._check_data_types(data)

            # For non-flat lists and tuples, convert to DataFrame and
            # only check the number of cols and the data types,
            # because lists and tuples do not contain column names.
            data_df = DataFrame(data)
            return (
                    self._check_n_cols(data_df) and
                    self._check_data_types(data_df)
            )

        if data is None:
            # Cover the None case for completeness.
            # Trying to add new data without passing any data will
            # ultimately result in the creation of a new row in the class's
            # dataframe.
            return True

        msg = "Unsupported data type: %s" % type(data)
        self._log(msg, "error")
        raise TypeError(msg)

    def _check_data_types(
            self,
            data: DataFrame | dict | list | tuple
    ) -> bool:
        """
        Checks whether the data types of the data match the data types of
        the existing cols in the dataframe wrapped in this class.

        Parameters
        ----------
        data: DataFrame | dict | list | tuple
            Data to be checked.

        Returns
        -------
        bool
           - 'True' if all datatypes match.
           - 'False' if there is a mismatch or if column names do not match
             those of the dataframe.

        Notes
        -----
        This method logs an error message and returns 'False' if any of the
        column names in the data do not match the cols in the dataframe.
        Ensure that column names in the data match those in the dataframe to
        avoid mismatches and unnecessarily executing the method's code,
        e.g. by using the _check_keys method beforehand.

        """
        try:
            if isinstance(data, DataFrame):
                # By only checking cols which are common to both dataframes,
                # different column orders or missing cols in one of the
                # dataframes do not matter.
                common_columns = self.my_df.df.columns.intersection(
                    data.columns)
                return all(
                    self.my_df.df[col].dtype == data[col].dtype
                    for col in common_columns
                )

            if isinstance(data, dict):
                for key, value in data.items():
                    if self.my_df.do_with_column(
                        'get_col_type', col_name=key
                    ) != pd.Series(value).dtype:
                        return False

            elif isinstance(data, (list, tuple)):
                for i, value in enumerate(data):
                    if (
                            self.my_df.df.iloc[i, :].dtype !=
                            pd.Series(value).dtype
                    ):
                        return False

            return True

        except KeyError as err:
            msg = "Column names do not match! (%s)" % err
            self._log(msg, "error")
            return False

    def _check_n_cols(
            self,
            data: DataFrame
    ) -> bool:
        """
        Checks whether the given dataframe contains the same number of
        cols as the dataframe wrapped in this class.

        Parameters
        ----------
        data : DataFrame
            The dataframe to check.

        Returns
        -------
        bool
           - 'True' if the column numbers match.
           - 'False' if the column numbers do not match.

        """

        return len(data.columns) == self.my_df.n_cols

    def _check_keys(
            self,
            data: DataFrame | dict | list
    ) -> bool:
        """
        Checks whether all keys of the given data are contained in the
        DataFrame wrapped in this class.

        Parameters
        ----------
        data: DataFrame | dict | list
            Data to be checked.

        Returns
        -------
        bool
           - 'True' if all keys of the data are found in the DataFrame.
           - 'False' if there are keys in the data that are not found
             in the DataFrame.

        """

        if isinstance(data, DataFrame):
            return are_all_elements_included(
                data.columns, self.my_df.df.columns
            )

        if isinstance(data, dict):
            return are_all_elements_included(
                list(data.keys()),
                self.my_df.df.columns
            )

        if isinstance(data, list):

            # Check if it's a list of dictionaries
            if all(isinstance(item, dict) for item in data):
                return self._check_keys_of_list_of_dicts(data)

            # Check if it's a list of lists
            if all(isinstance(item, list) for item in data):
                return self._check_shapes_of_list_of_lists(data)

            # Unsupported list formats
            return False

        return False

    def _check_keys_of_list_of_dicts(
            self,
            data: List[Dict[str, int | float | str]]
    ) -> bool:
        """
        Checks compatibility of the data structure with the current DataFrame.

        Checks whether all keys of the given list of dicts correspond to
        column names in the DataFrame wrapped in this class.

        Parameters
        ----------
        data : List[Dict[str, int | float | str]]
            List of dictionaries whose string keys are to be matched with
            the column names of the current MyDataFrame object.

        Returns
        -------
        bool
            - True if the data structure is compatible with the current
              MyDataFrame.
            - False if the structure is incompatible.

        Notes
        -----
        If the data is None, it is assumed to be compatible, so that this
        method will return True.

        """

        if not data:
            return True

        return all(is_subset(list(d.keys()), list(self.my_df.df.columns))
                   for d in data)

    def _check_shapes_of_list_of_lists(
            self,
            data: List[List[int | float | str]]
    ) -> bool:
        """
        Checks compatibility of the data structure with the current DataFrame.

        Checks whether the number of elements in the inner list of the given
        list of lists corresponds to the number of columns in the
        DataFrame wrapped in this class.

        Parameters
        ----------
        data : List[List[int | float | str]]
            List of list whose number is to be matched with the number
            of columns of the current MyDataFrame object.

        Returns
        -------
        bool
            - True if the number of elements matches the number of columns.
            - False if the numbers are not equal.

        Notes
        -----
        If the data is None, it is assumed to be compatible, so that this
        method will return True.

        """

        if not data:
            return True

        return all(len(inner_list) == len(self.my_df.df.columns)
                   for inner_list in data)

    # endregion --- Protected Methods
