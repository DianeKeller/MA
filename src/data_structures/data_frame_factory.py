"""
data_frame_factory.py
---------------------
Version 1.0, validated on 2024-12-04

This module provides a generic interface that dynamically selects the
appropriate method for constructing a DataFrame based on the type of input
data provided. It consists of the DataFrameFactory class and several functions
that form a single-dispatch mechanism.

"""
import inspect
from collections import OrderedDict
from functools import singledispatch
from typing import Dict, List, Any, Tuple

from pandas import DataFrame

from logger import Logger
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.dict_utils import (
    is_dict_of_list_of_str_int_tuples,
    is_dict_of_dicts
)
from src.utils.list_utils import (
    are_all_of_the_same_type, is_subset,
    have_intersection
)
from src.utils.type_utils import is_int
from type_aliases import DictOfLists, OrderedDictOfLists

logger = Logger(__name__).get_logger()
log = LoggingMixin().log


@singledispatch
def create_dataframe(
        data: DictOfLists |
              List[List[int | float | str]] |
              List[Dict[str, int | float | str]] |
              List[int | float | str] |
              DataFrame |
              OrderedDictOfLists |
              Tuple[Any, Any] |
              None,
        col_names: list[str] | None = None,
        row_names: list[str] | None = None,
        index_column: str | None = None
) -> DataFrame:
    """
    Generic function to create a pandas DataFrame from various types of
    input data. This function is the entry point for the singledispatch
    mechanism, which, based on the type of 'data', dynamically
    selects which of the following implementations to execute.

    Parameters
    ----------
    data :  DictOfLists |
            List[List[int | float | str]] |
            List[Dict[str, int | float | str]] |
            List[int | float | str] |
            DataFrame |
            OrderedDictOfLists |
            Tuple[Any, Any] |
            None
        The data to populate the DataFrame. The specific type of this argument
        determines which implementation of the function is called. Defaults
        to None.

    col_names : list[str] | None
        A list of column names for the DataFrame. If provided, it
        overrides the column names in the given data. Defaults to None.

    row_names : list[str] | None
        A list of row names for the DataFrame. Defaults to None.

    index_column : str | None
        The name of the index column. Defaults to None.

    Returns
    -------
    DataFrame
        A pandas DataFrame populated with the provided data.

    Raises
    ------
    NotImplementedError
        If the data type of 'data' is not supported.

    """

    msg = (f"Creation from {type(data).__name__} is not supported. "
           f"Data must be one of the supported data types")

    # Dummy if condition followed by return statement to make the code
    # checkers happy:
    if msg:
        logger.error(msg)
        raise NotImplementedError(msg)

    return DataFrameFactory.create(None)


@create_dataframe.register(type(None))
def _(
        _data: None,
        col_names: list[str] | None = None,
        row_names: list[str] | None = None,
        index_column: str | None = None
) -> DataFrame:
    """
    Implementation for creating an empty pandas DataFrame, executed when the
    data is None.

    Parameters
    ----------
    _data : None
        No data provided.

    For the other parameters, see the create_dataframe function.

    Example
    -------
    Creating an empty DataFrame with predefined column names:

    >>> df = DataFrameFactory.create(col_names=['name', 'nr'])
    >>> print(df)
    Empty DataFrame
    Columns: [name, nr]
    Index: []

    """

    if row_names:
        df = DataFrame(columns=col_names, index=row_names)
    else:
        df = DataFrame(columns=col_names)
        df = set_index(df, index_column)

    return df


@create_dataframe.register(dict)
def _(
        data: DictOfLists,
        col_names: list[str] | None = None,
        row_names: list[str] | None = None,
        index_column: str | None = None
) -> DataFrame:
    """
    Implementation for creating a DataFrame from a dictionary.

    Parameters
    ----------
    data : DictOfLists
        A dictionary of lists where the keys are column names and the values
        lists of column data.

    For the other parameters, see the create_dataframe function.

    Example
    --------
    Creating a DataFrame from a dictionary
    (Note that each dictionary entry consists of a column name and a
    list of values representing the column's data):

    >>> from src.data_structures.my_dataframe_factory import MyDataFrameFactory

    >>> ex_data = {'name': ['nnn', 'lll'], 'nr': [30, 24]}
    >>> ex_df = DataFrameFactory.create(ex_data)
    >>> print(ex_df)
       name  nr
    0  nnn   30
    1  lll   24


   """

    # Check whether the ordered dictionary contains scalar values instead of
    # lists of values (This is the case if only one row is passed to create a
    # DataFrame):
    if isinstance(data, dict) and all(
            isinstance(val, (int, float, str)) for val in data.values()
    ):
        data = [data]

    if is_dict_of_list_of_str_int_tuples(data):
        # Convert into dictionary of dictionaries
        data = {key: dict(values) for key, values in data.items()}

    if is_dict_of_dicts(data):
        return DataFrame.from_dict(data, orient='index')

    if row_names:
        df = DataFrame(data, columns=col_names, index=row_names) \
            if col_names \
            else DataFrame(data, index=row_names)
    else:
        df = DataFrame(data, columns=col_names) \
            if col_names \
            else DataFrame(data)

        df = set_index(df, index_column)

    return df


