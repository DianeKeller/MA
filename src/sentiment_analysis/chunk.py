"""
chunk.py
--------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

import os
from typing import Dict, List

from pandas import DataFrame

from src.data_structures.my_data_frame import MyDataFrame
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.serialization.directory_factory import DirectoryFactory
from src.utils.list_sort_utils import sort_list_with_int_behind_last_underscore
from src.utils.list_utils import (
    remove_elements_from_list,
    get_elements_by_substring
)
from src.utils.data_utils import is_none_or_empty


class Chunk(MyDataFrame):
    """
    A specialized class for managing chunks of data.

    Inherits from MyDataFrame and adds methods specific to chunk operations.

    A Chunk is a MyDataFrame whose DataFrame contains a special data
    structure: It has non-query columns like 'sentence_normalized', 'mention'
    and 'polarity', 'query' columns and 'answer' columns, all identified by
    a query number appended to the column name.

    Attributes
    ----------
    config : SentimentAnalysisConfig
        The configuration settings for sentiment analysis operations.

    non_query_cols : List[str]
        The list of non-query columns in the data, retrieved from the LLM
        specified in the config settings.

    answer_cols : List[str]
        The list of answer columns in the data.

    query_cols : List[str]
        The query columns in the data.

    version : str
        The version retrieved from the _config variable.


    Methods
    -------
    rename_cols(cols_map: 'Dict[str, str]') -> None:
        Renames the columns of the DataFrame based on the provided column map.

    reorder_cols() -> None:
        Orders the columns of the current chunk in a standardized way.

    set_directory() -> None:
        Sets the directory for storing chunks.


    Inherited Attributes and Methods
    --------------------------------
    See the MyDataFrame class.

    """

    def __init__(
            self,
            data: DataFrame | None = None,
            name: str = '',
            source: str = ''
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the Chunk class with a DataFrame
        collection of data, an identifying name and an optional source from
        which the data can be fetched if is available from an online source.

        Parameters
        ----------
        data: DataFrame | None
            The data to populate the DataFrame. Defaults to None.

        name : str
            The name of the DataFrame. Defaults to an empty string.

        source : str | None
            The source (Url) where the data is to be fetched from.

        """

        super().__init__(data, name, source)

        self._query_cols = None
        self._answer_cols = None

        self.config = SentimentAnalysisConfig()

        """
        The non_query_cols is the list of column names that do not represent 
        query or answer columns. This depends on the columns a data source 
        suite produces and therefore, it needs to be fetched from the llm the 
        suite is attached to at the moment the Chunk instance is initialized.
        """
        self.non_query_cols = self.config.get('llm').non_query_cols

    # region --- Properties
    @property
    def version(self) \
            -> str:
        """
        Gets the version from the _config variable.

        Retrieves the version from the _config variable each time this getter
        is called. This ensures that the getter always returns the latest
        version.

        Returns
        -------
        str
            The version.

        """

        return self.config.get('version')

    @property
    def answer_cols(self) \
            -> List[str]:
        """
        Retrieves the list of answer columns associated with this object.

        This method returns the answer columns stored in the '_answer_cols'
        attribute. If '_answer_cols' is None or empty, it initializes the
        answer and query columns by invoking the '_set_answer_and_query_cols'
        method before returning the updated '_answer_cols' list.

        Returns
        -------
        List[str]
            A list of strings representing the answer column names.

        """

        if is_none_or_empty(self._answer_cols):
            self._set_answer_and_query_cols()

        return self._answer_cols

    @answer_cols.setter
    def answer_cols(self, answer_cols: List[str]) \
            -> None:
        """
        Sets the answer columns for the object.

        Parameters
        ----------
        answer_cols : List[str]
            A list of strings representing the column names to store as the
            answer columns within the object.

        """

        self._answer_cols = answer_cols

    @property
    def query_cols(self) \
            -> List[str]:
        """
        Returns the query columns for the instance.

        The 'query_cols' property retrieves the list of query column names
        associated with the instance. If the internal '_query_cols'
        variable is not set or empty, it invokes the
        '_set_answer_and_query_cols' method to populate the necessary
        query columns.

        Returns
        -------
        List[str]
            A list of query column names for the instance.

        """
        if is_none_or_empty(self._query_cols):
            self._set_answer_and_query_cols()

        return self._query_cols

    @query_cols.setter
    def query_cols(self, query_cols: List[str]) \
            -> None:
        """
        Sets the `query_cols` attribute for the instance.

        This setter method is used to assign a list of strings to the
        'query_cols' property of the instance. It directly updates the
        private attribute '_query_cols' with a provided value.

        Parameters
        ----------
        query_cols : List[str]
            A list of column names represented as strings to be stored
            in the `query_cols` attribute.

        """

        self._query_cols = query_cols

    # endregion --- Properties

    # region --- Public Methods
    def rename_cols(self, cols_map: Dict[str, str]) \
            -> None:
        """
        Renames the columns of the DataFrame based on the provided column map.

        This method updates the current DataFrame's column names according to
        the mapping provided in the `cols_map` parameter. The renaming is done
        in place and modifies the original DataFrame.

        Parameters
        ----------
        cols_map : Dict[str, str]
            A dictionary mapping the original column names (keys) to their
            new names (values). Keys represent the existing column names,
            and values define the corresponding new names to be assigned.

        """

        self.df.rename(columns=cols_map, inplace=True)

    def reorder_cols(self) \
            -> None:
        """
        Orders the columns of the current chunk in a standardized way.

        Puts the non-query columns first, then displays the query columns in
        alphabetically ascending orden, then the answer columns in the same
        order.

        """

        new_order = self.non_query_cols + self.query_cols + self.answer_cols

        if self.n_cols != len(new_order):
            raise CriticalException(
                self.logger,
                "Reordering of columns failed! Original number of "
                "columns: %d vs. reordered number of columns: %d" % (
                    self.n_cols, len(new_order)
                )
            )

        self.df = self.df[new_order]

        msg = (f"{self.n_cols} chunk columns reordered: "
               f"\n  - old:"
               f" {self.col_names} \n  - "
               f"new: "
               f"{new_order}")
        self.log(msg, 'info')

    def set_directory(self) \
            -> None:
        """
        Sets the directory for storing chunks.

        This method ensures that the appropriate directory path is set for
        storing chunks, based on the file's extension and the provided
        version. If the directory path does not already match the specified
        version, a new directory is created using the DirectoryFactory. The
        path of the directory is then updated, and an informational log
        message is generated for the operation.

        Raises
        ------
        FileNotFoundError
            If the directory cannot be created by the DirectoryFactory.

        Notes
        -----
        This method does not return any value.

        """

        if not self.serializer.file.path.endswith(self.version):
            dir_name = os.path.join(
                self.serializer.file.path,
                f"chunks_v_{self.version}"
            )
            try:
                directory = DirectoryFactory.create(
                    self.serializer.file.extension,
                    dir_name
                )
            except FileNotFoundError:
                directory = DirectoryFactory.make(
                    self.serializer.file.extension,
                    dir_name
                )

            self.serializer.file.path = str(directory.path)

        msg = "Chunk directory for %s set to %s" % (
            self.name, self.serializer.file.path
        )

        self._log(msg, 'info')

    # endregion --- Public Methods

    # region --- Protected Methods

    def _set_answer_and_query_cols(self) \
            -> None:
        """
        Sets the query and answer columns based on the column names.

        This method determines which columns correspond to query and answer
        data by removing non-query columns from the available column names
        and identifying columns that contain either the substring 'query' or
        'answer'. It sorts these columns based on integer values that appear
        behind the last underscore in their names and assigns them to
        respective attributes for later use.

        Notes
        -----
        This method modifies the 'query_cols' and 'answer_cols' properties in
            place and does not return any values.

        """

        cols = remove_elements_from_list(self.col_names, self.non_query_cols)
        query_cols = get_elements_by_substring(cols, "query")
        answer_cols = get_elements_by_substring(cols, "answer")
        self.query_cols = sort_list_with_int_behind_last_underscore(query_cols)
        self.answer_cols = sort_list_with_int_behind_last_underscore(
            answer_cols
        )

    # endregion --- Protected Methods
