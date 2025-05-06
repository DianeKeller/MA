"""
mad_tsc_suite.py
-----------------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

from typing import List, TypeVar, TYPE_CHECKING

from pandas import DataFrame, Series

from constants import Language
from src.data_sources.data_source_factory import get_data_source_strategy
from src.data_sources.data_source_suite import DataSourceSuite
from src.data_sources.mad_tsc_fact_sheet_mixin import MadTscFactSheetMixin
from src.data_sources.mad_tsc_strategy import MadTscStrategy
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.sentiment_analysis.sentiment_stats import SentimentStats
from src.utils.data_utils import is_none_or_empty

if TYPE_CHECKING:
    from src.data_structures.my_data_frame import MyDataFrame

T = TypeVar('T', bound=MadTscStrategy)


class MadTscSuite(
    DataSourceSuite,
    MadTscFactSheetMixin
):
    """
    MadTscSuite class.

    This class serves as an interface that declares common operations
    for all supported MAD-TSC suite strategies, including loading,
    processing and comparing data subsets across different languages and
    splits. It extends functionality from the DataSourceSuite class,
    respecting the specific characteristics of the MAD-TSC suite.

    Attributes
    ----------
    SUITE_NAME : str
        The name of the data suite.
        
    SUITE_PREFIX : str
        The prefix used for naming strategies and files in the suite.
        
    SPLIT_TRAIN : str
        The string identifier for the training split.
        
    SPLIT_TEST : str
        The string identifier for the testing split.
        
    SPLIT_VAL : str
        The string identifier for the validation split.
        
    languages : List[str]
        A list of supported language codes in the suite. (Read-only)
        
    splits : List[str]
        A list of supported data splits (e.g., train, test, validation). 
        (Read-only)


    Methods
    -------
    are_cols_identical(subset: T, other: T, col_name: str) -> bool:
        Checks if a specific column is identical between two subsets.

    choose_subset(language: str) -> T:
        Returns the subset corresponding to a specified language.

    compare_cols(col_name: str, subset_names: List[str] | None = None) -> None:
        Compares a specific column across multiple subsets.

    get_comparison_column(subset: T, other: T, col_name: str) -> Series:
        Compares a specific column between two subsets row by row.

    get_sentiment_distributions(language='en', batch_size=100) -> DataFrame:
        Calculates sentiment distributions for a specified language and batch
        size.
    
    show_compare_cols(col_name, additional_col_name: str = '') -> MyDataFrame:
        Compares columns across different subsets and returns a DataFrame with
        the results.

    """

    SUITE_NAME: str = 'MadTsc'
    SUITE_PREFIX: str = 'mad_tsc'

    # Define format strings as class constants
    STRATEGY_STR: str = "{self.SUITE_NAME} strategy '{strategy_name}'"
    SUBSET_STR: str = "{self.SUITE_NAME} subset '{subset_name}'"

    # Split constants
    SPLIT_TRAIN: str = 'train'
    SPLIT_TEST: str = 'test'
    SPLIT_VAL: str = 'validation'

    # List of column names that do not represent query or answer columns.
    NON_QUERY_COLS = [
        'sentence_normalized',
        'mention',
        'polarity'
    ]

    def __init__(self):
        """
        Initializes a new instance of the MadTsc class and provides
        private variables to store the different data subsets of the data suite
        in memory and make them accessible via properties.

        """

        # Languages used in the data suite:
        self._languages = [
            Language.DE,
            Language.EN,
            Language.ES,
            Language.FR,
            Language.IT,
            Language.NL,
            Language.PT,
            Language.RO
        ]

        self._splits: List[str] = [
            self.SPLIT_TRAIN,
            self.SPLIT_TEST,
            self.SPLIT_VAL
        ]

        # The concrete implementations of some of the abstract methods
        # called when the parent class is initialized need the above lists.

        super().__init__()

        # Dictionary for assigning files to data subsets
        self._files_in_subsets: List[str] = self._splits

    # region --- Properties

    @property
    def splits(self) -> List[str]:
        return self._splits

    # endregion --- Properties

    # region --- Public Methods

    def get_sentiment_distributions(
            self,
            language: str = 'en',
            batch_size: int = 100
    ) -> DataFrame:

        for subset_name in self.subset_names:
            if f"_{language}_" in subset_name:
                subset = self.use_subset(subset_name)
                stats = SentimentStats(subset.data.df)
                distributions = stats.sentiment_distributions_for_all_batches(
                    batch_size
                )
                stats.show_sentiment_distributions()
                return distributions

        return DataFrame()

    def show_compare_cols(
            self,
            col_name: str,
            additional_col_name: str = ''
    ) -> MyDataFrame:
        """
        Compares columns across different subsets and returns the result.

        Compares columns across different subsets and returns a DataFrame with
        the results.

        Parameters
        ----------
        col_name : str
            The name of the column to compare across the subsets.

        additional_col_name : str
            The name of an additional column to include in the comparison.
            Defaults to an empty string.

        Returns
        -------
        MyDataFrame
            A DataFrame containing the comparison results.

        """

        base = None

        # Create an empty MyDataFrame instance to store the comparison results.
        my_df = MyDataFrameFactory.create()

        # Loop through each subset in the suite.
        for subset_name in self.subset_names:
            subset = self.use_subset(subset_name)

            # Set the first subset as the base for comparison.
            if base is None:
                base = subset
                # Get the index column from the base subset.
                index = base.my_df.df.index

                # If an additional column is given, take it from the base and
                # add it to the new DataFrame.
                if not is_none_or_empty(additional_col_name):
                    my_df.do_with_column(
                        'add_column',
                        data=base.my_df.df[additional_col_name],
                        col_name=additional_col_name + '_' + base.language
                    )

                # Add the index column to the new DataFrame.
                my_df.do_with_column(
                    'add_column',
                    data=index,
                    col_name=index.name
                )
                my_df.index_column = index.name

                # Add the specified column from the base subset to the
                # new DataFrame.
                my_df.do_with_column(
                    'add_column',
                    data=base.my_df.df[col_name],
                    col_name=col_name + '_' + base.language
                )

            else:
                # For subsequent subsets:
                # If an additional column is given, take it from the subset and
                # add it to the results DataFrame.
                if not is_none_or_empty(additional_col_name):
                    my_df.do_with_column(
                        'add_column',
                        data=subset.my_df.df[additional_col_name],
                        col_name=additional_col_name + '_' + subset.language
                    )

                # Add the specified column from the subset to the
                # results DataFrame.
                my_df.do_with_column(
                    'add_column',
                    data=subset.my_df.df[col_name],
                    col_name=col_name + '_' + subset.language
                )

                # Compare the current subset's column with the base subset's
                # column and add the result in a new column of the results
                # DataFrame. The values in the column indicate whether
                # the values of the two subsets are equal.
                my_df.do_with_column(
                    'add_column',
                    data=self.get_comparison_column(base, subset, col_name),
                    col_name="equal" + '_' + base.language + '_' +
                             subset.language
                )

        # Return the results DataFrame.
        return my_df

    @staticmethod
    def are_cols_identical(
            subset: T,
            other: T,
            col_name: str
    ) -> bool:
        """
        Checks if a specific column is identical between two subsets.

        Parameters
        ----------
        subset : MadTscStrategy
            The first subset to compare.

        other : MadTscStrategy
            The second subset to compare.

        col_name : str
            The name of the column to compare.

        Returns
        -------
        bool
            True if the columns are identical, False otherwise.

        """

        return subset.are_cols_identical(col_name, other, col_name)

    def get_comparison_column(
            self,
            subset: T,
            other: T,
            col_name: str
    ) -> Series:
        """
        Compares a specific column between two subsets row by row.

        This method returns a boolean Series indicating whether the values in
        the specified column of one subset are equal to the corresponding
        values in the same column of another subset.

        Parameters
        ----------
        subset : T
            The first subset to compare.
        other : T
            The second subset to compare.
        col_name : str
            The name of the column to compare between the two subsets.

        Returns
        -------
        Series
            A pandas Series of booleans where each entry is True if the
            corresponding values in the columns are equal, and False otherwise.

        """

        col_comparison = subset.my_df.df[col_name] == other.my_df.df[col_name]
        # Explicit type casting to make the type checkers happy:
        return Series(col_comparison)

    def choose_subset(self, language: str) \
            -> T:
        """
        Returns the subset with the specified language.

        Parameters
        ----------
        language : str
            The language of the subset.

        Returns
        -------
        Subset
            The subset.

        Notes
        -----
        The subset must be loaded before calling this method.

        """

        return self.use_subset(
            self._compose_strategy_name(language)
        )

    def to_string(self) -> str:
        """
        Provides a formatted string representation of the data in the current
        suite.

        Expands the base description by suite specific details like the name
        and source of the data collection, the author(s) of the collection
        and the citation of the associated scientific paper. If the data
        is not yet initialized, the description includes statistical insights
        such as the numbers and names of the domains, languages and original
        datasets contained in the data.

        Returns
        -------
        str
            A string representation of the data in the current MMS suite.

        """
        string = self.DESCRIPTION
        for _, value in self._subsets.items():
            string += value.to_string()

        return string

    # endregion --- Public Methods

    # region --- Protected Methods

    def _initialize_strategies(self) \
            -> None:
        """
        Initialize all strategies, respecting their dependencies.

        Each strategy is configured specifying
        - its strategy name,
        - its data type,
        - its file name,
        - its language, if there is only one,
        - its dataset name, if there is only one.

        """

        # Set strategy configurations
        strategy_configs = []

        for lang in self._languages:
            file_name = self._compose_file_name(lang)
            strategy_configs.append((
                file_name + "_strategy",
                file_name,
                lang
            ))

        # Initialize the strategies based on their configurations
        for (
                strategy_name,
                file_name,
                language
        ) in strategy_configs:
            strategy: T = self._create_strategy(
                file_name,
                language
            )

            self._strategies[strategy_name] = strategy

    def _compose_file_name(self, language: str) \
            -> str:
        """
        Composes the file name of the subset identified by the specified
        parameters.

        Parameters
        ----------
        language : str
            The language of the subset.

        Returns
        -------
        str
            The file name of the subset.

        """

        return f"{self.SUITE_PREFIX}_{language}"

    def _compose_strategy_name(self, language: str) \
            -> str:
        """
        Composes the name of the strategy.

        Composes the name of the strategy that is identified by the specified
        parameters.

        Parameters
        ----------
        language : str
            The language of the strategy.

        Returns
        -------
        str
            The name of the strategy.

        """

        return f"{self.SUITE_PREFIX}_{language}_strategy"

    @staticmethod
    def _create_strategy(
            file_name: str,
            language: str
    ) -> T:

        strategy: T = get_data_source_strategy(
            'mad',
            'tsc',
            file_name
        )

        if language:
            strategy.language = language

        return strategy

    def _compose_from_original_files(
            self,
            subset: T,
            strategy_name: str
    ) -> None:
        """
        Composes the specified subset from the original files.

        Parameters
        ----------
        subset : T
            The subset to compose.

        Notes
        -----
        The created subset is not returned from this method but

        - stored in the _subsets dictionary of this class and
        - saved to disk according to the serialization strategy used by the
          Olympia strategy of the subset (PKL format for DataFrame objects).

        """

        # Get the original files
        file_names = self._splits

        # List for the strategies collected from the files
        strategies: List[T] = []

        for file_name in file_names:
            # Create a strategy for each file
            strategy: T = get_data_source_strategy(
                'mad',
                'tsc',
                file_name
            )
            # Set the language of the strategy.
            # This will also set the source.
            strategy.language = subset.language

            strategies.append(strategy)

        # Create the subset
        subset.create(strategies)

        # Preprocess the subset
        subset.preprocess()

        # Add columns
        subset.add_columns()

        # Drop single-value columns
        subset.drop_single_value_cols()

        # Store the subset in the subsets collection
        self._subsets[strategy_name] = subset

        # Save the subset data to disk
        subset.save()

    def compare_cols(
            self,
            col_name,
            subset_names: List[str] | None = None
    ) -> None:
        """
        Compares corresponding columns in different subsets.

        Uses the first subset in the list as the base subset to which the
        other subsets are compared.

        Parameters
        ----------
        col_name
            The name of the columns to compare.

        subset_names : List[str] | None
            The names of the subsets whose columns are to be compared.
            Defaults to None. If the list is empty or None, it is set to all
            loaded subsets.

        """

        if is_none_or_empty(subset_names):
            subset_names = self.subset_names

        base = None

        for subset_name in subset_names:  # type: ignore
            subset = self.use_subset(subset_name)
            if base is None:
                base = subset
            else:
                other = subset
                what = "'%s' columns" % col_name.capitalize()

                if self.are_cols_identical(base, other, col_name):
                    print("%s are identical." % what)
                else:
                    print("%s differ." % what)

    # endregion --- Protected Methods
