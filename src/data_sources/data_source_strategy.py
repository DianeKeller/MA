"""
data_source_strategy.py
-----------------------
Version 1.0, updated on 2025-05-01

"""

from abc import ABC, abstractmethod
from typing import TypeVar, Any, List

from logger import Logger
from src.data_sources.data_source_subset_stats import DataSourceSubsetStats
from src.logging_mixin import LoggingMixin

T = TypeVar('T', bound='DataSourceStrategy')
D = TypeVar('D', bound='DataCollection')


class DataSourceStrategy(ABC, LoggingMixin):
    """
    Abstract base class for data source strategies.

    Serves as a blueprint for concrete data source strategies. Defines
    properties and methods for the management and the manipulation of data
    collections that the concrete data source strategies must implement.


    Attributes
    ----------
    logger : Logger
        The logger instance used for logging within the data source strategy
        subclasses.


    Abstract Attributes
    -------------------
    data : D
        The data in the current strategy.

    base_description : str
        The base description of the data in its current strategy.

    language : str
        The language of the data.

    alphabet : List[str]
        The alphabet used in the data.


    Abstract Methods
    ----------------
    add_columns() -> None:
        Adds new computed columns to the data collection.

    add_text_length_column() -> None:
        Adds a text length column to the data.

    add_word_count_column(tokenization_strategy_name='') -> None:
        Adds a word count column to the data.

    create_subset_stats_instance()  -> DataSourceSubsetStats:
        Creates an instance of a SubsetStats class for the current strategy.

    extract_columns(subset_name_extension: str, col_names: List[str]) -> T:
        Extracts a subset of the data containing only the specified columns.

    """

    def __init__(self):
        """
        Initializes common attributes.
        """

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    # region --- Properties

    @property
    @abstractmethod
    def data(self) \
            -> D:
        """
        Gets the data in the current strategy.

        Returns
        -------
        D
            The data. Its concrete type depends on the type of DataCollection
            the current strategy uses to store the data.

        """

    @property
    @abstractmethod
    def base_description(self) \
            -> str:
        """
        Gets the base description of the data in its current strategy.

        The base description is the basic description for any data stored in an
        instance of a class that implements the DataCollection class. It is
        passed from the current MMS strategy to the MmsStrategy base class
        at the moment of initialization. It includes information about:

        - the type of the data,
        - the name of the data,
        - the number of rows and columns,
        - the column names,
        - the names and values of the single-value columns dropped.

        Returns
        -------
        str
            The base description of the data in its current strategy.

        Notes
        -----
        The base description is originally the content of the __str__ method in
        the DataCollection class, but it may have been overridden by the
        inheriting classes. For example, the MyDatasetDict class adds to it
        information about the number and the names of the splits contained
        in the class's DatasetDict data structure before it passes the base
        description on to the MmsStrategy base class.

        """

    @property
    @abstractmethod
    def language(self) \
            -> str:
        """
        Gets the language of the data.

        Returns
        -------
        str
            The language code of the data.

        """

    @language.setter
    @abstractmethod
    def language(self, language: str) \
            -> None:
        """
        Sets the language of the data.
        """

    @property
    def alphabet(self) \
            -> List[str]:
        """
        Returns the alphabet used in the data.

        Returns
        -------
        List[str]
            The alphabet used in the data.

        """

        return self.data.alphabet

    # endregion --- properties

    # region --- Abstract Methods

    @abstractmethod
    def add_columns(self) \
            -> None:
        """
        Adds new computed columns to the data collection.

        Adds new computed columns such as a text length column, a word count
        column, and a sentence count column.

        Notes
        -----
        The modified data is not returned. Instead, the data in the class
        instance is modified in place.

        """

    @abstractmethod
    def add_text_length_column(self) \
            -> None:
        """
        Adds a text length column to the data.

        Adds a column to the data that stores the length of the text
        from the 'text' column.

        Notes
        -----
        The data is modified in place and is not returned from this
        method.

        """

    @abstractmethod
    def add_word_count_column(self, tokenization_strategy_name='') \
            -> None:
        """
        Adds a word count column to the data.

        Adds a column to the data that stores the number of words
        contained in the 'text' column.

        Parameters
        ----------
        tokenization_strategy_name : str
            The identifying first part of the name of the word tokenization
            strategy to use, e.g. "NoPunctuation" for the
            NoPunctuationStrategy. Defaults to an empty string.

        Notes
        -----
        - If no tokenization strategy name is provided, the word tokenizer
          will use the default word tokenization strategy specified in the
          TokenizationMixin class.

        - The data is modified in place and is not returned from this
          method.

        """

    @abstractmethod
    def create_subset_stats_instance(self: T) \
            -> DataSourceSubsetStats:
        """
        Creates an instance of a SubsetStats class for the current strategy.

        Creates an instance of a concrete implementation of the SubsetStats
        class for the current strategy.

        Returns
        -------
        DataSourceSubsetStats
            An instance of the SubsetStats class.

        """

    @abstractmethod
    def extract_columns(
            self: T,
            subset_name_extension: str,
            col_names: List[str]
    ) -> T:
        """
        Extracts a subset of the data containing only the specified columns.

        Parameters
        ----------
        subset_name_extension : str
            The string by which the data's name will be extended to form the
            subset's name.

        col_names : List[str]
            The names of the columns to include in the subset.

        Returns
        -------
        T
            A new DataSourceStrategy instance containing the extracted
            subset.

        """

    @abstractmethod
    def _extract_subset(
            self,
            subset_name_extension: str,
            col_name: str,
            col_value: Any
    ) -> T:
        """
        Extracts a subset of the data filtered by a given column value.

        Parameters
        ----------
        subset_name_extension : str
            The string by which the data's name will be extended to form the
            subset's name.

        col_name : str
            The name of the column in which to seek for the specified value.

        col_value : Any
            The value for which to seek in the specified column

        Returns
        -------
        T
            A new DataSourceStrategy instance containing the extracted
            subset.

        """

    # endregion --- Abstract Methods