@create_dataframe.register(OrderedDict)
def _(
        data: OrderedDictOfLists,
        col_names: List[str] | None = None,
        row_names: List[str] | None = None,
        index_column: str | None = None
) -> DataFrame:
    """
    Implementation for creating a DataFrame from an ordered dictionary.

    Parameters
    ----------
    data : OrderedDictOfLists
        An ordered dictionary of lists where the keys are column names and
        the values lists of column data.

    For the other parameters, see the create_dataframe function.

    Example
    --------
    Creating a MyDataFrame from an ordered dictionary
    (Note that each dictionary entry consists of a column name and a
    list of values representing the column's data):
    >>> o_dict = OrderedDict ({
    ...     'b': "1bcd",
    ...     'f': "3fgh",
    ...     'e': "11def"
    ... })
    >>> ex_df = DataFrameFactory().create(
    ...     o_dict,
    ...     col_names=['values']
    ... )
    >>> print(ex_df)

   """
    # Check whether the ordered dictionary contains scalar values instead of
    # lists of values (This is the case if only one row is passed to create a
    # DataFrame):
    if isinstance(data, dict) and all(
            isinstance(val, (int, float, str)) for val in data.values()
    ):
        data = [data]

    if row_names:
        df = DataFrame(data, columns=col_names, index=row_names) \
            if col_names \
            else DataFrame(data, index=row_names)

    else:
        df = DataFrame(data, columns=col_names) \
            if col_names \
            else DataFrame(data)

        df = set_index(df, index_column)

    return df


@create_dataframe.register(list)
@create_dataframe.register(tuple)
def _(
        data: List[Any] | Tuple[Any],
        col_names: list[str] | None = None,
        row_names: list[str] | None = None,
        index_column: str | None = None
) -> DataFrame:
    """
    Implementation for creating a DataFrame from a list or tuple.

    Parameters
    ----------
    data : List[Any] | Tuple[Any]
        A list or tuple to convert into a DataFrame. The list or tuple can
        contain
        - dictionaries (each representing a row),
        - lists of values (each list representing a row),
        - or a single list of values (representing a single row).

    For the other parameters, see the create_dataframe function.

    Examples
    --------
    Creating a MyDataFrame from a list and specifying column names (Note
    that each inner list represents a row):

    >>> ex_data = [['nnn', 30], ['lll', 24]]
    >>> ex_df = DataFrameFactory.create(
    ...     data=ex_data, col_names=['name', 'nr']
    ... )
    >>> print(ex_df)
       name  nr
    0  nnn   30
    1  lll   24

    Creating a MyDataFrame from a list of values and specifying a column
    name (Note that the list of values represents the values of the
    column):

    >>> ex_data = ['nnn', 'lll']
    >>> ex_col_names = ['name']
    >>> ex_df = DataFrameFactory.create(data=ex_data, col_names=ex_col_names)
    >>> print(ex_df)
       name
    0  nnn
    1  lll

    """
    # Check if the list contains dictionaries, each representing a row
    if all(isinstance(item, dict) for item in data):
        return DataFrame(data)

    # Check if the list is a simple list of values forming a single
    # column or row.
    if all(isinstance(item, (int, float, str)) for item in data):
        if are_all_of_the_same_type(data):
            # The data are all have the same type. It is therefore assumed
            # that the values represent the content of a single column.

            column = col_names[0] if col_names else 'Column_0'
            return DataFrame({column: data}, columns=col_names)

        # The data have different types. It is therefore assumed that
        # they need to go into different columns, representing a
        # row with the given column names.

        return DataFrame([data], columns=col_names)

    # Check if the list contains lists, each representing a row
    if all(isinstance(item, (list, tuple)) for item in data):

        if col_names:
            return DataFrame(data, columns=col_names)

        return DataFrame(data)

    raise CriticalException(
        Logger(f"{inspect.currentframe().f_code.co_name}").get_logger(),
        "Unsupported list format for MyDataFrame creation."
    )


