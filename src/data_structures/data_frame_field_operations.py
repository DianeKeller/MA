"""
data_frame_field_operations.py
------------------------------
Version 1.0, validated on 2024-12-17

"""

from __future__ import annotations

from typing import Any

from src.data_structures.data_frame_operations import DataFrameOperations
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)


class DataFrameFieldOperations(DataFrameOperations):
    """
    DataFrameFieldOperations class.

    Provides field-specific operations for a MyDataFrame instance.

    This class extends DataFrameOperations to include methods that perform
    operations specifically on the fields of a MyDataFrame object. It
    allows for flexible manipulation of DataFrame fields using either labels
    or positional indices.

    Inherited Parameters
    --------------------
    my_df : MyDataFrame
        An instance of MyDataFrame on which field operations will be
        performed. This parameter is inherited from the DataFrameOperations
        base class.

    Methods
    -------
    get_field_value(row_identifier: str | int, col_identifier: str | int)
            -> Any:
        Gets the value of a field defined by row and column identifiers.

    set_field_value(row_identifier: str | int, col_identifier: str | int,
            value: str | int) -> None:
        Sets the value of a field defined by row and column identifiers.

    """

    # region --- Public Methods

    def set_field_value(
            self,
            row_identifier: str | int,
            col_identifier: str | int,
            value: str | int
    ) -> None:
        """
        Sets the value of a field defined by row and column identifiers.

        Parameters
        ----------
        row_identifier : str | int
            The label or the index number of the row.

        col_identifier : str | int
            The label or the index number of the column.

        value : Any
            The value to set in the specified field.

        Raises
        ------
        KeyError
            If the specified row or column does not exist.

        IndexError
            If the row or column index is out of bounds.

        CriticalException
            If an unexpected error occurs.

        Notes
        -----
        If the column identifier is a column name and the column does not
        exist in the DataFrame, the column is created.

        """

        df = self.my_df.df.copy()

        try:
            row_id = self.normalize_row_id(row_identifier)
            col_id = self.normalize_col_id(col_identifier)

            df.iat[row_id, col_id] = value

            self.my_df.df = df

        except KeyError as err:

            # Catch not existing column name by creating the missing column:
            if (
                    isinstance(col_identifier, str) and
                    col_identifier not in df.columns
            ):
                if not isinstance(row_identifier, str):
                    row_name = self.do_with_row(
                        'get_row_name_by_row_id',
                        id=row_identifier
                    )
                else:
                    row_name = row_identifier

                df.at[row_name, col_identifier] = value
                self.my_df.df = df

            else:
                msg = (
                    f"The specified row or column "
                    f"({row_identifier}, {col_identifier}) "
                    f"does not exist in the DataFrame. "
                    f"Row IDs: {list(df.index)}, "
                    f"Column IDs: {list(df.columns)}"
                )

                self._log(msg, level="error")
                raise KeyError(msg) from err

        except IndexError as err:

            # Handle out of bounds indices

            msg = (
                f"Row or column index ({row_identifier}, {col_identifier}) "
                f"is out of bounds. "
                f"Ensure that the identifiers are correct."
            )

            self._log(msg, level="error")
            raise IndexError(msg) from err

        except Exception as err:

            # Catch any other unexpected exceptions
            raise CriticalException(
                self.logger,
                (
                    f"An unexpected error occurred while setting the value at "
                    f"({row_identifier}, {col_identifier}): {err}"
                )
            )

    def get_field_value(
            self,
            row_identifier: str | int,
            col_identifier: str | int
    ) -> Any:
        """
        Gets the value of the specified field.

        Gets the value of the field defined by 'row_identifier' and
        'col_identifier'.

        Parameters
        ----------
        row_identifier : str | int
            The label or the index number of the row.

        col_identifier : str | int
            The label or the index number of the column.

        Returns
        -------
        Any
            The value of the field, which can be of any type that can be
            stored in a pandas DataFrame object.

        Raises
        ------
        KeyError
            If the specified row or column does not exist.

        IndexError
            If the row or column indices are out of bounds.

        CriticalException
            If an unexpected exception is raised.

        Notes
        -----
        This method is designed to work with both labels and indices for rows
        and columns.

        """

        df = self.my_df.df.copy()

        try:
            row_id = self.normalize_row_id(row_identifier)
            col_id = self.normalize_col_id(col_identifier)

            return df.iat[row_id, col_id]

        except KeyError as err:
            msg = (f"The specified row or column ({row_identifier}, "
                   f"{col_identifier}) does not exist in the "
                   f"DataFrame.")
            self._log(msg, level="error")
            raise KeyError(msg) from err

        except IndexError as err:
            msg = (f"Row or column index ({row_identifier}, "
                   f"{col_identifier}) is out of bounds.")
            self._log(msg, level="error")
            raise IndexError(msg) from err

        except Exception as err:
            raise CriticalException(
                self.logger,
                (
                    f"An unexpected error occurred ({row_identifier}, "
                    f"{col_identifier}): {err}"
                )
            )

    # endregion --- Public Methods
