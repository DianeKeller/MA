"""
data_collection.py
------------------
Version 1.0, updated on 2025-05-01

"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Any

from src.logging_mixin import LoggingMixin
from src.utils.data_utils import is_none_or_empty
from src.utils.print_utils import SUBSEPARATOR

T = TypeVar('T')


class DataCollection(ABC, Generic[T], LoggingMixin):
    """
    Abstract base class for different data collection structures. It defines
    functionalities like filtering and extracting data subsets by the
    content of given columns, and automatically eliminating columns with no
    informational value.

    Attributes
    ----------
    data T | None:
        The data, which can be stored in different types of data structures,
        e.g. a pandas dataframe or a HuggingFace DatasetDict.        .

    name : str
        An optional name for the data, providing a human-readable
        identifier for data saving, logging and tracking purposes.

    single_value_cols : dict[str, Any]
        A dictionary where the keys are column names and the values are the
        single unique value found in that column, if applicable. This is used
        to track columns that may not be informative.

    n_single_value_cols : int
        The number of columns that have been identified as containing no
        values or only a single unique value.

    Abstract Attributes
    -------------------
    n_rows : int
        The number of rows in the data. 

    n_cols : int
        The number of columns in the data. 

    col_names : List[str]
        A list of the column names in the data. Must be implemented by
        subclasses.


    Methods
    -------
    has_data() -> bool:
        Checks if the data is set and is not None or empty. Returns True if
        the data exists, False otherwise.
        
    to_string() -> str:
        Returns a string representation of the data, including basic metadata
        such as the number of rows and columns, column names, and any
        single-value columns identified and removed.
        
    Abstract Methods
    ----------------
    filter_rows_by_col_value(col_name: str, col_value: Any) -> T:
        Extracts all rows from the data where the value in the given column
        matches the specified column value and returns them in the same type
        of data structure as the original data. Must be implemented by 
        subclasses.

    drop_single_value_cols() -> None:
        Removes identified single-value columns from the data to streamline
        the data set. 

    find_single_value_cols() -> None:
        Identifies columns in the data that contain no values or only a single
        value, marking them for potential removal. This method sets the
        'single_value_cols' property. 

    has_no_data(verbose: bool = True) -> bool:
        Checks if the data is None or empty. If the 'verbose' parameter is set
        to True, a warning message is logged in case the data is None or empty.
        

    min_filter(col_name: str, min_value: Any) -> T:
        Extracts all rows from the data where the value in the given column
        is greater than or equal to the specified minimum value. Must be 
        implemented by subclasses.

    max_filter(col_name: str, max_value: Any) -> T:
        Extracts all rows from the data where the value in the given column
        is smaller than or equal to the specified maximum value. Must be 
        implemented by subclasses.

    """

    def __init__(
            self,
            data: T | None,
            name: str = ''
    ) -> None:
        """
        Constructor.

        Initializes a new instance of this base class with any type of data
        collection and an identifying name.

        Parameters
        ----------
        data : T | None
            The data wrapped in this class.

        name: str
            A name identifying the data, used for naming files when saving
            the data or information related to it.

        """
        self._data: T | None = None
        self._name: str = ''

        self.data = data
        self.name = name

        self._single_value_cols: dict[str, Any] = {}

    # region --- Properties

    @property
    def name(self) \
            -> str:
        """
        Gets the name of the data.
        """
        return self._name

    @name.setter
    def name(self, name: str) \
            -> None:
        """
        Sets the name of the data.
        """
        self._name = name

    @property
    def data(self) \
            -> T | None:
        """
        Gets the data.
        """
        return self._data

    @data.setter
    def data(self, data: T) \
            -> None:
        """
        Sets the data.
        """
        self._data = data

    @property
    def single_value_cols(self) \
            -> dict[str, Any]:
        """
        Gets the single value columns from the data.

        If they are not set, the find_single_value_cols method will be
        called, which will set the single_value_cols so that they can be
        returned.

        """

        if is_none_or_empty(self.data):
            msg = "There is no data! Cannot search for single value columns!"
            self._log(msg, level="warning")
            return {}

        if not self._single_value_cols:
            self.find_single_value_cols()

        return self._single_value_cols

    @single_value_cols.setter
    def single_value_cols(self, cols: dict[str, Any]) \
            -> None:
        """
        Sets the single value columns.
        """

        self._single_value_cols = cols

    @property
    def n_single_value_cols(self) \
            -> int:
        """
        Returns the number of single-value columns.
        """

        return len(self.single_value_cols.keys())

    @property
    @abstractmethod
    def n_rows(self) \
            -> int:
        """
        Returns the number of rows in the data.
        """

    @property
    @abstractmethod
    def n_cols(self) \
            -> int:
        """
        Returns the number of columns in the data.
        """

    @property
    @abstractmethod
    def col_names(self) \
            -> List[str]:
        """
        Returns the column names of the data object.

        The way how the list of column names is provided by the data object of
        the different subclasses depends on the data type of the data object.
        Therefore, this property is abstract and must be implemented by the
        subclasses.

        """

    # endregion --- properties

    # region --- Public Methods

    @abstractmethod
    def filter_rows_by_col_value(self: T, col_name: str, col_value: Any) \
            -> T:
        """
        Extracts all rows from the data where the value in a given column
        matches the specified column value.

        Parameters
        ----------
        col_name : str
            The name of the column in which to seek for the specified value.

        col_value : Any
            The value for which to seek in the specified column

        Returns
        -------
        T
            A new MyDataFrame containing the extracted rows.

        """

    @abstractmethod
    def min_filter(self: T, col_name: str, min_value: Any) \
            -> T:
        """
        Extracts all rows from the data where the value in a given column
        is greater than or equal to the specified minimum value.

        Parameters
        ----------
        col_name : str
            The name of the column in which to seek for the specified value.

        min_value : Any
            The minimum value with which to compare the values in the
            specified column

        Returns
        -------
        T
            A new MyDataFrame containing the extracted rows.

        """

    @abstractmethod
    def max_filter(self: T, col_name: str, max_value: Any) \
            -> T:
        """
        Extracts all rows from the data where the value in a given column
        is smaller than or equal to the specified minimum value.

        Parameters
        ----------
        col_name : str
            The name of the column in which to seek for the specified value.

        max_value : Any
            The maximum value with which to compare the values in the
            specified column

        Returns
        -------
        T
            A new MyDataFrame containing the extracted rows.

        """

    @abstractmethod
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
        The result of this method is a dictionary containing the names and the
        single value (if any) of columns identified as having no or a single
        unique value (format: {col_name: col_value}). The resulting
        dictionary is not returned, but used to set the 'single_value_cols'
        property.

        """

    @abstractmethod
    def drop_single_value_cols(self) \
            -> None:
        """
        Removes all columns from the DatasetDict that have no informational
        value.

        Empty columns and columns that only have one single value across the
        dataset are dropped.

        """

    @abstractmethod
    def has_no_data(self, verbose: bool = True) \
            -> bool:
        """
        Checks if the data is None or empty.

        If the 'verbose' parameter is set to True, a warning message is
        logged in case the data is None or empty.

        Returns
        -------
        bool
            True if the data is None or empty, False otherwise.

        """

    def has_data(self) \
            -> bool:
        """
        Checks if the data is set and is not None or empty.

        Returns
        -------
        bool
            True if the data exists, False otherwise.

        """

        return not self.has_no_data()

    def to_string(self):
        """
        Returns a string representation of the data.

        Returns
        -------
        str
            A string representation of the data.

        Notes
        -----
        The content of this method is not inserted in the __str__ method
        because this is executed each time the class is viewed in the
        debugger. This is extremely confusing, especially if the string
        representation uses computed properties.

        """

        return (
            f"{SUBSEPARATOR} \n"
            f"{self.name} \n"
            f"{SUBSEPARATOR} \n"
            f"Data: {self.data} \n"
            f"Data type: {type(self.data)} \n"
            f"Rows and columns: {(self.n_rows, self.n_cols)} \n"
            f"Columns: {self.n_cols} {self.col_names} \n"
            f"Empty or single-value columns dropped:"
            f""
            f"{len(self.single_value_cols) if self.single_value_cols else ''}"
            f" {self.single_value_cols} \n"
        )

    # endregion --- Public Methods