@create_dataframe.register(DataFrame)
def _(
        data: DataFrame,
        col_names: list[str] | None = None,
        row_names: list[str] | None = None,
        index_column: str | None = None
) -> DataFrame:
    """
    Implementation for handling a data input of type DataFrame.

    Implementation for handling the case that a DataFrame is passed to the
    factory.

    In case col_names is provided, this method checks whether the specified
    columns match the columns in the given DataFrame. If not, the columns in
    the DataFrame are switched to the new column names and a warning is
    issued and logged.

    Parameters
    ----------
    data : DataFrame
        A DataFrame.

    For the other parameters, see the create_dataframe function.

    """

    if col_names and col_names != data.columns:
        msg = (f"Column names of the DataFrame and specified columns "
               f"differ: DataFrame: {data.columns}, specified: "
               f"{col_names}. Column names set to the specified columns.")
        log(msg, "warning")
        data.columns = col_names

    return data


def set_index(df: DataFrame, index_column: str | None = None) \
        -> DataFrame:
    """
    Sets the index in the provided DataFrame using the specified column.

    Parameters
    ----------
    df : DataFrame
        The DataFrame whose index to set.

    index_column : str | None
        The name of the column to use as the index.

    Returns
    -------
    DataFrame
        The modified DataFrame.

    """
    if index_column:
        df.set_index(index_column, inplace=True)
    else:
        msg = ("No index column provided for DataFrame. You may want to "
               "set an index manually.")
        log(msg, 'info', 'set_index_manually')

    return df


