"""
data_frame_operations.py
------------------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

import pandas as pd

from logger import Logger
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.type_utils import is_int

if TYPE_CHECKING:
    from src.data_structures.my_data_frame import MyDataFrame


class DataFrameOperations(LoggingMixin):
    """
    A base class for performing operations on a MyDataFrame instance.

    This class provides a structured way to access and manipulate data
    within a MyDataFrame object. It utilizes dynamic method resolution to
    perform specified operations, which allows for flexible handling of
    various data manipulation tasks. The class also integrates logging
    capabilities for operation tracking and error reporting.

    Parameters
    ----------
    my_dataframe : MyDataFrame
        An instance of MyDataFrame on which operations will be performed.

    Attributes
    ----------
    my_df : MyDataFrame
        The MyDataFrame instance passed during the class initialization.

    logger : Logger
        A Logger instance for logging messages related to the operations
        performed by the class.

    Methods
    -------
    do(operation, **kwargs) -> Any:
        Performs the specified operation on the MyDataFrame instance.

    normalize_col_id(col_identifier: str | int) -> int:
       Normalize the column identifier to an integer index.

    normalize_row_id(row_identifier: str | int) -> int:
        Normalize the row identifier to an integer index.


    See Also
    --------
    LoggingMixin : A mixin class providing logging capabilities.

    Notes
    -----
    The 'do' method dynamically resolves and calls the method corresponding
    to the 'operation' argument. This design allows for extending the class
    with new operations without modifying its interface.

    """

    def __init__(
            self,
            my_dataframe: MyDataFrame
    ):
        """
        Initializes the DataFrameOperations instance with a MyDataFrame object.

        Parameters
        ----------
        my_dataframe : MyDataFrame
            The MyDataFrame instance on which operations will be performed.

        """

        self.my_df = my_dataframe

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    def do(self, operation, **kwargs) \
            -> Any:
        """
        Performs the specified operation on the MyDataFrame instance.

        This method dynamically resolves and executes a method based on the
        'operation' argument. If the operation is not recognized, it raises
        a ValueError.

        Parameters
        ----------
        operation : str
            The name of the operation to perform. This should correspond to a
            method name within the class.

        **kwargs : dict
            Keyword arguments necessary for the specified operation.

        Returns
        -------
        Any
            The result of the operation performed, which varies depending on
            the operation.

        Raises
        ------
        CriticalException
            If the specified operation is not recognized or cannot be
            performed.

        Examples
        --------
        >>> operations.do('get_col_type', col_name='age')
        This would return the data type of the 'age' column in the MyDataFrame
        instance.

        """

        # Dynamically decide what to do based on the requested operation.
        method = getattr(self, operation, None)

        if method:
            return method(**kwargs)

        raise CriticalException(
            self.logger,
            "Unknown Operation %s!" % (operation,)
        )

    def normalize_row_id(self, row_identifier: str | int) \
            -> int:
        """
        Normalize the row identifier to an integer index.

        Parameters
        ----------
        row_identifier : str | int
            The label or index number of the row.

        Returns
        -------
        int
            The integer index corresponding to the row.

        Raises
        ------
        KeyError
            If the row index does not contain strings or the specified row
            identifier is not found in the index.

        """

        df = self.my_df.df.copy()

        if is_int(row_identifier):
            return row_identifier

        # Check if the index consists of labels instead of integer numbers:
        if not pd.api.types.is_object_dtype(df.index):
            msg = "DataFrame has no row labels."
            self._log(msg, 'error')

            raise KeyError(msg)

        # Search the identifier in the row labels.
        row_nr = self.my_df.do_with_row(
            'get_row_id_by_row_name',
            row_name=row_identifier
        )

        if row_nr is None:
            msg = "Row identifier '{row_identifier'} not found in row index."
            self._log(msg, 'error')

            raise KeyError(msg)

        return row_nr

    def normalize_col_id(self, col_identifier: str | int) -> int:
        """
        Normalize the column identifier to an integer index.

        Parameters
        ----------
        col_identifier : str | int
            The label or index number of the column.

        Returns
        -------
        int
            The integer index corresponding to the column.

        """

        df = self.my_df.df.copy()

        if isinstance(col_identifier, int):
            return col_identifier

        return df.columns.get_loc(col_identifier)
