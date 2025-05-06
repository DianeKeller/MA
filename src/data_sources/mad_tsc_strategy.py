"""
mad_tsc_strategy.py
-------------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

import os
from typing import no_type_check, List, Any

from pandas import DataFrame

from src.authentication.local_strategy import LocalStrategy
from src.data_sources.data_source_strategy import DataSourceStrategy, T, D
from src.data_sources.mad_tsc_fact_sheet_mixin import MadTscFactSheetMixin
from src.data_sources.mad_tsc_subset_stats import MadTscSubsetStats
from src.data_structures.my_data import MyData
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.decorators.data_check_decorators import requires_property
from src.decorators.data_decorators import requires_data
from src.decorators.execution_time_decorator import execution_time
from src.decorators.type_check_decorators import enforce_input_types
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty
from src.utils.print_utils import DOUBLE_LINE, SEPARATOR


class MadTscStrategy(
    MyData,
    DataSourceStrategy,
    MadTscFactSheetMixin
):
    """
    MadTscStrategy class.

    Attributes
    ----------
    WORD_TOKENIZATION_STRATEGY : str
        The default strategy for word tokenization.

    SENTENCE_TOKENIZATION_STRATEGY : str
        The default strategy for sentence tokenization.

    TEXT_COLUMN_NAME : str
        The name of the column containing the text data. Overrides the
        constant in the MyData class.

    SPLIT_COLUMN_NAME : str
        The name of the column that indicates the data split
        (e.g., train/test).

    GID_COLUMN_NAME : str
        The name of the column containing the primary GID.

    TARGETS_COLUMN_NAME : str
        The name of the column containing the targets.

    TEXT_DUPLICATES_COUNT_COLUMN_NAME : str
        The name of the column for storing the count of text duplicates.

    TARGET_COUNT_COLUMN_NAME : str
        The name of the column for storing the count of targets in a row.

    FROM_COLUMN_NAME : str
        The name of the column for storing the 'from' field of the target.

    TO_COLUMN_NAME : str
        The name of the column for storing the 'to' field of the target.

    MENTION_COLUMN_NAME : str
        The name of the column for storing the 'mention' field of the target.

    NUMERICAL_SENTIMENT_POLARITY_COLUMN_NAME : str
        The name of the column for storing the numerical sentiment polarity.

    POSITIVE : int
        The constant value representing positive sentiment.

    NEGATIVE : int
        The constant value representing negative sentiment.

    NEUTRAL : int
        The constant value representing neutral sentiment.

    name : str
        The name of the strategy.

    split_type : str
        The type of split the data in the current strategy represents
        (e.g., train, test).

    data : D | None
        The data of the strategy.

    base_description : str
        The base description of the data in the current strategy.

    language : str
        The language code of the data.

    n_rows_with_multiple_targets : int
        The number of rows with multiple targets. Computed property without
        setter.


    Methods
    -------
    add_columns() -> None:
        Adds new computed columns to the data collection.

    add_text_length_column() -> None:
        Adds a text length column to the DataFrame.

    add_word_count_column(tokenization_strategy_name: str = '') -> None:
        Adds a word count column to the DataFrame.

    are_cols_identical(col_name, other, other_col_name) -> bool:
        Checks if columns in the current data and another subset are identical.

    create(subsets: List[MadTscStrategy]) -> None:
        Creates the data in the current strategy by joining the subsets.

    create_subset_stats_instance() -> MadTscSubsetStats:
        Creates an instance of MadTscSubsetStats for the current strategy.

    extract_columns(subset_name_extension, col_names) -> MadTscStrategy:
        Extracts a subset of the data containing only the specified columns.

    filter_by_split(split_type: str) -> MadTscStrategy:
        Filters the data by the specified split type.

    get_original_file_name() -> str:
        Gets the original file name of the data.

    join(subset: MadTscStrategy) -> None:
        Joins the data columns in the subset with the current data.

    load() -> None:
        Loads the data from its local storage location.

    preprocess() -> None:
        Preprocesses the data in the current strategy.

    set_index(col_name: str) -> None:
        Sets the index of the data in the current strategy.

    to_string() -> str:
        Provides a formatted string representation of the data in the current
        strategy.

    """

    WORD_TOKENIZATION_STRATEGY: str = 'NoPunctuation'
    SENTENCE_TOKENIZATION_STRATEGY: str = 'RegexWithColons'

    # Name of the column containing the text data
    # Overrides the constant definition in the MyData class
    TEXT_COLUMN_NAME = "sentence_normalized"
    SPLIT_COLUMN_NAME: str = 'original_file'

    # Other existing column names
    GID_COLUMN_NAME: str = 'primary_gid'
    TARGETS_COLUMN_NAME: str = 'targets'

    # New column names
    TEXT_DUPLICATES_COUNT_COLUMN_NAME: str = 'n_duplicates'
    TARGET_COUNT_COLUMN_NAME: str = 'n_targets'
    FROM_COLUMN_NAME: str = 'from'
    TO_COLUMN_NAME: str = 'to'
    MENTION_COLUMN_NAME: str = 'mention'
    NUMERICAL_SENTIMENT_POLARITY_COLUMN_NAME: str = 'polarity'

    # Sentiment polarity values
    POSITIVE: int = 6
    NEGATIVE: int = 2
    NEUTRAL: int = 4

    def __init__(
            self,
            name: str = '',
            data: D | None = None,
            source: str = '',
            base_description: str = ''
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the MadTscStrategy class with the
        provided parameters.

        Parameters
        ----------
        name : str
            The name of the MAD-TSC strategy. Defaults to an empty string.

        data : D
            The data of the strategy. Defaults to None.

        source : str
            The source path of the strategy. Defaults to an empty string.

        base_description : str
            The base description of the data in the current strategy.

        """

        DataSourceStrategy.__init__(self)
        MyData.__init__(self, data, name, source)

        self._split_type = ''
        self.__base_description: str = base_description
        self.__language: str = ''

        # Set the authentication strategy for fetching the original data
        self.auth_strategy: LocalStrategy = LocalStrategy('jsonl')

        # Set the file type and file name for saving and loading the
        # previously processed data.
        self.file_name = self.name
        self.file_type = 'pkl'

    # region --- Properties

    @property
    def name(self) \
            -> str:
        return self._name

    @name.setter
    def name(self, name: str) \
            -> None:
        self._name = name
        self.file_name = name

    @property
    def split_type(self) \
            -> str:
        """
        Gets the split type the data in the current strategy represents.

        """

        return self._split_type

    @split_type.setter
    def split_type(self, split_type: str) \
            -> None:
        """
        Sets the split type.

        Sets the type of split that the data in the current strategy
        represents, e.g. 'train', 'val' or 'test'.

        Parameters
        ----------
        split_type : str
            The split type to set.

        """

        self._split_type = split_type

    @property
    def data(self) \
            -> D | None:
        """
        Gets the data in the current strategy.

        Gets the data from the MyData parent.

        Returns
        -------
        D
            The data in the current strategy.

        """

        return self._data

    @data.setter
    def data(self, data: D | DataFrame | None) \
            -> None:
        """
        Sets the data.

        Sets the data in this class's parent "MyData" class.

        Parameters
        ----------
        data : D | DataFrame | None
            The data to set.

        Notes
        ------
        Uses the '_set_data' method to enable the use of the
        enforce_input_types decorator.

        """

        self._set_data(data)

    @property
    def base_description(self) \
            -> str:
        """
        Gets the base description of the data in its current strategy.

        The base description is the basic description for any data stored in an
        instance of a class that implements the DataCollection class. It is
        passed from the current MadTsc strategy to the MadTscStrategy base
        class at the moment of initialization. It includes information about:

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

        return self.__base_description

    @property
    def language(self) \
            -> str:
        """
        Gets the language of the data.

        Returns
        -------
        str
            The language code of the data.

        """

        return self.__language

    @language.setter
    def language(self, language: str) \
            -> None:
        """
        Sets the language and the source of the data.

        As the original JSONL files are stored in language-specific folders
        named after the language code, the source is set to the language
        code when the language is set.

        """

        self.__language = language
        self.set_source()

    @requires_property('language')
    def set_source(self) \
            -> None:
        """
        Sets the source of the data.

        As the original files are stored in language-dependent subdirectories
        of a local directory, the source is composed of the local directory
        and the subdirectory corresponding to the language of the
        current strategy.

        """

        self.source = os.path.join(self.ORIG_DIR, self.language)

    @property
    def n_rows_with_multiple_targets(self) \
            -> int:
        """
        Gets the number of rows with multiple targets.

        Returns
        -------
        int
            The number of rows with multiple targets.

        """

        return self._get_rows_with_multiple_targets().shape[0]

    # endregion --- Properties

    # region --- Public Methods

    @requires_property('name')
    def get_original_file_name(self) \
            -> str:
        """
        Gets the original file name of the data.

        Gets the name of the original file from which to fetch the data.

        Returns
        -------
        str
            The original file name of the data.

        """

        return self.name

    def load(self):
        """
        Loads the data from its local storage location into the DatasetDict.

        Uses the load_if_possible method provided by the DataSerializationMixin
        in the MyData parent class to load the data.

        Notes
        -----
        The loaded data is not returned but stored in the "data" property.

        """

        self.load_if_possible()

    def create(self, subsets: List[MadTscStrategy]) \
            -> None:
        """
        Creates the data in the current strategy.

        Creates the data in the current strategy by joining the subsets loaded
        from the original files.

        Parameters
        ----------
        subsets : List[T]
            The subsets of the data to be joined.

        Notes
        -----
        - For each subset, the original file name is stored in the
          'original_file' column, providing additional information, if needed,
          regarding

              - the topic of the samples (e.g., ''london', 'rio')
              - the news outlet from which the samples were collected (e.g.,
                'bbc', 'globo')

        - The 'original' file names are the file names used in this project
          to store and use the original data files. They differ from the file
          names of the original files downloaded from their online sources.
          They were re-named for more clarity and convenience in this project.
          Here is the list of file names as used in this project compared to
          the online sources:

        - The unchanged files from the online sources are stored in the ZIP
          files in the 'original_files' subfolders of the xls dataset
          directories.

        - The created data is stored in the 'data' attribute of the current
          strategy. It is up to the caller to save the composed data.

        """

        for subset in subsets:

            # Fetch the data from the original files:
            subset.fetch()

            # Subset.data is guaranteed to be a MyDataFrame or None because
            # it was set using its setter. The use_data() method guarantees
            # the data is not None.
            my_df = subset.use_data()

            # Add a column with the original file name to keep the
            # information it provides:
            my_df.do_with_column(
                'add_column',
                data=subset.name,
                col_name='original_file'
            )

            # Join the data of the different files in one data subset
            if self.data is None:
                self.data = my_df
            else:
                self.data.do_with_row('add_rows', data=my_df.df)

    def join(self, subset: MadTscStrategy) \
            -> None:
        """
        Joins the data columns in the subset with the current data.

        Joins each of the the data columns in the subset with the current data
        provided that the data column's values are not identical with those of
        the corresponding column from the first subset that was used
        as the base of the combined subset (i.e., the '_de' subset).


        Parameters
        ----------
        subset : T
            The subset to be joined.

        """

        for col_name in subset.my_df.col_names:
            if not self.are_cols_identical(
                f'{col_name}_de',
                subset,
                col_name
            ):
                self.my_df.do_with_column(
                    'add_column',
                    data=subset.my_df.df[col_name],
                    col_name=f'{col_name}_{subset.language}'
                )

    def are_cols_identical(
            self,
            col_name: str,
            other: MadTscStrategy,
            other_col_name: str
    ) -> bool:
        """
        Checks if columns in the current data and another subset are identical.

        Checks if the specified columns in the current data and another subset
        are identical.

        Parameters
        ----------
        col_name : str
            The name of the column in the current data.

        other : MadTscStrategy
            The other strategy to compare with.

        other_col_name : str
            The name of the column in the other strategy.

        Returns
        -------
        bool
            True if the columns are identical, False otherwise.

        """

        return self.my_df.do_with_column(
            "are_cols_identical",
            col_name=f'{col_name}',
            other=other.my_df,
            other_col_name=other_col_name
        )

    def create_subset_stats_instance(self) \
            -> MadTscSubsetStats:
        """
        Creates an instance of MadTscSubsetStats for the current strategy.

        Returns
        -------
        MadTscSubsetStats
            An instance of the MadTscSubsetStats class.

        """

        return MadTscSubsetStats(self)

    def preprocess(self) \
            -> None:
        """
        Preprocesses the data in the current strategy.

        Notes
        -----
        The modified data is not returned. Instead, the data in the class
        instance is modified in place.

        """

        msg = "Adding target count column to the data..."
        self._log(msg, 'info')

        self._ensure_no_duplicate_gids()
        self.set_index(self.GID_COLUMN_NAME)
        self._add_text_duplicates_count_column()

        self._extract_target_details()

    @no_type_check
    @requires_data
    def set_index(self, col_name: str) \
            -> None:
        """
        Sets the index of the data in the current strategy.

        Parameters
        ----------
        col_name : str
            The name of the column to be used as index.

        Notes
        -----
        The modified data is not returned. Instead, the data in the class
        instance is modified in place.

        """

        self.data.index_column = col_name

    def add_columns(self) \
            -> None:
        """
        Adds new computed columns to the data collection.

        Adds new computed columns such as a text length column, and a word
        count column.

        Notes
        -----
        The modified data is not returned. Instead, the data in the class
        instance is modified in place.

        """

        # Add columns with text length and word count
        msg = "Adding text length column to the data..."
        self._log(msg, 'info')

        self.add_text_length_column()

        msg = "Adding sentence count column to the data..."
        self._log(msg, 'info')

        self.add_sentence_count_column(self.SENTENCE_TOKENIZATION_STRATEGY)

        msg = "Adding word count column to the data..."
        self._log(msg, 'info')

        self.add_word_count_column(self.WORD_TOKENIZATION_STRATEGY)

    @execution_time
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

        MyData.add_text_length_column(self)

    @execution_time
    def add_word_count_column(self, tokenization_strategy_name='') \
            -> None:
        """
        Adds a word count column to the DataFrame.

        Adds a column to the DataFrame that stores the number of words
        contained in the 'text' column.

        This method delegates the task of implementing the parent's
        corresponding abstract method to the specific data structure
        ('MyData') this class is implementing.

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

        MyData.add_word_count_column(self, tokenization_strategy_name)

    def extract_columns(
            self,
            subset_name_extension: str,
            col_names: List[str]
    ) -> MadTscStrategy:
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
        MadTscStrategy
            A Subset of the same type as the current strategy.

        """

        subset_name = f"{self.name}{subset_name_extension}"

        return MadTscStrategy(
            subset_name, self.extract_mydata_columns(col_names)
        )

    def filter_by_split(self: T, split_type: str) \
            -> T:
        """
        Filters the data by the specified split type.

        Parameters
        ----------
        split_type : str
            The name of the split type to filter by.

        Returns
        -------
        T
            The extracted subset of the data as another instance of the same
            class as the current class.

        """

        subset_name_extension = f"_{split_type}"

        if self.SPLIT_COLUMN_NAME in self.col_names:
            split_col_name = self.SPLIT_COLUMN_NAME
        else:
            split_col_name = self.SPLIT_COLUMN_NAME + '_de'

        # Dynamically create an instance of the same class
        subset = self._extract_subset(
            subset_name_extension,
            split_col_name,
            split_type
        )

        subset.split_type = split_type

        return subset

    def to_string(self) \
            -> str:
        """
        Provides a formatted string representation of the data in the current
        MMS strategy.

        Expands the base description by MMS specific details like the name
        and source of the data collection, the author(s) of the collection
        and the citation of the associated scientific paper. If the MMS data
        is not yet initialized, the description includes statistical insights
        such as the numbers and names of the domains, languages and original
        datasets contained in the data.

        Returns
        -------
        str
           A string representation of the data in the current MMS strategy.

        """

        if is_none_or_empty(self.data):
            return self.DESCRIPTION

        return (
            f"{SEPARATOR} \n"
            f"Language: {self.language} ({self.name}) \n"
            f"{DOUBLE_LINE} \n"
            f"{self.data} \n\n"
            f"{self.data.df.describe()} \n"
            f"{SEPARATOR} \n"
        )

    # endregion --- Public Methods

    # region --- Protected Methods

    @enforce_input_types
    def _set_data(self, data: D | DataFrame | None) \
            -> None:
        """
        Sets the data property enforcing the data is of type D.

        Parameters
        ----------
        data : D | DataFrame | None
            The data to set.

        Notes
        -----
        - Sets the value of the _data variable provided by the 'MyData'
          parent's parent class, 'DataCollection'.

        - Uses the 'enforce_input_types' decorator to ensure that the input
          data is of type D, DataFrame or None. If it is a simple
          pandas DataFrame, it is wrapped in a MyDataFrame, so that _data is
          guaranteed to be of type MyDataFrame or None.

        - The input data comes in a simple pandas DataFrame format when
          loaded from a file using the PKL serialization strategy.

        """
        if isinstance(data, DataFrame):
            self._data = MyDataFrameFactory.create(data)
        else:
            self._data = data

    @no_type_check
    @requires_data
    def _get_rows_with_multiple_targets(self) \
            -> DataFrame:
        """
        Gets rows with multiple targets.

        Returns
        -------
        DataFrame
            A DataFrame containing the rows with multiple targets.

        """
        return self.data.df[self.data.df[self.TARGET_COUNT_COLUMN_NAME] > 1]

    @no_type_check
    @requires_data
    def _get_duplicate_gids(self) \
            -> DataFrame:
        return self.data.df[self.data.df[
            self.GID_COLUMN_NAME].duplicated(keep=False)]

    @no_type_check
    @requires_data
    def _get_duplicate_texts(self) \
            -> DataFrame:

        return self.data.df[self.data.df[
            self.TEXT_COLUMN_NAME].duplicated(keep=False)]

    def _ensure_no_multiple_targets(self) \
            -> None:
        """
        Ensures that there is only one target per row.

        Creates a temporary column that counts the numbers of targets
        in the 'targets' column. Uses the n_rows_with_multiple_targets property
        to check for rows with multiple targets. If there are any, a ValueError
        is raised.

        """

        self._add_target_count_column()

        if self.n_rows_with_multiple_targets > 0:
            raise CriticalException(self.logger,
                                    'Found rows with multiple targets: %s' % (
                                        self.n_rows_with_multiple_targets
                                    ))

    def _extract_subset(
            self,
            subset_name_extension: str,
            col_name: str,
            col_value: Any
    ) -> MadTscStrategy:
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
        MadTscStrategy
            A new MadTscStrategy instance containing the extracted subset.

        Notes
        -----
        This method implements the corresponding abstract method in the
        DataSourceStrategy interface.

        """
        subset_name = f"{self.name}{subset_name_extension}"

        return MadTscStrategy(
            subset_name, self.filter_rows_by_col_value(col_name, col_value)
        )

    @no_type_check
    @requires_data
    def _add_target_count_column(self) \
            -> None:
        """
        Adds a target count column to the DataFrame.

        Adds a column to the DataFrame that stores the number of targets
        contained in the 'targets' column.

        Notes
        -----
        - The DataFrame is modified in place and is not returned from this
          method.

        """

        self.data.df[self.TARGET_COUNT_COLUMN_NAME] = \
            (
                self.data.df[self.TARGETS_COLUMN_NAME].apply(
                    lambda x: len(x)
                )
            )

    def _add_target_detail_columns(self) \
            -> None:
        """
        Adds columns for categories extracted from the targets column.

        Adds separate columns to the DataFrame extracting the values from
        the targets column.

        Notes
        -----
        - The DataFrame is modified in place and is not returned from this
          method.

        """
        self._add_target_detail_column('from', self.FROM_COLUMN_NAME)
        self._add_target_detail_column('to', self.TO_COLUMN_NAME)
        self._add_target_detail_column(
            'mention', self.MENTION_COLUMN_NAME
        )
        self._add_target_detail_column(
            'polarity', self.NUMERICAL_SENTIMENT_POLARITY_COLUMN_NAME
        )

    @no_type_check
    @requires_data
    def _add_target_detail_column(self, category: str, col_name: str) \
            -> None:
        """
        Adds a target detail column for the specified category.

        Parameters
        ----------
        category : str
            The name of the category to add the target detail column for.

        col_name : str
            The name of the target detail column to add.

        """

        self.data.df[col_name] = \
            (
                self.data.df[self.TARGETS_COLUMN_NAME].apply(
                    lambda x: x[0].get(category, None)
                )
            )

    @no_type_check
    @requires_data
    def _add_text_duplicates_count_column(self) \
            -> None:
        """
        Adds a text duplicates count column to the DataFrame.

        Adds a column to the DataFrame that stores the number of times the
        text in the 'text' column appears. Duplicate text has multiple
        targets, each treated in a separate row. Therefore, the number of
        duplicates corresponds to the number of targets identified in the text.

        Notes
        -----
        - The DataFrame is modified in place and is not returned from this
          method.

        """

        self.data.df[self.TEXT_DUPLICATES_COUNT_COLUMN_NAME] = \
            (
                self.data.df.groupby(self.TEXT_COLUMN_NAME)[
                    self.TEXT_COLUMN_NAME].transform('count')
            )

    def _ensure_no_duplicate_gids(self) \
            -> None:
        """
        Ensures that there are no duplicate GIDs in the data.

        Raises
        ------
        CriticalException
            If there are duplicate GIDs in the data.

        """

        duplicates = self._get_duplicate_gids()

        if len(duplicates) > 0:
            raise CriticalException(
                self.logger,
                '%d GID duplicates found: \n%s' % (len(duplicates), duplicates)
            )

    @no_type_check
    @requires_data
    def _extract_target_details(self) \
            -> None:
        """
        Extracts target details from the targets column into separate columns.

        """

        self._ensure_no_multiple_targets()

        self._add_target_detail_columns()
        self.data.do_with_column(
            'drop_column', col_name=self.TARGETS_COLUMN_NAME
        )

    @requires_property('language')
    def _set_source(self) \
            -> None:
        """
        Sets the source of the data.

        As the original files are stored in language-dependent subdirectories
        of a local directory, the source is composed of the local directory
        and the subdirectory corresponding to the language of the
        current strategy.

        """

        self.source = os.path.join(self.ORIG_DIR, self.language)

    # endregion --- Protected Methods
