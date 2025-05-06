"""
prompt_optimizer.py
---------------------
Version 1.0, updated on 2025-05-01

"""

from typing import Dict, List, Tuple, Any, Set

from pandas import DataFrame

from logger import Logger
from src.data_structures.item_series import ItemSeries
from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.str_series import StrSeries
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.prompt_engineering import (
    prompts_and_ingredients_manager as manager
)
from src.sentiment_analysis.prompt_engineering.prompt_engineer_factory import (
    get_prompt_engineer
)
from src.sentiment_analysis.prompt_engineering.prompt_printer import (
    PromptPrinter
)
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.utils.data_utils import is_none_or_empty
from src.utils.list_sort_utils import (
    sort_list_of_tuples_by_desc_second_element_asc_first
)
from src.utils.list_utils import (
    get_first_elements_from_list_of_tuples,
    is_substring_of_list_content,
    remove_elements_from_list
)


class PromptOptimizer(LoggingMixin):
    """
    PromptOptimizer class.

    This class provides methods for analyzing valid and invalid prompt
    variants and ingredients so that decision can be taken which prompt
    ingredients should be removed from the lists used for prompt generation.

    Attributes
    ----------
    VALIDATED_PROMPTS_FILE_NAME : str
        File name for storing validated prompts.

    FREQ_THRESHOLD : int
        Minimum frequency an ingredient should have if it appears only in
        invalid prompts to be excluded from the lists of possible ingredients.

    VALID : str
        The 'valid' label.

    INVALID : str
        The 'invalid' label.

    chunk_size : int
       Size of each chunk.

    """

    VALIDATED_PROMPTS_FILE_NAME = 'prompt_sets_history_1'

    # Number of times an ingredient must at least have been used to qualify
    # for removal if it only leads to invalid prompts.
    FREQ_THRESHOLD = 5

    # Variants types

    VALID = "valid"
    INVALID = "invalid"

    def __init__(
            self,
            language: str = 'en',
            chunks: Dict[int, MyDataFrame] = None
    ):
        """
        Initializes the PromptOptimizer with the specified parameters.

        Parameters
        ----------
        language : str
           Language code (default is 'en').

        chunks : Dict[int, MyDataFrame]
            Data chunks dictionary, where the keys are the integer numbers
            of the chunks and the value is a MyDataFrame with the chunk data.

        """

        self.prompts_manager = manager.PromptsAndIngredientsManager(
            language, chunks
        )

        # Whether values of previous prompt engineering strategies should be
        # used to countercheck results when only invalid values are retrieved
        self.prompts_manager.check_previous = True

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.language: str = language
        self.chunks: Dict[int, MyDataFrame] = chunks

        # Configs used in this class
        self.config = SentimentAnalysisConfig()
        strategy_nr = int(self.config.get('version'))

        # Set the printer with the strategy number
        self.printer = PromptPrinter(strategy_nr)

        # ATTENTION: The PromptEngineeringStrategy used to set the
        # prompt_engineer modifies the configuration settings. Hence, use any
        # config settings only after the prompt_engineer is created.

        self.prompt_engineer = get_prompt_engineer(strategy_nr)

        self.chunk_size: int = self.config.get('chunk_size')

        """
        Initialize variables for collections of
        - prompt-parts that are always valid / invalid
        - ingredients that always produce valid / invalid prompts
        """
        self.only_valid_prompt_parts: Dict[str, List[Tuple[str, int]]] = {}
        self.only_invalid_prompt_parts: Dict[str, List[Tuple[str, int]]] = {}
        self.only_valid_ingredients: Dict[str, List[Tuple[str, int]]] = {}
        self.only_invalid_ingredients: Dict[str, List[Tuple[str, int]]] = {}

    # region --- Properties

    # endregion --- Properties

    # region --- Public Methods

    def find_influential_variants_by_col_name(
            self,
            valid_df: DataFrame,
            invalid_df: DataFrame,
            col_name: str,
            previous_valid_df: DataFrame | None
    ) -> Tuple[
        List[
            Tuple[str, int]
        ],
        List[
            Tuple[str, int]
        ]
    ]:
        """
        Finds influential variants of prompt parts or ingredients.

        Examines which prompt parts or ingredients in a column that
        corresponds to a variants category only lead to valid
        prompts and which ones only to invalid prompts.

        Returns the lists of valid and invalid variants which are found to
        significantly influence the validity of a prompt.

        Parameters
        ----------
        valid_df : DataFrame
            A DataFrame with valid prompts or prompt ingredients sets.

        invalid_df : DataFrame
            A DataFrame with invalid prompts or prompt ingredients sets.

        col_name : str
            Name of the column whose values are to be examined. The name
            equals the category to which the prompt parts or ingredients
            belong.

        previous_valid_df : DataFrame
            A DataFrame with valid prompts or prompt ingredients sets from
            one or more previous prompt engineering strategies.

        Returns
        -------
        Tuple[
            List[
                Tuple[str, int]
            ],
            List[
                Tuple[str, int]
            ]
        ]
            Two lists of tuples with the prompt parts or ingredients of
            the category corresponding to the examined column's name that
            were found to significantly influence the validity of a prompt.
            The first list is the list of elements always leading to valid
            prompts, the second list contains the elements that lead to
            invalid prompts.

        Notes
        -----
        This method is used by
        - find_influential_variants
          (
            - find_influential_prompt_parts,
            - find_influential_prompt_ingredients_sets,
            which presently are not used
          )
        - analyze_valid_invalid_correlation_by_category

        """

        # Extract the column's values from the valid data ...
        valid_col_values = StrSeries(
            valid_df[col_name],
            name=self.VALID
        )
        # ... and from the invalid data. Store the values in StrSeries types
        # that will provide the frequencies of the values.
        invalid_col_values = StrSeries(
            invalid_df[col_name],
            name=self.INVALID
        )

        # Reduce the number of occurrences of each value to 1 per result set:
        unique_valid = valid_col_values.distinct_elements
        unique_invalid = invalid_col_values.distinct_elements

        # Prepare result lists
        only_valid = []
        only_invalid = []

        # Iterate through the values of the valid data's column
        for el in unique_valid:
            # Ensure the value is not also among the values of the
            # invalid data's column.
            if el not in unique_invalid:
                # If the value only appeared in the valid data, add it to
                # the only_valid list, together with the value's frequency
                freq = valid_col_values.frequencies[el]
                only_valid.append((el, freq))

        # Iterate through the values of the invalid data's column
        for el in unique_invalid:
            # Ensure the value is not also among the values of the
            # valid data's column.
            if el not in unique_valid:
                if previous_valid_df is not None:
                    previous_valid_col_values = StrSeries(
                        previous_valid_df[col_name],
                        name=self.VALID
                    )
                    previous_unique_valid = (
                        previous_valid_col_values.distinct_elements
                    )
                    if el not in previous_unique_valid:
                        # If the value only appeared in the invalid data,
                        # and was not valid in previous strategies, add it to
                        # the only_invalid list, together with the value's
                        # frequency
                        freq = invalid_col_values.frequencies[el]
                        only_invalid.append((el, freq))
                    else:
                        msg = "Was valid in previous strategies: '%s'" % el
                        self.log(msg, "info")
                else:
                    freq = invalid_col_values.frequencies[el]
                    only_invalid.append((el, freq))

        # Sort the result lists first by frequency and then alphabetically
        sorted_only_valid = self._sort_variants_with_freqs(only_valid)
        sorted_only_invalid = self._sort_variants_with_freqs(only_invalid)

        return sorted_only_valid, sorted_only_invalid

    def find_influential_variants(
            self,
            valid: MyDataFrame,
            invalid: MyDataFrame
    ) -> None:
        """
        Finds influential variants of prompt parts or prompt ingredients.

        Examines which prompt parts or prompt ingredients only lead to valid
        prompts and which ones only to invalid prompts. Sets the 'only'
        properties accordingly.

        Prints the results (the respective 'only' DataFrames and their
        descriptions):

        Parameters
        ----------
        valid : MyDataFrame
            DataFrame with valid prompts or prompt sets.

        invalid : MyDataFrame
            DataFrame with invalid prompts or prompt sets.

        Raises
        ------
        CriticalException
            If the name of the valid data does not correspond to one of the
            expected values (VALID_PROMPTS_NAME or
            VALID_INGREDIENTS_SETS_NAME).

        """

        # Prepare result dictionaries:
        only_valid: Dict[str, List[Tuple[str, int]]] = {}
        only_invalid: Dict[str, List[Tuple[str, int]]] = {}

        prompts_manager = self.prompts_manager

        try:
            # Distinguish between prompt parts and prompt ingredients to store
            # them in the corresponding class variables:
            is_prompts_collection = self._is_prompts_collection(valid)

        except CriticalException as err:
            raise CriticalException from err

        if prompts_manager.check_previous is True:
            if is_prompts_collection:
                previous_valid_df = (
                    prompts_manager.previous_valid_prompts.data.df
                )
            else:
                previous_valid_df = (
                    prompts_manager.previous_valid_ingredients_sets.data.df
                )
        else:
            previous_valid_df = None

        # Distinguish between prompt parts and prompt ingredients to store
        # Iterate through the columns of the data (which are assumed to be
        # the same for valid and invalid data)
        for col_name in valid.col_names:
            # From valid and invalid data, extract the values that only appear
            # in valid data and those that only appear in invalid data
            valid_values, invalid_values = (
                self.find_influential_variants_by_col_name(
                    valid.df, invalid.df, col_name, previous_valid_df)
            )

            # Store the results in the corresponding dictionaries
            only_valid[col_name] = valid_values
            only_invalid[col_name] = invalid_values

        # Distinguish between prompt parts and prompt ingredients to store
        # them in the corresponding class variables:
        if is_prompts_collection:
            self.only_valid_prompt_parts = only_valid
            self.only_invalid_prompt_parts = only_invalid

            self.printer.print_variants_dicts(
                self.only_valid_prompt_parts,
                self.only_invalid_prompt_parts
            )

        else:
            self.only_valid_ingredients = only_valid
            self.only_invalid_ingredients = only_invalid

            self.printer.print_variants_dicts(
                self.only_valid_ingredients,
                self.only_invalid_ingredients
            )

    def find_influential_prompt_parts(self) \
            -> None:
        """
        Finds prompt parts that may be responsible for the validity of prompts.

        Calls the find_influential_variants method to perform the
        comparison.

        Notes
        -----
        This method does not return any values. The
        find_influential_variants method will update the 'only' dictionaries
        of this class and additionally, it will output its findings to the
        console.

        """

        valid = self.prompts_manager.valid_prompts.data
        invalid = self.prompts_manager.invalid_prompts.data

        self.find_influential_variants(valid, invalid)

    def find_influential_prompt_ingredients_sets(self) \
            -> None:
        """
        Finds influential prompt ingredients for valid and invalid prompts.

        Calls the find_influential_variants method to perform the
        comparison.

        """

        valid = self.prompts_manager.valid_ingredients_sets.data
        invalid = self.prompts_manager.invalid_ingredients_sets.data

        self.find_influential_variants(valid, invalid)

    def print_overall_prompts_results(self) \
            -> None:
        """
        Prints the overall prompts results.

        Prints the number of prompts processed and the
        resulting numbers of valid and invalid prompts.

        """

        self.printer.print_prompt_statistics(
            self.prompts_manager.valid_prompts.data.n_rows,
            self.prompts_manager.invalid_prompts.data.n_rows,
            self.prompts_manager.all_prompts.data.n_rows
        )

    def correlation_analysis(self) \
            -> None:
        """
        Finds and prints ingredients that correlate with prompt validity.

        Analyzes valid and invalid prompts to find ingredients that correlate
        with valid or invalid outcomes.

        """

        self.printer.print_prompt_statistics(
            self.prompts_manager.valid_prompts.data.n_rows,
            self.prompts_manager.invalid_prompts.data.n_rows,
            self.prompts_manager.all_prompts.data.n_rows
        )

        self.analyze_valid_invalid_correlation_per_category()

    def analyze_valid_invalid_correlation_per_category(self) \
            -> None:
        """
        Analyzes valid and invalid correlations across specified categories.

        This method evaluates whether there is a correlation between
        prompt ingredients and the validity of prompts, i.e., whether a
        prompt is valid or invalid. It analyzes categories such as 'order',
        'scale', 'politeness', and others deemed relevant, while excluding
        those considered irrelevant (e.g., 'preposition'). It builds two
        dictionaries containing results for only valid and only invalid
        ingredients, respectively.

        Notes
        -----
        This method does not return any value. It calls the
        analyze_valid_invalid_correlation_by_category method to perform the
        analysis for each category and print the results

        """

        valid_df = self.prompts_manager.valid_ingredients_sets.data.df
        invalid_df = self.prompts_manager.invalid_ingredients_sets.data.df

        # Check only categories that seem to influence whether a prompt
        # triggers a valid answer (e.g. 'preposition' or 'toward' are
        # irrelevant):
        categories = [
            'answer_start',
            'given',
            'politeness',
            'scale',
            'sentence_label',
            'target',
            'task',
            'thought',
            'what',
            'where'
        ]

        only_valid: Dict[str, List[Tuple[str, int]]] = {
            category: [] for category in categories
        }
        only_invalid: Dict[str, List[Tuple[str, int]]] = {
            category: [] for category in categories
        }

        for category in categories:
            only_valid[category], only_invalid[category] = \
                self.analyze_valid_invalid_correlation_by_category(
                    category, valid_df, invalid_df
                )

    def analyze_valid_invalid_correlation_by_category(
            self,
            category: str,
            valid_df: DataFrame,
            invalid_df: DataFrame
    ) -> Tuple[Any, Any]:
        """
        Analyzes valid and invalid correlations of the specified category.

        Evaluates whether there is a correlation between prompt ingredients
        of the given category and the validity of prompts, i.e., whether a
        prompt is valid or invalid.

        Parameters
        ----------
        category : str
            The name of the ingredients category to analyze.

        valid_df : DataFrame
            A DataFrame containing valid ingredient sets.

        invalid_df : DataFrame
            A DataFrame containing invalid ingredient sets.

        Returns
        -------
        Tuple[Any, Any]
            A tuple containing two elements:
            (1) A collection of ingredients that produce only valid prompts.
            (2) A collection of ingredients that produce only invalid prompts.

        """

        valid_values, invalid_values = (
            self.find_influential_variants_by_col_name(
                valid_df,
                invalid_df,
                category,
                self.prompts_manager.previous_valid_ingredients_sets.data.df
            )
        )

        n_unique_values = len(self._get_all_unique_ingredients(category))
        n_valid_unique_values = len(
            self._get_unique_ingredients(
                category, self.VALID
            )
        )
        n_invalid_unique_values = len(
            self._get_unique_ingredients(
                category, self.INVALID
            )
        )

        total_n_elements_in_category = len(
            self.prompt_engineer.get_all_ingredients()[category]
        )

        self.printer.print_category_analysis(
            category,
            valid_values,
            invalid_values,
            n_unique_values,
            n_valid_unique_values,
            n_invalid_unique_values,
            total_n_elements_in_category
        )

        return valid_values, invalid_values

    def finegrained_analysis(self) \
            -> None:
        """
        Analyzes the basic ingredients of composed ingredients.

        Refines the results of the correlation analysis.

        Since the categories analyzed in the correlation analysis are not
        atomic enough (as they are composed of more basic ingredients),
        they cannot be removed from any ingredients lists. Therefore,
        this method uses the results of the correlation analysis to perform
        a more finegrained analysis on the basic ingredients and determine
        the elements that should be removed from the basic ingredients lists.

        """
        """
        Includes only categories that seem to have an influence on whether
        the prompt is valid or invalid and that are composed of ingredients 
        that are not already included in the ingredients collection. 
        After optimization of the prompt engineering, this is 
        only true for scale:
        
        """

        engineer = self.prompt_engineer

        basic_and_composed = engineer.get_basic_and_composed_ingredients()

        for basic, composed in basic_and_composed:
            ingredients = engineer.get_basic_ingredients()[basic]
            category = composed

            self._perform_finegrained_analysis(ingredients, category)

    def discarded_prompts_analysis(self) \
            -> None:
        """
        Analyzes the discarded prompts.

        """

        discarded = self.prompts_manager.discarded_prompts

        categories = discarded.data.col_names
        # Exclude irrelevant categories where the total number of
        # ingredient variants is known to be used in valid prompts:
        irrelevant_categories = [
            'before_mention',
            'answer_start'
        ]
        categories = remove_elements_from_list(
            categories, irrelevant_categories
        )

        # Prepare a dictionary to store the invalid values per category
        only_invalid_values_per_category = {}

        for category in categories:
            # List of category values in discarded prompts
            values = ItemSeries(
                discarded.data.df[category],
                f"'{category}' values in discarded prompts"
            )

            # List of category values in valid prompts
            valid_category_values = self.prompts_manager.valid_prompts.data.df[
                category
            ].values

            freqs = values.frequencies

            self.printer.print_unique_category_values_with_freqs(
                category,
                freqs,
                validity='discarded',
                min_freq=2
            )

            only_invalid_category_values = []

            for freq in freqs:
                if freqs[freq] >= 5:
                    if freq not in valid_category_values:
                        only_invalid_category_values.append(freq)

                else:
                    # Exit the loop as freqs is sorted in descending
                    # frequency order
                    break

            # Sort the invalid values per category and store them in the
            # prepared dictionary
            only_invalid_values_per_category[category] = (
                sorted(only_invalid_category_values)
            )

        self.printer.print_invalid_prompt_parts(
            only_invalid_values_per_category
        )

        self._finegrained_prompt_parts_analysis(
            only_invalid_values_per_category)

    def _finegrained_prompt_parts_analysis(
            self,
            prompt_parts: Dict[str, List[str]]
    ):
        basic_ingredients = self._retrieve_basic_ingredients_from_prompt_parts(
            prompt_parts
        )
        invalid_ingredients = {}
        for ingredients_category, ingredient in basic_ingredients:

            if not self._is_used_in_valid_prompts(
                    ingredients_category, ingredient
            ) and not self._is_used_in_previous_valid_prompts(
                ingredients_category, ingredient
            ):
                if ingredients_category not in invalid_ingredients:
                    invalid_ingredients[ingredients_category] = []

                invalid_ingredients[ingredients_category].append(ingredient)

        self.printer.print_invalid_ingredients_in_discarded_prompts(
            invalid_ingredients
        )


    def _retrieve_basic_ingredients_from_prompt_parts(
            self,
            prompt_parts: Dict[str, List[str]]
    ) -> Set[Tuple[str, str]]:

        basic_ingredients = {
            ingredient
            for parts_category in prompt_parts
            for prompt_part in prompt_parts[parts_category]
            for ingredient in self.prompt_engineer.decompose_prompt_part(
                parts_category, prompt_part
            )
        }

        return basic_ingredients

    def _is_used_in_valid_prompts(self, category: str, ingredient: str) \
            -> bool:
        """
        Check whether an ingredient is used in valid prompts.

        Parameters
        ----------
        category : str
            The category of the ingredient. Matches the name of the relevant
            column in the valid_ingredients_sets Dataframe.

        ingredient : str
            Prompt ingredient to look for in the column.

        Returns
        -------
        bool
            True if the ingredient is used in valid prompts, False otherwise.

        Notes
        -----
        This method uses Pandas's isin method to benefit from the fast and
        memory-efficient vectorized operation Pandas uses for lookups in
        Series.

        """

        df = self.prompts_manager.valid_ingredients_sets.data.df
        return df[category].isin([ingredient]).any()

    def _is_used_in_previous_valid_prompts(
            self,
            category: str,
            ingredient: str
    ) -> bool:
        """
        Check whether an ingredient is used in previous valid prompts.

        Parameters
        ----------
        category : str
            The category of the ingredient. Matches the name of the relevant
            column in the valid_ingredients_sets Dataframe.

        ingredient : str
            Prompt ingredient to look for in the column.

        Returns
        -------
        bool
            True if the ingredient is used in valid prompts, False otherwise.

        Notes
        -----
        This method uses Pandas's isin method to benefit from the fast and
        memory-efficient vectorized operation Pandas uses for lookups in
        Series.

        """

        df = self.prompts_manager.previous_valid_ingredients_sets.data.df
        return df[category].isin([ingredient]).any()

    # endregion --- Public Methods

    # region --- Protected Methods

    def _get_all_unique_ingredients(self, category: str) \
            -> List[str]:
        """
        Gets all unique ingredients for the specified category.

        Parameters
        ----------
        category : str
            The category to get unique ingredients for.

        Returns
        -------
        List[str]
            List of all unique ingredients for the specified category.

        """

        all_ingredients_sets = self.prompts_manager.all_ingredients_sets

        if category in all_ingredients_sets.data.col_names:
            col_values = StrSeries(
                all_ingredients_sets.data.df[category],
                name=category
            )
            unique_values = col_values.distinct_elements

            self.printer.print_unique_category_values(
                category,
                unique_values,
                'all',
            )

        else:
            raise CriticalException(self.logger,
                                    "Unknown column in prompts: %s" % category)

        return unique_values

    def _get_unique_ingredients(self, category: str, validity: str = '', ) \
            -> List[str]:
        """
        Gets unique ingredients for the specified category and validity.

        Parameters
        ----------
        category : str
            The category to get unique ingredients for.

        validity : str, optional
            The validity ('valid' or 'invalid') to filter by (default is '').

        Returns
        -------
        List[str]
            List of unique ingredients for the specified category and validity.

        """

        if not validity:
            return self._get_all_unique_ingredients(category)

        prompts = self._get_ingredients_sets_by_validity(validity)

        if category in prompts.col_names:
            col_values = StrSeries(prompts.df[category], name=category)
            unique_values = col_values.distinct_elements

            self.printer.print_unique_category_values(
                category,
                unique_values,
                validity,
            )

        else:
            raise CriticalException(
                self.logger, "Unknown column in prompts: %s" % category
            )

        return unique_values

    def _get_ingredients_sets_by_validity(self, validity: str) \
            -> MyDataFrame:
        """
        Gets ingredients sets by validity.

        Parameters
        ----------
        validity : str
            The validity status ('valid' or 'invalid').

        Returns
        -------
        MyDataFrame
            The ingredients sets with the specified validity.

        """

        match validity:
            case "valid":
                prompts = self.prompts_manager.valid_ingredients_sets.data
            case "invalid":
                prompts = self.prompts_manager.invalid_ingredients_sets.data
            case _:
                raise CriticalException(
                    self.logger,
                    "Unknown validity value: %s" % validity
                )

        return prompts

    def _is_prompts_collection(self, valid: MyDataFrame) \
            -> bool:
        """
        Determines if the given valid data is a "prompts" collection.

        Determines if the given valid data is a "prompts" or a
        ingredients sets collection.

        Parameters
        ----------
        valid : MyDataFrame
            The valid data. The MyDataFrame's name attribute is
            evaluated to determine its collection type.

        Returns
        -------
        bool
            `True` if the dataframe belongs is a "prompts" collection,
            `False` if it is a "ingredient sets" collection.

        Raises
        ------
        CriticalException
            Raised when the `name` attribute of the provided dataframe does
            not match any expected values.

        """

        match valid.name:
            case self.prompts_manager.VALID_PROMPTS_NAME:
                return True
            case self.prompts_manager.VALID_INGREDIENTS_SETS_NAME:
                return False
            case _:
                raise CriticalException(
                    self.logger,
                    "Unknown variants type. Cannot set 'only' variants."
                )

    def _is_sufficiently_frequent(self, basic_ingredient: str, category: str) \
            -> bool:
        """
        Checks if the given ingredient was used often enough to be removed.

        Calls the _compute_frequency_of_possible_invalid_basic_ingredient
        method to determine how often the ingredient was used. It then
        compares the frequency with the threshold set at the beginning of
        this class.

        If a basic ingredient appears to be invalid because all the prompts
        it has contributed to are invalid, the ingredient is still kept in
        the corresponding list of possible ingredients if it was only used
        very infrequently so that it is unsure whether it will always lead
        to the prompt being invalid.

        Parameters
        ----------
        basic_ingredient : str
            The ingredient that possibly should be removed from the list
            because it is used in prompts that always result to be invalid.

        category: str
            The composed category in whose elements the elements of the
            basic ingredients_list need to be searched.

        Returns
        -------
        bool
            True if the frequency is equal to or higher than the defined
            threshold, False otherwise.

        """

        freq = self._compute_frequency_in_invalid_prompts(
            basic_ingredient, category
        )

        return freq >= self.FREQ_THRESHOLD

    def _compute_frequency_in_invalid_prompts(
            self,
            basic_ingredient: str,
            category: str
    ) -> int:
        """
        Computes the frequency of a basic ingredient in the invalid prompts.

        Parameters
        ----------
        basic_ingredient : str
            The ingredient that possibly should be removed from the list
            because it is used in prompts that always result to be invalid.

        category : str
            The composed category in whose elements the elements of the
            basic ingredients_list need to be searched.

        Returns
        -------
        int
            The frequency of the basic ingredient in invalid prompts.

        """

        only_invalid = self.only_invalid_ingredients

        return sum(
            freq for ingredient, freq in only_invalid[category]
            if basic_ingredient in ingredient
        )

    def _perform_finegrained_analysis(
            self,
            ingredients: List[str],
            category: str
    ) -> None:
        """
        Performs the analysis for the given ingredients in the given category.

        Parameters
        ----------
        ingredients : List[str]
            List of basic prompt ingredients that were used to compose the
            ingredients of a composed category.

        category: str
            The composed category in whose elements the elements of the
            basic ingredients_list need to be searched.

        Notes
        -----
        This method requires the only_invalid_ingredients property to be set
        beforehand. Therefore, if the property is not set, the
        find_influential_prompt_ingredients_sets method is executed first to
        ensure the property is set.

        """

        all_valid = self.prompts_manager.valid_ingredients_sets.data

        if is_none_or_empty(self.only_invalid_ingredients):
            self.find_influential_prompt_ingredients_sets()

        only_invalid = self.only_invalid_ingredients

        # Skip the entire method if the category is not a key in the
        # only_invalid dictionary:
        if category not in only_invalid:
            msg = "Category '%s' cannot be processed!" % category
            self._log(msg, 'info')

            return

        # Extract the list of first tuple elements from the list of
        # only_invalid tuples
        invalid_category_elements = get_first_elements_from_list_of_tuples(
            only_invalid[category]
        )

        # Get the list of unique category elements from all valid
        # ingredients sets
        all_valid_category_elements = StrSeries(
            all_valid.df[category], 'all_valid_category_elements'
        ).distinct_elements

        bad_elements = []
        good_elements = []

        # Check whether a basic ingredient whose composed category is always
        # used in invalid prompts is nevertheless used in any valid prompts.
        # If so, it is a good ingredient, otherwise a bad one.
        for ingredient in ingredients:
            if is_substring_of_list_content(
                    ingredient,
                    invalid_category_elements
            ):
                if self._is_sufficiently_frequent(ingredient, category) \
                        and not is_substring_of_list_content(
                    ingredient,
                    all_valid_category_elements
                ):
                    bad_elements.append(ingredient)
                else:
                    good_elements.append(ingredient)

        # Sort the results alphabetically
        bad_elements = sorted(bad_elements)
        good_elements = sorted(good_elements)

        self.printer.print_finegrained_analysis(
            category, bad_elements, good_elements
        )

    def _sort_variants_with_freqs(self, lst: List[Tuple[str, int]]) \
            -> List[Tuple[str, int]]:
        """
        Sort the list of tuples containing the variants and frequencies.

        Parameters
        ----------
        lst : List[Tuple[str, int]]
            The list of variants with frequencies.

        Returns
        -------
        List[Tuple[str, int]]
            The sorted list.

        """

        return sort_list_of_tuples_by_desc_second_element_asc_first(lst)

    # endregion --- Protected Methods
