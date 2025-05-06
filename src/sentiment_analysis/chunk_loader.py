"""
chunk_loader.py
---------------
Version 1.0, updated on 2025-05-01

"""

import sys
from math import ceil
from typing import Dict, List

from constants import DEFAULT_LANGUAGE
from logger import Logger

from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.decorators.data_check_decorators import (
    input_not_none_or_empty, output_not_none
)
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.chunk import Chunk
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.serialization.directory import Directory
from src.serialization.directory_factory import DirectoryFactory
from src.utils.data_utils import is_none_or_empty
from src.utils.string_utils import StringUtils


class ChunkLoader(LoggingMixin):
    """
    ChunkLoader class.

    This class provides methods for loading serialized chunks from disk.

    Parameters
    ----------
    language, base_dir and chunk_dir. See details in the __init__ method.

    Attributes
    ----------
    chunks : Dict[int, Chunk]
        Dictionary of all chunks for the current language where the keys are
        the integer numbers of the chunks and the values are the chunks.

    version : str
        The query/prompt variants version set in the SentimentAnalysisConfig
        settings. This attribute  only has a getter. If you need to change
        the version, change the version in the SentimentAnalysisConfig
        settings.

    valid_queries_chunk : Chunk
        A Chunk object with all valid queries combined from all chunks for the
        current language.

    Methods
    -------
    extract_best_queries(self, best_query_nrs: List[str]) -> Chunk:
        Extracts the columns of the best queries into a new chunk.

    """

    def __init__(
            self,
            language: str = '',
            base_dir: str = '',
            chunk_dir: str = 'chunks',
    ):
        """
        Initializes the ChunkLoader with the specified parameters.

        Parameters
        ----------
        language : str
           Language code (default is 'en').

        base_dir : str
           Base directory path (default is '').

        chunk_dir : str
           Chunk directory path (default is 'chunks').

        """

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self._config = SentimentAnalysisConfig()

        self._language: str = ''
        self._set_language(language)

        self._base_dir: Directory = self._set_directory(base_dir)
        self._chunk_dir: Directory = self._set_directory(
            f'{chunk_dir}_v_{self.version}'
        )

        self.chunks: Dict[int, Chunk] = {}
        self._load_chunks()

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

        return self._config.get('version')

    @property
    def valid_queries_chunk(self) \
            -> Chunk:
        """
        Returns the valid columns of the chunks in a single Chunk.

        Assembles the valid columns from all chunks for the current language
        in a single Chunk.

        Returns
        -------
        Chunk
            The Chunk with the valid queries and answers from all the
            chunks for the current language.

        Notes
        -----
        'Invalid' query columns, i.e. columns having no corresponding answer
        column, are discarded in this process.

        """

        joined_chunk = None

        for _, chunk in self.chunks.items():

            valid_chunk = self._remove_invalid_queries(chunk)

            if joined_chunk is None:

                joined_chunk = valid_chunk.copy()

                # Change the joined chunks' name to reflect the character of
                # the joined data collection:
                # Remove the file extension and the last 8 characters from
                # the joined chunks' name.
                joined_chunk.name = (
                    StringUtils.shorten_string_by_n_chars(
                        StringUtils.remove_extension_from_file_name(
                            joined_chunk.name
                        ), 8
                    )
                )

            else:

                joined_chunk = self._add_valid_cols(
                    joined_chunk, valid_chunk)

        return joined_chunk

    # endregion --- Properties

    # region --- Public Methods

    @input_not_none_or_empty("No best query numbers given!")
    @output_not_none("Chunk is None!")
    def extract_best_queries(self, best_query_nrs: List[str]) \
            -> Chunk:
        """
        Extracts the columns of the best queries into a new chunk.

        Extracts the columns of the best queries from all chunks that exist
        for the current language into a new chunk only containing the best
        queries.

        Parameters
        ----------
        best_query_nrs : List[str]
            The string identifiers of the best queries.

        Returns
        -------
        Chunk
            A Chunk containing the query and answer columns of the best
            queries.

        """

        chunk: Chunk | None = None
        processed_chunks: List[int] = []

        self._validate_query_nr_format(best_query_nrs)

        for query_nr in best_query_nrs:
            nr = StringUtils.get_int_behind_last_underscore(query_nr)
            chunk_nr = ceil(nr / self._config.get('chunk_size'))

            # Make sure a chunk is not processed twice
            if chunk_nr in processed_chunks:
                continue

            if is_none_or_empty(chunk):

                # The first processed chunk constitutes a problem,
                # as it is entirely processed without knowing which
                # of the best query numbers are contained.
                processed_chunks.append(chunk_nr)

                chunk = self._extract_first_best_queries(
                    chunk_nr, best_query_nrs
                )

                base_chunk_name = StringUtils.get_str_before_last_underscore(
                    StringUtils.remove_extension_from_file_name(chunk.name)
                )

                chunk.name = f"{base_chunk_name}_1"

            else:
                chunk = self._extract_single_query(nr, chunk_nr, chunk)

                print(chunk)

        return chunk

    # endregion --- Public Methods

    # region --- Protected Methods
    def _validate_query_nr_format(self, best_query_nrs: List[str]) \
            -> None:
        if not StringUtils.all_end_with_underscore_and_numbers(best_query_nrs):
            raise CriticalException(
                self.logger,
                "Query numbers have not the expected format: %s" %
                best_query_nrs
            )

    def _set_language(self, language: str) \
            -> None:

        if is_none_or_empty(language):
            msg = "No language specified! Trying config settings ..."
            self._log(msg, 'info')

            language = self._config.get('language')

            if is_none_or_empty(language):
                msg = "No language found! Using default ..."
                self._log(msg, 'info')

                language = DEFAULT_LANGUAGE

        self._language: str = language

        msg = f"Language set to {language}."
        self._log(msg, 'info')

    def _get_query_cols_names(self, chunk: Chunk) \
            -> List[str]:
        """
        Gets the names of the query columns in a given chunk.

        Parameters
        ----------
        chunk : Chunk
            The chunk whose query columns are to be found.

        Returns
        -------
        List[str]
            The List of the names of the query columns in the given chunk.

        """

        return chunk.do_with_column(
            "get_col_names_by_substring",
            substring="query"
        )

    def _get_answer_cols_names(self, chunk: Chunk) \
            -> List[str]:
        """
        Gets the names of the answer columns in a given chunk.

        Parameters
        ----------
        chunk : Chunk
            The chunk whose answer columns are to be found.

        Returns
        -------
        List[str]
            The List of the names of the answer columns in the given chunk.

        """

        return chunk.do_with_column(
            "get_col_names_by_substring",
            substring="answer"
        )

    def _add_valid_cols(
            self,
            joined_chunks: MyDataFrame,
            valid_chunk: Chunk
    ) -> MyDataFrame:

        substrings = ['query_', 'answer_']

        for substr in substrings:
            extracted_my_df = self._extract_valid_cols_by_substring(
                valid_chunk,
                substr
            )

            joined_chunks.do_with_column(
                "merge",
                other=extracted_my_df
            )

        return joined_chunks

    def _set_directory(self, dir_name: str) \
            -> Directory:
        """
        Sets the directory with the specified directory name.

        Parameters
        ----------
        dir_name : str
            Name of the directory to set.

        Returns
        -------
        Directory
            An instance of the Directory class with the specified directory
            name.

        """
        try:
            return DirectoryFactory.create('csv', dir_name)
        except FileNotFoundError as err:
            msg = (
                    "Have you moved the created chunks to directory %s? (%s)" %
                    (dir_name, str(err))
            )
            self._log(msg, 'error')
            sys.exit()

    def _load_chunks(self):
        """
        Loads chunks with the prompt variants results for the current language.

        Loads chunks with the prompt variants results for the current
        language from the local disk.

        Sets the chunks property of this class.

        """

        chunk_files = self._chunk_dir.file_names

        for file_name in chunk_files:
            if f"_{self._language}_" in file_name:
                chunk = MyDataFrameFactory.create_chunk(name=file_name)
                chunk.file_type = 'csv'
                chunk.serializer.file.path = self._chunk_dir.path
                chunk.load()
                self.chunks[self._get_chunk_nr(file_name)] = chunk

    def _get_chunk_nr(self, file_name: str) \
            -> int:
        """
        Extracts the chunk number from the file name of a chunk.

        Parameters
        ----------
        file_name : str
            The name of the chunk file.

        Returns
        -------
        int
            The number of the chunk.

        """

        return StringUtils.get_int_behind_last_underscore(
            StringUtils.remove_extension_from_file_name(
                file_name
            )
        )

    def _remove_invalid_queries(self, chunk: Chunk) \
            -> Chunk:

        # Keep the original chunk untouched
        valid_chunk = chunk.copy()
        query_cols = self._get_query_cols_names(valid_chunk)
        answer_cols = self._get_answer_cols_names(valid_chunk)

        for query_col in query_cols:
            answer_col = query_col.replace("query", "answer")
            if answer_col not in answer_cols:
                valid_chunk.do_with_column(
                    "drop_column",
                    col_name=query_col
                )

        return valid_chunk

    def _extract_valid_cols_by_substring(
            self,
            valid_chunk: Chunk,
            substr: str
    ) -> MyDataFrame:

        extracted_cols = valid_chunk.do_with_column(
            "extract_columns_by_name_substring",
            substring=substr
        )

        return MyDataFrameFactory.create(extracted_cols)

    def _extract_first_best_queries(
            self, chunk_nr: int, best_query_nrs: List[str]
    ) -> Chunk:

        """
        Extracts the first best_queries.

        Determines the chunk that contains the first of the list of best
        queries, copies the corresponding chunk and removes all query and
        answer columns that do not match the list of best queries. This
        method can lead to multiple elements from the list of best queries
        being processed.

        Parameters
        ----------
        chunk_nr : int
            Number of the chunk in which to look for queries matching the
            best queries.

        Returns
        -------
        Chunk
            A Chunk containing the query and answer columns of the
            specified chunk that match one or more of the best query numbers.

        """

        # Verify that the chunk is correct.
        self._validate_chunk_nr(chunk_nr, best_query_nrs[0])

        # Copy chunk
        chunk = self.chunks[chunk_nr].copy()

        # Remove all query and answer columns that do not match the
        # best query numbers

        query_cols = self._get_query_cols_names(chunk)

        for query_col in query_cols:
            query_col_nr = str(
                StringUtils.get_int_behind_last_underscore(query_col)
            )

            if (f"{self._language}_{query_col_nr}" not in
                    best_query_nrs):
                chunk = self._drop_query_and_answer_column(
                    chunk, query_col_nr
                )

        return chunk

    def _validate_chunk_nr(self, chunk_nr: int, query_nr: str) \
            -> None:
        """
        Checks if the specified chunk exists and contains the specified query.

        Parameters
        ----------
        chunk_nr : int
            The integer chunk number.

        query_nr : str
            The query identifier as a string.

        Raises
        ------
        CriticalException
            If the chunk does not exist or the query is not found in the chunk.

        """

        try:
            chunk = self.chunks[chunk_nr]

        except KeyError:
            msg = (
                    "Chunk n° %d not found! Verify the configuration "
                    "settings. Is the chunk size correct? " % chunk_nr
            )
            self._log(msg, 'error')
            self._config.print()
            sys.exit(1)

        nr = StringUtils.get_int_behind_last_underscore(query_nr)
        if f"query_{nr}" not in chunk.col_names:
            raise CriticalException(
                self.logger,
                "Query n° %s not found in chunk n° %s " % (
                    query_nr, chunk_nr
                )
            )

    def _extract_single_query(
            self,
            query_nr: int,
            chunk_nr: int,
            output_chunk: Chunk
    ) -> Chunk:

        """
        Extracts a query from a chunk to the given chunk.

        Extracts the query and answer column identified by the specified
        number from the chunk identified by the specified chunk number and adds
        the columns to the given output chunk.

        Parameters
        ----------
        query_nr : int
            The number of the query and the answer column to extract from the
            chunk.

        chunk_nr : int
            The number of the chunk from which to extract the query and
            answer columns.

        output_chunk : Chunk
            The chunk in which to assemble the extracted columns.

        Returns
        -------
        Chunk
            The output chunk with the extracted columns added.

        """

        # Verify that the chunk is correct.
        self._validate_chunk_nr(chunk_nr, str(query_nr))

        # Add all query and answer columns that match the best query
        # numbers
        cols_to_extract = [
            f"query_{query_nr}",
            f"answer_{query_nr}",
        ]
        extracted_query_cols = self.chunks[chunk_nr].do_with_column(
            'extract_columns', col_names=cols_to_extract
        )

        output_chunk.do_with_column(
            "merge", other=extracted_query_cols
        )

        return output_chunk

    def _drop_query_and_answer_column(
            self,
            chunk: Chunk,
            query_nr: str
    ) -> Chunk:

        """
        Drops the specified query and answer columns from the chunk.

        Removes the query and answer columns with the specified query number
        from the given chunk.

        Parameters
        ----------
        chunk : Chunk
            A chunk with query and answer columns.

        query_nr : str
            Number in string format by which the query and answer columns to
            drop can be identified.

        Returns
        -------
        Chunk
            The given chunk without the removed query and answer columns.

        """

        col_name = f"query_{query_nr}"
        chunk.do_with_column(
            "drop_column",
            col_name=col_name
        )

        # Check whether an answer column with the current
        # query column number exists at all before trying to
        # drop it (The corresponding query could be an
        # invalid one, not having produced answers worth
        # keeping.)
        col_name = f"answer_{query_nr}"
        if col_name in self._get_answer_cols_names(chunk):
            chunk.do_with_column(
                "drop_column",
                col_name=col_name
            )

        return chunk

    # endregion --- Protected Methods