class DataFrameFactory(LoggingMixin):
    """
    DataFrameFactory class.

    Factory class for creating pandas DataFrames.
    """

    # region --- Public Methods

    @staticmethod
    def create(
            data: DictOfLists |
                  List[List[int | float | str]] |
                  List[Dict[str, int | float | str]] |
                  List[int | float | str] |
                  DataFrame |
                  OrderedDictOfLists |
                  Tuple[Any, Any] |
                  None,
            col_names: list[str] | None = None,
            row_names: list[str] | None = None,
            index_column: str | None = None
    ) -> DataFrame:
        """
        Factory method to create a pandas DataFrame. This method delegates
        to the create_dataframe function, utilizing the singledispatch
        mechanism to handle different types of input data.

        Parameters
        ----------
        data : DictOfLists |
              List[List[int | float | str]] |
              List[Dict[str, int | float | str]] |
              List[int | float | str] |
              DataFrame |
              OrderedDictOfLists |
              Tuple[Any, Any] |
              None
            The data to populate the DataFrame. The specific type of this
            argument determines which implementation of the create_dataframe
            function is called.

        col_names : list[str] | None
            A list of column names for the DataFrame. If provided,
            the column names will be used to name the columns instead of
            assigning column numbers or keeping potentially automatically
            created column names, provided that the data does not already
            contain custom column names. See the 'notes' section for more
            information about the behavior of this parameter.

        row_names : list[str] | None
            A list of row names for the DataFrame. Should be provided when
            only one row is passed to the factory and none of the columns
            can be used as an index column. Defaults to None.

        index_column : str | None
            The name of the index column. Should be provided when
            only one row is passed to the factory and one of the columns
            is to be used as an index column. Defaults to None.

        Returns
        -------
        DataFrame
            A pandas DataFrame populated with the provided data.

        Notes
        -----
        Note the special behavior pandas DataFrames have if column names
        are specified when a DataFrame is created and the data already contains
        column names:

        - The additionally provided column names define the order of the
          matching existing columns. If the order does not match the
          existing order, the columns will be reordered.

        - Column names that are specified but not present in the data create
          new columns with empty values.

        - Existing columns which are not present in the specified column names
          will be dropped.

        - If the data already contains column names but none of them is in the
          specified column names, none of the data columns will be preserved
          and the specified column names will be used to label completely
          empty columns, i.e. the data will contain no rows.

        Examples
        --------
        >>> from src.data_structures.my_dataframe_factory import (
        ...     MyDataFrameFactory
        ... )

        # Data to create the DataFrame
        >>> data = {
        ...     'name': ['nnn', 'lll'],  # Index column values
        ...     'url': ['nnn_url', 'lll_url']  # Column values
        ... }

        # Create MyDataFrame with 'name' as the index column
        >>> my_df = MyDataFrameFactory.create(
        ...     data=data,
        ...     index_column='name'
        ... )

        >>> print(my_df)
                url
        name
        nnn     n_url
        lll   lll_url

        """

        # Delegate to the singledispatch function
        if col_names:
            # Compare the existing column names with the specified column names
            if DataFrameFactory.check_column_names(data, col_names):
                # The column names basically match but might be reordered or
                # new columns might be added when the DataFrame is created.
                if row_names:
                    return create_dataframe(
                        data,
                        col_names=col_names,
                        row_names=row_names,
                        index_column=index_column
                    )

                return create_dataframe(
                    data,
                    col_names=col_names,
                    index_column=index_column
                )

            # If the column check fails, do not change the columns. The
            # DataFrameFactory is not intended to be used for this kind of
            # operation and will not try to silently infer the intended
            # operation. Users should choose another, more explicit way to
            # manipulate the data according to their needs.

            df = create_dataframe(
                data,
                row_names=row_names,
                index_column=index_column
            ) if row_names \
                else create_dataframe(
                data,
                index_column=index_column
            )

            msg = "DataFrame created without changes to the data."
            log(msg, 'warning')
            return df

        # The column names are not specified

        return create_dataframe(
            data,
            row_names=row_names,
            index_column=index_column
        ) if row_names else create_dataframe(
            data, index_column=index_column
        )

    # region --- Public Methods

    @staticmethod
    def check_column_names(data: Any, col_names: list[str]) \
            -> bool:
        """
        Checks if the provided column names match the column names in the data.

        Converts the data to a temporary DataFrame without using the specified
        column names to be able to check for column names. The method then
        checks whether the temporary DataFrame has automatically assigned or
        custom column names and if the latter is the case, if they match the
        specified column names or can otherwise be safely applied to the
        target DataFrame the DataFrameFactory is about to create.

        Parameters:
        ----------
        data : Any
            The data whose column names are to be checked and compared with
            the specified column names.

        col_names : list[str]
            The specified column names that are to be compared with the
            existing column names

        Returns:
        -------
        bool
            True if the specified column names can safely be applied when
            creating the DataFrame, False otherwise.

        """

        df = DataFrameFactory.create(data)
        existing_col_names = df.columns.tolist()

        if existing_col_names == col_names:
            return True

        if DataFrameFactory._check_for_auto_col_identifiers(
                existing_col_names
        ):
            return True

        # For custom column names:
        return DataFrameFactory.check_custom_col_names(
            existing_col_names,
            col_names
        )

    # endregion --- Public Methods

    # region --- Protected Methods

    @staticmethod
    def _check_for_auto_col_identifiers(col_names: list[str | int]) \
            -> bool:
        """
        Checks for automatically assigned column identifiers.

        Checks whether the provided column names were automatically assigned.
        If so, they can be column numbers or column names starting with
        "Column_".

        Parameters
        ----------
        col_names : list[str | int]
            The column names to check.


        Returns
        -------
        bool
            True if the column names were automatically assigned,
            False otherwise.

        Notes
        -----
        When the DataFrameFactory constructs a DataFrame from a list having no
        custom column names, the column names are set to a string starting with
        "Column_", followed by the column number. In this case, the user will
        probably want to replace the column names with custom column names.

        """

        # Check whether the DataFrame has only column numbers:
        if all(is_int(name) for name in col_names):
            return True

        # Check whether the DataFrame has column names starting with "Column_":
        if all(
                isinstance(name, str) and name.startswith('Column_')
                for name in col_names
        ):
            return True

        return False

    @staticmethod
    def check_custom_col_names(
            existing_col_names: list[str],
            col_names: list[str]) -> bool:
        """
        Checks if the provided column names match the column names in the data.

        This method checks if the specified column names can be assigned to
        the DataFrame without the risk of altering the data.

        Parameters
        ----------
        existing_col_names : list[str]
            The existing column names in the data.

        col_names : list[str]
            The column names to check for.

        Returns
        -------
        bool
            - True if the column names match or if only new empty columns will
              be added to the existing ones if the specified column names are
              assigned.

            - False otherwise, as assigning the specified column names to the
              data would either overwrite existing column names or alter the
              data dropping entire columns.

        """

        if set(existing_col_names) == set(col_names):
            msg = ("Column names will be reordered. Current order: %s. New "
                   "order: %s" % (existing_col_names, col_names))
            log(msg, 'warning')
            return True

        if is_subset(existing_col_names, col_names):
            added_column_names = set(col_names) - set(existing_col_names)
            msg = ("The following empty columns will be added:  %s"
                   % added_column_names)
            log(msg, 'warning')
            return True

        if is_subset(col_names, existing_col_names):
            dropped_column_names = set(existing_col_names) - set(col_names)
            msg = ("The following existing data columns would be dropped:  %s"
                   % dropped_column_names)
            log(msg, 'warning')
            return False

        if have_intersection(existing_col_names, col_names):
            dropped_column_names = set(existing_col_names) - set(col_names)
            added_column_names = set(col_names) - set(existing_col_names)
            msg = ("The following existing data columns would be dropped:  %s "
                   "\n and the following empty columns would be added: %s"
                   % (dropped_column_names, added_column_names))
            log(msg, 'warning')
            return False

        msg = ("All existing data columns would be dropped and replaced by "
               "the specified empty columns. Is this the intended purpose?")
        log(msg, 'warning')
        return False

    # endregion --- Protected Methods
