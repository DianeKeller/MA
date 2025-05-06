"""
my_data.py
----------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

import operator
from typing import Any, List, no_type_check, Callable

from pandas import Series

from constants import INT
from logger import Logger
from src.data_structures.data_collection import DataCollection
from src.data_structures.my_data_frame import MyDataFrame
from src.decorators.data_decorators import info_requires_data, requires_data
from src.decorators.execution_time_decorator import execution_time
from src.decorators.type_check_decorators import enforce_output_types
from src.nlp.tokenization.tokenization_mixin import TokenizationMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.serialization.data_serialization_mixin import DataSerializationMixin
from src.utils.data_utils import is_none_or_empty
from src.utils.late_imports import LateImports


@no_type_check
class MyData(DataCollection, TokenizationMixin, DataSerializationMixin):
    """
    MyData class.
    
    This class is designed to manage and manipulate data stored in a
    MyDataFrame format. It extends the functionalities of the DataCollection
    class and provides data serialization capabilities through the
    DataSerializationMixin, enabling efficient handling, transformation and
    serialization of data.

    The MyData class facilitates operations on data that may require
    preprocessing steps commonly found in machine learning and data science
    projects, such as adding new columns based on existing data, filtering
    rows based on specific criteria and managing single-value or empty
    columns.

    Key Features:
    
    - Direct manipulation of the MyDataFrame object for dataset-specific
      operations like adding new columns based on text analysis.
      
    - Methods for text length calculation, sentence and word count,
      and column management.

    - Integration of data serialization for efficient data storage and 
      retrieval.
      
    
    Attributes
    ----------
    data MyDataFrame | None
        The data stored in a MyDataFrame format.

    name : str
        A name for the data, providing an identifier for logging
        and tracking purposes.

    source : str
        The source (URL or path) for fetching the data.

    col_names : List[str]
        The column names in the MyDataFrame.

    my_df : MyDataFrame
        The MyDataFrame wrapped in this class.

    n_cols : int
        The number of columns in the MyDataFrame.

    n_rows : int
        The number of rows in the MyDataFrame.


    Methods
    -------
    add_sentence_count_column(tokenization_strategy_name: str = '') -> None:
        Adds a column that counts the number of sentences in the 'text' column.

    add_sentiment_value_column(sentiment_map: dict, source_col: str, 
            target_col: str) -> None:
        Adds a sentiment value column to the data.
    
    add_text_length_column() -> None:
        Adds a text length column to the data.
            
    add_word_count_column(tokenization_strategy_name='') -> None:
        Adds a word count column to the data.
        
    drop_single_value_cols() -> None:
        Removes identified single-value columns to streamline the dataset.

    extract_mydata_columns(col_names: List[str]) -> MyDataFrame:
        Extracts the specified columns from the data to a MyDataFrame.
      
    filter_rows_by_col_value(col_name: str, col_value: Any, op: Callable[[
            Any, Any], bool] = operator.eq) -> MyDataFrame:
        Filters rows in the data based on the specified column value.

    find_single_value_cols() -> None:
        Identifies columns that contain no values or a single value, marking
        them for potential removal.
        
    get_col(col_name: str) -> Series:
        Returns the specified column in the data.
        
    get_unique_values(col_name: str) -> List[Any]:
        Returns the unique values in the specified column.

    has_no_data(verbose: bool = True) -> bool:
        Checks if the data is None or empty.
  
    max_filter(col_name: str, max_value: Any) -> MyDataFrame:
        Filters rows in the data by the given maximum value in the specified 
        column.
    
    min_filter(col_name: str, min_value: Any) -> MyDataFrame:
        Filters the data by the given minimum value in the specified column.
  
    use_data() -> MyDataFrame:
        Returns the data ensuring it is not None.

    Usage
    -----
    >>> ex_my_data = MyData(
    ...     data=ex_my_dataframe, name="My Data",source="Local"
    ... )
    >>> ex_my_data.add_text_length_column()
    >>> ex_filtered_data = ex_my_data.filter_rows_by_col_value(
    ...     column="category", value="news"
    ... )

    """

    # Default name for the column containing the text data
    # Override in the subclasses if necessary
    TEXT_COLUMN_NAME: str = "text"

    # Column names for the computed columns
    LENGTH_COLUMN_NAME: str = "length"
    SENTENCE_COUNT_COLUMN_NAME: str = "n_sentences"
    WORD_COUNT_COLUMN_NAME: str = "n_words"

    # Define format strings for decorators
    DATA_STR: str = "{self.__class__.__name__} data"

    def __init__(
            self,
            data: MyDataFrame | None = None,
            name: str = '',
            source: str = ''
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the MyData class with a MyDataFrame
        collection of data, an identifying name and a source from which 
        to fetch the data.

        Parameters
        ----------
        data : MyDataFrame | None
            The MyDataFrame data wrapped in this class.

        name: str
            A name identifying the data, used for naming files when saving
            the data or information related to it.

        source: str
            The source (Url or file path) where to fetch the data from.

        """

        super().__init__(data, name)

        self.source: str = source

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    # region --- Properties

    @property
    def my_df(self) \
            -> MyDataFrame:
        """
        Returns the MyDataFrame that is wrapped in this class.

        Returns
        -------
        MyDataFrame
            The MyDataFrame wrapped in this class.

        Notes
        -----
        - Especially when referenced from outside this class, this property
          is used rather than the 'data' attribute, which is inherited from the
          'DataCollection' class, to avoid confusion because the MyData
          instance itself may also be 'data' wrapped in other classes. Rather
          than referencing the MyDataFrame by 'data.data', you can reference it
          by 'data.my_df'.

        - Calls the _get_my_df() to enable the use of the requires_data and
          the enforce_output_types decorator.

        """

        return self._get_my_df()

    @my_df.setter
    def my_df(self, my_df: MyDataFrame) \
            -> None:
        """
        Sets the MyDataFrame that is wrapped in this class.
        
        This property references the same object as the data property. It is 
        introduced to make it clearer for the user that the data in this class 
        is a MyDataFrame instance.

        Parameters
        ----------
        my_df : MyDataFrame
            The MyDataFrame to be wrapped in this class.

        Notes
        -----
        Especially from outside this class, use this setter rather than the
        'data' setter to avoid confusion between different 'data' attributes of
        different classes inheriting from the DataCollection class.

        """

        self.data = my_df

    @property
    def n_rows(self) \
            -> int:
        """
        Returns the number of rows in the data.

        Returns
        -------
        int
            The number of rows in the data. Defaults to 0.

        Notes
        -----
        Uses _get_n_rows() to enable the use of the info_requires_data
        decorator and to set the default value for the case that the data
        is None or empty.

        """

        return self._get_n_rows()

    @property
    def n_cols(self) \
            -> int:
        """
        Returns the number of columns in the data.

        Returns
        -------
        int
            The number of columns in the data. Defaults to 0.

        Notes
        -----
        Uses _get_n_cols() to enable the use of the info_requires_data
        decorator and to set the default value for the case that the data
        is None or empty.

        """

        return self._get_n_cols()

    @property
    def col_names(self) \
            -> List[str]:
        """
        Returns the column names in the data.
        
        Returns
        -------
        List[str]
            The names of the columns in the MyDataFrame.
            
        """

        return self._get_col_names()

    # endregion --- properties

    # region --- Public Methods
    def get_col(self, col_name: str) \
            -> Series:
        """
        Returns the specified column from the data.

        Parameters
        ----------
        col_name : str
            The name of the column to return.

        Returns
        -------
        Series
            The specified column from the data.

        """

        return self.my_df.df[col_name]

    @no_type_check
    @execution_time
    def min_filter(self, col_name: str, min_value: Any) \
            -> MyDataFrame:
        """
        Filters the data by the given minimum value in the specified column.
        
        Extracts all rows from the data where the value in a given column
        is greater than or equal to the specified minimum value.

        Parameters
        ----------
        col_name : str
            The name of the column in which to seek for the specified value.

        min_value : Any
            TThe minimum value with which to compare the values in the
            specified column.

        Returns
        -------
        MyDataFrame
            A new MyDataFrame containing the extracted rows.

        """

        return self.filter_rows_by_col_value(col_name, min_value, operator.ge)

    @no_type_check
    @execution_time
    def max_filter(self, col_name: str, max_value: Any) \
            -> MyDataFrame:
        """
        Filters the data by the given maximum value in the specified column.
        
        Extracts all rows from the data where the value in a given column
        is less than or equal to the specified maximum value.

        Parameters
        ----------
        col_name : str
            The name of the column in which to seek for the specified value.

        max_value : Any
            The maximum value with which to compare the values in the
            specified column.

        Returns
        -------
        MyDataFrame
            A new MyDataFrame containing the extracted rows.

        """

        return self.filter_rows_by_col_value(
            col_name, col_value=max_value, op=operator.le
        )

    @no_type_check
    @execution_time
    @requires_data
    def filter_rows_by_col_value(
            self,
            col_name: str,
            col_value: Any,
            op: Callable[[Any, Any], bool] = operator.eq
    ) -> MyDataFrame:
        """
        Extracts rows by the specified value in the specified column.
        
        Extracts all rows from the data where the value in a given column
        fulfills the specified condition.

        Parameters
        ----------
        col_name : str
            The name of the column in which to seek for the specified value.

        col_value : Any
            The value for which to seek in the specified column

        op : Callable[[Any, Any], bool]
            The comparison operator to use for the filter ,  e.g.:
            - operator.lt for <,
            - operator.gt for >,
            - operator.le for <=,
            - operator.ne for !=,
            - operator.eq for ==,
            - operator.ge for >=.

            Defaults to operator.eq.

        Returns
        -------
        MyDataFrame
            A new MyDataFrame containing the extracted rows.

        """

        msg = ("Trying to extract data subset from data set '%s' with value "
               "'%s' in column '%s'." % (self.name, col_value, col_name))
        self._log(msg, 'info')

        filtered_df = self.data.do_with_row(  # type: ignore
            'extract_rows_by_col_value',
            col_name=col_name,
            col_value=col_value,
            op=op
        )

        if filtered_df.empty:
            msg = ("'%s' not found in column '%s'. " % (col_value, col_name) +
                   "Have you provided the correct column name and value?")
            self._log(msg, 'error')
            raise KeyError(msg)

        # Prevent circular import
        my_dataframe_factory_cls = LateImports.get_my_dataframe_factory_class()

        my_df = my_dataframe_factory_cls().create(filtered_df)

        msg = "Data subset successfully extracted."
        self._log(msg, 'info')

        return my_df

    @no_type_check
    @requires_data
    def extract_mydata_columns(
            self,
            col_names: List[str],
    ) -> MyDataFrame:
        """
        Extracts the specified columns from the data to a MyDataFrame.

        Parameters
        ----------
        col_names : List[str]
            The names of the columns to extract.

        Returns
        -------
        MyDataFrame
            A new MyDataFrame containing the extracted columns.

        """

        msg = ("Trying to extract data columns %s from data set '%s'." % (
            col_names, self.name
        ))
        self._log(msg, 'info')

        extracted_df = self.data.do_with_column(
            "extract_columns",
            col_names=col_names
        )

        if extracted_df.empty:
            msg = "Columns not found in data set '%s'." % self.name
            self._log(msg, 'error')
            raise KeyError(msg)

        # Prevent circular import
        my_dataframe_factory_cls = LateImports.get_my_dataframe_factory_class()
        my_df = my_dataframe_factory_cls().create(extracted_df)

        msg = "Data subset successfully extracted."
        self._log(msg, 'info')

        return my_df

    @no_type_check
    @requires_data
    def get_unique_values(self, col_name: str) \
            -> List[Any]:
        """
        Returns the unique values in the specified column.

        Parameters
        ----------
        col_name : str
            The name of the column in which to seek for the unique values.

        Returns
        -------
        List[Any]
            The unique values in the specified column. Empty list if there
            are no data.

        Raises
        ------
        CriticalException
            - If the DataFrame in the MyDataFrame object is empty.
            - If the column name is not found in the DataFrame.

        """

        if col_name not in self.col_names:
            raise CriticalException(
                self.logger,
                "Column '%s' not found in the data! " % col_name +
                "Cannot get unique values."
            )

            # Get the unique values from the first split.
        unique_values = self.data.df[col_name].unique().tolist()

        return unique_values

    @no_type_check
    @execution_time
    def find_single_value_cols(self) \
            -> None:
        """
        Finds single-value columns.
        
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

        self.single_value_cols = self.my_df.find_single_value_cols

    @no_type_check
    @requires_data
    @execution_time
    def drop_single_value_cols(self) \
            -> None:
        """
        Removes all columns from the MyDataFrame that have no informational
        value.

        Empty columns and columns that only have one single value across the
        dataset are dropped.

        """
        # Make sure the dataframe contains data

        self.my_df.drop_single_value_cols()

    @no_type_check
    @requires_data
    def add_text_length_column(self) \
            -> None:
        """
        Adds a text length column to the DataFrame.

        Adds a column to the DataFrame that stores the length of the text
        from the 'text' column.

        Notes
        -----
        The DataFrame is modified in place and is not returned from this
        method.

        """

        self.data.df[self.LENGTH_COLUMN_NAME] = (
            self.data.df[self.TEXT_COLUMN_NAME].str.len()
        )

    @no_type_check
    @requires_data
    def add_sentiment_value_column(
            self,
            sentiment_map: dict,
            source_col: str,
            target_col: str
    ) -> None:
        """
        Adds a sentiment value column to the data.

        Adds a column to the data that stores the sentiment value
        of the categorical sentiment polarity column
        (see CATEGORICAL_SENTIMENT_POLARITY_COLUMN_NAME) in a numerical form.

        Parameters
        ----------
        sentiment_map : dict
            A dictionary that maps the categorical sentiment polarity
            to the numerical sentiment value.

        source_col : str
            The name of the column in the data that contains the
            categorical sentiment polarity.

        target_col : str
            The name of the column in the data that will contain
            the numerical sentiment value.

        Notes
        -----
        - The data is modified in place and is not returned from this
          method.

        - The 'requires_data' decorator is used to ensure that the
          data is not empty before adding the sentiment value column.
          Therefore, type checking is not needed here.

        """

        # Map the sentiment string values to the numerical values stripping
        # the source strings before their comparison with the map.
        self.data.df[target_col] = (
            self.data.df[source_col].str.strip().map(sentiment_map)
        )

        self.data.df[target_col] = self.data.df[target_col].astype(INT)

    @no_type_check
    @requires_data
    def add_sentence_count_column(self, tokenization_strategy_name: str = '') \
            -> None:
        """
        Adds a sentence count column to the DataFrame.

        Adds a column to the DataFrame that stores the number of sentences
        contained in the 'text' column. The sentence count is performed using
        the specified sentence tokenization strategy.

        Parameters
        ----------
        tokenization_strategy_name : str
            The identifying first part of the name of the sentence
            tokenization strategy to use, e.g. "RegexWithColons" for
            RegexWithColonsSentenceStrategy. Defaults to an empty string.

        Notes
        -----
        - If no tokenization strategy name is provided, the sentence
          tokenizer will use the default sentence tokenization strategy
          specified in the TokenizationMixin class.

        - The DataFrame is modified in place and is not returned from this
          method.

        """

        self.set_sentence_tokenizer(tokenization_strategy_name)

        self.data.df[self.SENTENCE_COUNT_COLUMN_NAME] = \
            (
                self.data.df[self.TEXT_COLUMN_NAME].apply(
                    lambda x: len(self.sentence_tokenizer.tokenize(x))
                )
            )

    @no_type_check
    @requires_data
    def add_word_count_column(self, tokenization_strategy_name='') \
            -> None:
        """
        Adds a word count column to the data wrapped in the Mydataframe.

        Adds a column to the DataFrame that stores the number of words
        contained in the 'text' column.

        This method contains the actual implementation of the
        add_word_count_column method required by the DataSourceStrategy
        class's children because the way to add columns to the data depends
        on the specific kind of data structure the column is to be added to.

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

        - The DataFrame is modified in place and is not returned from this
          method.

        """

        self.set_word_tokenizer(tokenization_strategy_name)

        self.data.df[self.WORD_COUNT_COLUMN_NAME] = \
            (
                self.data.df[self.TEXT_COLUMN_NAME].apply(
                    lambda x: len(self.word_tokenizer.tokenize(x))
                )
            )

    @no_type_check
    @requires_data
    def use_data(self) \
            -> MyDataFrame:
        """
        Returns the data ensuring it is not None.
        
        """

        return self.data

    @no_type_check
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

        Notes
        -----
        This method implements the corresponding abstract method in the
        DataCollection interface.

        """

        no_data = (is_none_or_empty(self.data) or
                   self.data.has_no_data(verbose=False))

        if no_data and verbose:
            msg = "No data! Cannot execute operation."
            self._log(msg, "warning")

        return no_data

    # endregion --- Public Methods

    # region --- Protected Methods

    @no_type_check
    @requires_data
    @enforce_output_types
    def _get_my_df(self) \
            -> MyDataFrame:
        """
        Returns the actual MyDataFrame that is wrapped in this class.

        Returns
        -------
        MyDataFrame
            The MyDataFrame wrapped in this class.

        Notes
        -----
        Especially when referenced from outside this class, this property
        is used rather than the 'data' attribute, which is inherited from the
        'DataCollection' class, to avoid confusion because the MyData
        instance itself may also be 'data' wrapped in other classes. Rather
        than referencing the MyDataFrame by 'data.data', you can reference it
        by 'data.my_df'.

        """

        return self.data

    @no_type_check
    @info_requires_data(int(0))
    def _get_n_rows(self) \
            -> int:
        """
        Returns the number of rows in the data.

        Returns the n_rows property of the MyDataFrame object wrapped in
        this class.

        Returns
        -------
        int
            The number of rows in the data. Defaults to 0.

        Notes
        -----
        The 'info_requires_data' decorator guarantees that the data is set
        and is not None. Therefore, type checking is not needed here.

        """

        return self.data.n_rows

    @no_type_check
    @info_requires_data(int(0))
    def _get_n_cols(self) \
            -> int:
        """
        Returns the number of columns in the data.

        Returns the n_cols property of the MyDataFrame object wrapped in
        this class.

        Returns
        -------
        int
            The number of rows in the data. Defaults to 0.

        Notes
        -----
        - The 'info_requires_data' decorator guarantees that the data is set
          and is not None. Therefore, type checking is not needed here.

        """

        return self.data.n_cols

    @no_type_check
    @info_requires_data([])
    def _get_col_names(self) \
            -> List[str]:
        """
        Returns the column names in the data.

        Returns the columns property of the DataFrame in the MyDataFrame
        object that is wrapped in this class.

        Returns
        -------
        List[str]
            The column names in the data. Defaults to an empty list.

        Notes
        -----
        The 'info_requires_data' decorator guarantees that the data is set
        and is neither None nor empty. Therefore, type checking is not needed
        here.

        """

        return self.data.df.columns.tolist()

    # endregion --- Protected Methods
