"""
my_data_frame.py
----------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

from copy import deepcopy
from typing import List, Any, TypeVar

from pandas import DataFrame, Index

from logger import Logger
from src.data_structures.data_collection import DataCollection
from src.data_structures.data_frame_column_operations import \
    DataFrameColumnOperations
from src.data_structures.data_frame_field_operations import \
    DataFrameFieldOperations
from src.data_structures.data_frame_row_operations import \
    DataFrameRowOperations
from src.data_structures.item_collection_factories import ItemSeriesFactory
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.serialization.data_serialization_mixin import DataSerializationMixin
from src.utils.data_utils import is_none_or_empty
from src.utils.type_utils import is_int

T = TypeVar('T', bound='MyDataFrame')


class MyDataFrame(DataCollection, DataSerializationMixin):
    """
    MyDataFrame class.

    This class is designed to manage and manipulate data stored as a
    pandas DataFrame. It extends the functionalities of the DataCollection
    class and provides data serialization capabilities through the
    DataSerializationMixin, enabling efficient handling, transformation and
    serialization of data.

    Key Features:

    - Direct manipulation of the pandas DataFrame for various dataset-specific
      operations, such as filtering rows and columns, managing single-value
      columns and data validation.

    - Support for row, column and field operations through the use of
      DataFrameRowOperations, DataFrameColumnOperations and
      DataFrameFieldOperations.

    - Integration of data serialization for efficient data storage and
      retrieval.


    Attributes
    ----------
    data : DataFrame | None
        The pandas DataFrame stored in this class.

    name : str
        A name for the data, providing an identifier for logging and
        tracking purposes.

    source : str
        The source (URL or file path) for fetching the data.

    col_names : List[str]
        The column names in the DataFrame.

    col_operations : DataFrameColumnOperations
        Provides column-specific operations for the DataFrame.

    df : DataFrame
        The pandas DataFrame wrapped in this class.

    field_operations : DataFrameFieldOperations
        Provides field-specific operations for the DataFrame.

    file_name : str
        The name of the file used when saving the DataFrame.

    file_type : str
        The file format to use for serialization (default is 'pkl').

    n_cols : int
        The number of columns in the DataFrame.

    n_rows : int
        The number of rows in the DataFrame.

    row_index : Index | None
        The index of the rows in the DataFrame.

    row_operations : DataFrameRowOperations
        Provides row-specific operations for the DataFrame.


    Methods
    -------
    copy() -> T:
        Returns a copy of the current MyDataFrame object.

    do_with_row(operation: str, **kwargs) -> Any:
        Executes row-level operations on the DataFrame.

    do_with_column(operation: str, **kwargs) -> Any:
        Executes column-level operations on the DataFrame.

    do_with_field(operation: str, **kwargs) -> Any:
        Executes field-level operations on the DataFrame.

    drop_single_value_cols() -> None:
        Removes columns that have a single unique value or no data.

    find_single_value_cols() -> None:
        Finds columns that have only one unique value and stores them.

    filter_rows_by_col_value(col_name: str, col_value: Any) -> T:
        Filters rows based on a specific value in the given column.

    has_no_data(verbose: bool = True) -> bool:
        Checks if the MyDataFrame has no data.

    min_filter(col_name: str, min_value: Any) -> T:
        Filters rows based on a minimum value in the specified column.

    max_filter(col_name: str, max_value: Any) -> T:
        Filters rows based on a maximum value in the specified column.

    sorted(by_col: int | str = 0, asc: bool = True) -> T:
        Sorts the DataFrame by the specified column.

    transpose() -> None:
        Transposes the DataFrame wrapped in this class.

    """

    def __init__(
            self,
            data: DataFrame | None = None,
            name: str = '',
            source: str = ''
    ) -> None:

        """
        Constructor.

        Initializes a new instance of the MyDataFrame class with a DataFrame
        collection of data, an identifying name and an optional source from
        which the data can be fetched if is available from an online source.

        Parameters
        ----------
        data: DataFrame | None
            The data to populate the DataFrame. Defaults to None.

        name : str
            The name of the DataFrame. Defaults to an empty string.

        source : str | None
            The source (Url or file path) for fetching the data.

        Notes
        -----
        This class does not provide input parameters for setting the column
        names or the index column of the pandas DataFrame object. If needed,
        users can provide these elements when creating the MyDataFrame via the
        MyDataFrameFactory class. However, the column names and the index
        column can be set or modified later with the methods provided by the
        MyDataFrame class.

        Examples
        --------
        Setting an index column:

        >>> from pandas import DataFrame
        >>> from src.data_structures.my_dataframe_factory import (
        ...     MyDataFrameFactory
        ... )

        # Define sample data
        >>> sample_data = DataFrame({
        ...     'name': ['Alice', 'Bob'],
        ...     'age': [30, 24]
        ... })

        # Create a MyDataFrame instance and set the 'name' column as the index
        # column
        >>> df_with_index = MyDataFrameFactory.create(
        ...     data=sample_data,
        ...     col_names=['name', 'age'],
        ...     index_column='name'
        ... )

        >>> print(df_with_index.df)
               age
        name
        Alice   30
        Bob     24

        """

        super().__init__(data, name)

        self.source: str = source

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        # Set the file type and file name for saving and loading the
        # previously processed data.
        self.file_name = self.name
        self.file_type = 'pkl'

        self.row_operations = DataFrameRowOperations(self)
        self.col_operations = DataFrameColumnOperations(self)
        self.field_operations = DataFrameFieldOperations(self)

    def __str__(self) \
            -> str:
        """
        Returns a string representation of the MyDataFrame instance.

        Returns
        -------
        str
            A string representation of the MyDataFrame instance.

        """

        return self.df.__str__()

    # region --- Properties

    @property
    def df(self) \
            -> DataFrame:
        """
        Returns the actual DataFrame that is wrapped in this class.
        
        Returns
        -------
        DataFrame
            The DataFrame wrapped in this class.

        Notes
        -----
        Especially when referenced from outside this class, this property
        is used rather than the 'data' attribute, which is inherited from the
        'DataCollection' class, to avoid confusion because the MyDataFrame
        instance itself may also be 'data' wrapped in other classes. Rather
        than referencing the DataFrame by 'data.data', you can reference it
        by 'data.df'.
        
        """

        return self.data

    @df.setter
    def df(self, df: DataFrame) \
            -> None:
        """
        Sets the DataFrame that is wrapped in this class.

        Parameters
        ----------
        df : DataFrame
            The DataFrame to be wrapped in this class.

        Notes
        -----
        Especially from outside this class, use this setter rather than the
        'data' setter to avoid confusion between different 'data' attributes of
        different classes inheriting from the DataCollection class.
        
        """

        self.data = df

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name
        self.file_name = name

    @property
    def col_names(self) \
            -> List[str]:
        """
        Returns the column names in the data.
        
        """

        if self.has_data():
            return self.data.columns.values.tolist()  # type: ignore
        return []

    @property
    def index_column(self) \
            -> str:
        """
        Gets the index column.

        """

        if self.has_data():
            return self.data.get_index()  # type: ignore
        return ''

    @index_column.setter
    def index_column(self, index_column: str) \
            -> None:
        """
        Sets the index column.

        Parameters
        ----------
        index_column : str
            The name of the column to be set as the index column.

        """

        if (self.has_data() and
                index_column in self.data.columns):  # type: ignore

            self.data.set_index(index_column, inplace=True)  # type: ignore

        else:
            raise CriticalException(
                self.logger,
                "Index column '%s not found." % index_column
            )

    @property
    def row_index(self) \
            -> Index | None:
        """
        Gets the row index.

        Returns
        -------
        Index | None
            The row index of the dataframe, provided it is set. Otherwise,
            None.

        Examples
        --------
        Import pandas libraries

        >>> from pandas import DataFrame, Series, Index

        Create MyDataFrame object with some cols and rows:

        >>> from src.data_structures.my_dataframe_factory import (
        ...    MyDataFrameFactory
        ... )
        >>> my_df = MyDataFrameFactory.create({
        ...     'name': ['a', 'b'],
        ...     'nr': [7,9],
        ...     'info': ['Hello', 'world!']
        ... })

        The resulting DataFrame looks like this:
        _________________________________
            name       nr       info
        0   a           7       Hello
        1   b           9       World!
        =================================

        Set one of the cols as the row index:

        >>> my_df.row_index = 'name'

        The resulting DataFrame looks like this:
        _____________________________
                  nr        info
        name
        a           7       Hello
        b           9       World!
        =============================

        Get the row index and print it:

        >>> index = my_df.row_index
        >>> print(index)
        Index(['a', 'b'], dtype='object', name='name')

        Use the index to access a specific row:

        >>> row_df = my_df.do_with_row('get_row_df_by_name', row_name='b')

        The resulting row dataframe looks like this:
        _____________________________
                  nr        info
        name
        b           9       World!
        =============================

        or

        >>> row_series = my_df.do_with_row(
        ...     'get_row_series_by_name', row_name='b'
        ... )

        The resulting row series looks like this:
        __________________
                 b
        nr       9
        info     World!
        ==================
        """

        if self.has_data():
            return self.data.index  # type: ignore
        return None

    @row_index.setter
    def row_index(self, index_col_name: str) \
            -> None:
        """
        Sets the row index.

        The row index contains the row names. Use this
        setter if you want the values of a given column in your DataFrame to
        be used as row names instead of or additionally to the row
        numbers.

        Parameters
        ----------
        index_col_name : str
            The name of the column containing the row names.
        
        """

        if self.has_data():
            self.df.set_index(index_col_name, inplace=True)

    @property
    def n_cols(self) \
            -> int:
        """
        Returns the number of cols in the DataFrame.

        Returns
        -------
        int
            The number of cols in the DataFrame.

        """

        return len(self.df.columns)

    @property
    def n_rows(self) \
            -> int:
        """
        Returns the number of rows in the DataFrame.

        Returns
        -------
        int
            The number of rows in the DataFrame.

        """

        return len(self.df)

    # endregion --- Properties

    # region --- Methods

    def copy(self) \
            -> T:
        """
        Returns a copy of the current MyDataFrame object.

        Returns a copy of the current object with updated row, column and
        field operations variables.

        Returns
        -------
        T
            A new instance of the same type of the current class instance (
            MyDataFrame, Chunk, ...) with the same properties as the
            current one, except for the row_operations, col_operations and
            field_operations which are updated to reference the new object
            instead of the copied one.

        """

        new_my_df = deepcopy(self)
        new_my_df.row_operations = DataFrameRowOperations(new_my_df)
        new_my_df.col_operations = DataFrameColumnOperations(new_my_df)
        new_my_df.field_operations = DataFrameFieldOperations(new_my_df)

        return new_my_df

    def has_no_data(self, verbose: bool = True) \
            -> bool:
        """
        Checks if the MyDataFrame has no data.

        Parameters
        ----------
        verbose : bool
            Whether to print the output.

        Returns
        -------
        bool
            True if the MyDataFrame has no data, False otherwise.

        Notes
        -----
        This method implements the corresponding abstract method in the
        DataCollection interface.

        """

        no_data = is_none_or_empty(self.df)

        if no_data and verbose:
            msg = "No data! Cannot execute operation."
            self._log(msg, "warning")

        return no_data

    def transpose(self) \
            -> None:
        """
        Transposes the DataFrame wrapped in this class.
        """

        self.df = self.df.T

    def do_with_row(self, operation: str, **kwargs) \
            -> Any:
        """
        Executes row-level operations on the DataFrame.

        This method delegates row-specific operations to the
        'DataFrameRowOperations' class, allowing for various row operations
        such as row filtering, updating, or extraction of rows.

        Parameters
        ----------
        operation : str
            The name of the operation to perform on the rows of the DataFrame.
            This should match a method available in 'DataFrameRowOperations'.

        kwargs
            Additional parameters required by the specific row operation,
            passed as keyword arguments.

        Returns
        -------
        Any
            The result of the row operation. Its type depends on the
            operation performed.

        Examples
        --------
        >>> from src.data_structures.my_dataframe_factory import (
        ...     MyDataFrameFactory
        ... )

        # Data to create the DataFrame
        >>>     data_1 = {
        ...         'name': ['nnn', 'lll'],  # Index column values
        ...         'url': ['nnn_url', 'lll_url']  # Column values
        ...     }

        # Create MyDataFrame with 'name' as the index column
        >>> my_df_1 = MyDataFrameFactory.create(
        ...     data=data_1,
        ...     index_column='name'
        ... )

        # Other DataFrame
        >>>     data_2 = {
        ...         'name': ['ooo', 'ppp'],  # Index column values
        ...         'url': ['ooo_url', 'ppp_url']  # Column values
        ...     }

        >>> my_df_2 = MyDataFrameFactory.create(
        ...     data=data_2,
        ...     index_column='name'
        ... )

        >>> my_df_1.do_with_row('add_rows', data=my_df_2, ignore_index = False)

        >>> print(my_df_1)

        """

        return self.row_operations.do(operation, **kwargs)

    def do_with_column(self, operation: str, **kwargs) \
            -> Any:
        """
        Executes column-level operations on the DataFrame.

        This method delegates column-specific operations to the
        'DataFrameColumnOperations' class, allowing for various column
        operations such as renaming, dropping or transforming columns.

        Parameters
        ----------
        operation : str
            The name of the operation to perform on the columns of the
            DataFrame. This should match a method available in
            'DataFrameColumnOperations'.

        kwargs : Any
            Additional parameters required by the specific column operation,
            passed as keyword arguments.

        Returns
        -------
        Any
            The result of the column operation. Its type depends on the
            operation performed.

        Examples
        --------
        # Create MyDataFrame with Index
        >>> from src.data_structures.my_dataframe_factory import (
        ...     MyDataFrameFactory
        ... )
        >>> my_df = MyDataFrameFactory.create(
        ...     ['nnn', 'lll'], ['name']
        ... )

        >>> my_df.df.set_index(my_df.df.columns[0], inplace=True)

        # Add a column
        >>> my_df.do_with_column(
        ...     'add_column',
        ...     data=['nnn_url', 'lll_url'],
        ...     col_name='url'
        ... )

        >>> print(my_df)
                url
        name
        nnn   nnn_url
        lll   lll_url

        """

        return self.col_operations.do(operation, **kwargs)

    def do_with_field(self, operation: str, **kwargs) \
            -> Any:
        """
        Executes field-level operations on the DataFrame.

        This method delegates field-specific operations to the
        'DataFrameFieldOperations' class, allowing for various field
        operations such as updating values.

        Parameters
        ----------
        operation : str
            The name of the operation to perform on the fields of the
            DataFrame. This should match a method available in
            'DataFrameFieldOperations'.

        kwargs
            Additional parameters required by the specific field operation,
            passed as keyword arguments.

        Returns
        -------
        Any
            The result of the field operation. Its type depends on the
            operation performed.

        Examples
        --------

        >>> from src.data_structures.my_dataframe_factory import (
        ...     MyDataFrameFactory
        ... )

        # Data to create the DataFrame
        >>>     data = {
        ...         'name': ['nnn', 'lll'],  # Index column values
        ...         'url': ['nnn_url', 'lll_url']  # Column values
        ...     }

        # Create MyDataFrame with 'name' as the index column
        >>> my_df = MyDataFrameFactory.create(
        ...     data=data,
        ...     index_column='name'
        ... )

        # Change a field value
        >>> my_df.do_with_field(
        ...     'set_field_value',
        ...     row_identifier='nnn',
        ...     col_identifier='url',
        ...     value='n_url'
        ... )

        >>> print(my_df)
                url
        name
        nnn     n_url
        lll   lll_url

        """

        return self.field_operations.do(operation, **kwargs)

    def find_single_value_cols(self) \
            -> None:
        """
        Finds empty and single-value columns to set the 'single_value_cols'
        property.

        Finds columns that have no values or that only have one single
        value across the entire dataset. Such columns are considered as
        irrelevant, so that they can be dropped from the dataset.
        Nevertheless, their names and values are kept in a dictionary
        so that the information about which columns and values have been
        removed can be retrieved even after the columns have been dropped.

        Notes
        -----
        - This method calls the _find_single_value_cols method to enable the
          use of the @info_requires_data decorator which checks if the data
          exists and returns an empty dictionary if it does not.

        - The result of this method is a dictionary containing the names and
          the single value (if any) of columns identified as having no or a
          single unique value (format: {col_name: col_value}).

        - The resulting dictionary is not returned, but used to set the
          'single_value_cols' property.

        """

        single_value_cols = {}

        for col_name in self.col_names:

            unique_values = ItemSeriesFactory.create(
                self.df[col_name], ''
            ).distinct_elements

            if len(unique_values) <= 1:
                # If the column is empty, the value should be None:
                single_value_cols[col_name] = unique_values[0] \
                    if len(unique_values) == 1 \
                    else None

        self.single_value_cols = single_value_cols

    def drop_single_value_cols(self) \
            -> None:
        # Make sure the dataframe contains data

        msg = "Dropping irrelevant columns."
        self._log(msg, 'info')

        self.find_single_value_cols()

        # Get the list of column names from the dictionary
        col_names = list(self.single_value_cols.keys())

        self.do_with_column(
            'drop_columns',
            col_names=col_names
        )

        msg = "Columns dropped: %s." % col_names
        self._log(msg, 'info')

    def min_filter(self: T, col_name: str, min_value: Any) \
            -> T:
        raise NotImplementedError

    def max_filter(self: T, col_name: str, max_value: Any) \
            -> T:
        raise NotImplementedError

    def filter_rows_by_col_value(self: T, col_name: str, col_value: Any) \
            -> T:
        raise NotImplementedError

    def sorted(self, by_col: int | str = 0, asc: bool = True) \
            -> T:
        """
        Sorts the DataFrame in the MyDataFrame object by the specified column.

        Sorts the DataFrame in the MyDataFrame object by the specified
        column and returns a MyDataFrame with the modified DataFrame.

        Parameters
        ----------
        by_col : int | str
            Either the index or the name of the column by which the
            DataFrame is to be sorted. Defaults to 0.

        asc : bool
            Whether to sort in ascending order. True if an ascending order
            is required, False if a descending order is to be applied.
            Default is True (= ascending order).

        Returns
        -------
        T
            An instance of the same type as the current object, but with the
            DataFrame sorted according to the specified parameters.

        """

        # Make by_col use the column name rather than the column index:
        if is_int(by_col):
            by_col = self.df.columns[by_col]

        sorted_my_df = self.copy()
        sorted_my_df.df = sorted_my_df.df.sort_values(
            by=by_col, ascending=asc
        )
        return sorted_my_df

    # endregion --- Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
