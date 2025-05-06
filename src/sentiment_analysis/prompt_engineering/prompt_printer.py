"""
prompt_printer.py
----------------
Version 1.0, updated on 2025-05-01

"""

from typing import Dict, List, Tuple, Counter

from src.sentiment_analysis.prompt_engineering.prompts import Prompts
from src.utils.print_utils import print_in_box
from src.utils.list_utils import filter_list_of_tuples_by_min_second_element


class PromptPrinter:
    """
    PromptPrinter class

    Handles all printing operations for PromptOptimizer.

    This class centralizes all print statements related to prompts,
    correlation analysis, discarded prompts, and frequency results.

    Methods
    -------
    print_category_analysis(
        category: str,
        valid_values: List[Tuple[str, int]],
        invalid_values: List[Tuple[str, int]],
        n_unique_values: int,
        n_valid_unique_values: int,
        n_invalid_unique_values: int,
        total_n_elements: int
    ) -> None:
        Prints the analysis results of a given category.

    print_category_statistics(
        category: str = '',
        total_n_elements: int = 0,
        n_unique_values: int = 0,
        n_valid_unique_values: int = 0,
        n_invalid_unique_values: int = 0,
        n_only_valid_values: int = 0,
        n_only_invalid_values: int = 0
    ) -> None:
        Prints the statistics of a given category.

    print_finegrained_analysis(
        category: str,
        bad_elements: List[str],
        good_elements: List[str]
    ) -> None:
        Prints results of fine-grained prompt part analysis.

    print_invalid_prompt_parts(
        invalid_prompt_parts: Dict[str, List[str]]
    ) -> None:
        Prints all invalid prompt parts identified in the analysis.

    print_prompt_statistics(
        n_valid_prompts: int,
        n_invalid_prompts: int,
        total_n_prompts: int
    ) -> None:
        Prints the counts of total prompts and valid and invalid prompts.

    print_unique_category_values(
        category: str,
        unique_values: List[str],
        validity: str = ''
    ) -> None:
        Prints the unique values of a given category.

    print_unique_category_values_with_freqs(
        category: str,
        values: Union[List[Tuple[str, int]], Counter],
        validity: str = ''
    ) -> None:
        Prints the values of a given category.

    print_variants(
        valid: Prompts,
        invalid: Prompts
    ) -> None:
        Prints the valid and invalid prompts.

    print_variants_dicts(
        valid: Dict[str, List[Tuple[str, int]]],
        invalid: Dict[str, List[Tuple[str, int]]]
    ) -> None:
        Prints the given variants dictionaries.

    """

    def __init__(self, strategy_nr: int) \
            -> None:
        self.strategy_nr = strategy_nr
        self.strategy = f"Strategy {self.strategy_nr} -"

    def print_variants(self, valid: Prompts, invalid: Prompts) \
            -> None:
        """
        Prints the valid and invalid prompts.

        Parameters
        ----------
        valid : Prompts
            Valid prompts.

        invalid : Prompts
            Invalid prompts.

        """

        valid.print()
        invalid.print()

    def print_variants_dicts(
            self,
            valid: Dict[str, List[Tuple[str, int]]],
            invalid: Dict[str, List[Tuple[str, int]]]
    ) -> None:
        """
        Prints the given variants dictionaries.

        Parameters
        ----------
        valid : Dict[str, List[Tuple[str, int]]]
            Dictionary with prompt parts or prompt ingredients that always
            lead to valid prompts. The key is the category the respective
            parts belong to, the value is a list of tuples where the first
            element is a prompt part or ingredient and the second element
            is the frequency with which the first element has been used in
            the 150 prompts.

        invalid : Dict[str, List[Tuple[str, int]]]
            Dictionary with prompt parts or prompt ingredients that always
            lead to invalid prompts. It is organized in the same way as the
            'valid' dictionary.

        """

        print_in_box('Only valid queries', valid)
        print_in_box('Only invalid queries', invalid)

    def print_prompt_statistics(
            self,
            n_valid_prompts: int,
            n_invalid_prompts: int,
            total_n_prompts: int
    ) -> None:
        """
        Prints the counts of total prompts and valid and invalid prompts.

        Parameters
        ----------
        n_valid_prompts : int
            The number of valid prompts.

        n_invalid_prompts : int
            The number of invalid prompts.

        total_n_prompts : int
            The total number of prompts.

        """

        title = f"{self.strategy} Overall Prompts Results"
        body = (
            f"Total prompts:\t {total_n_prompts}\n"
            f"Valid prompts:\t {n_valid_prompts}\n"
            f"Invalid prompts:\t {n_invalid_prompts}\n"
        )

        print_in_box(title, body)

    def print_category_analysis(
            self,
            category: str,
            valid_values: List[Tuple[str, int]],
            invalid_values: List[Tuple[str, int]],
            n_unique_values: int,
            n_valid_unique_values: int,
            n_invalid_unique_values: int,
            total_n_elements: int
    ) -> None:
        """
        Prints the analysis results of a given category.

        Prints the category statistics and the values that only lead to
        valid or invalid prompts.

        Parameters
        ----------
        category : str
            The category.

        valid_values : List[Tuple[str, int]]
            The values that appear in valid prompts. Each tuple contains
            the value and its frequency.

        invalid_values : List[Tuple[str, int]]
            The values that appear in invalid prompts. Each tuple contains
            the value and its frequency.

        n_unique_values : int
            The number of unique values.

        n_valid_unique_values : int
            The number of unique values that appear in valid prompts.

        n_invalid_unique_values : int
            The number of unique values that appear in invalid prompts.

        total_n_elements : int
            The total number of elements.

        """

        n_only_valid_values = len(valid_values)
        n_only_invalid_values = len(invalid_values)

        self.print_category_statistics(
            category,
            total_n_elements,
            n_unique_values,
            n_valid_unique_values,
            n_invalid_unique_values,
            n_only_valid_values,
            n_only_invalid_values
        )

        self.print_unique_category_values_with_freqs(
            category,
            valid_values,
            validity="only valid",
        )

        self.print_unique_category_values_with_freqs(
            category,
            invalid_values,
            validity="only invalid",
        )

    def print_category_statistics(
            self,
            category: str = "",
            total_n_elements: int = 0,
            n_unique_values: int = 0,
            n_valid_unique_values: int = 0,
            n_invalid_unique_values: int = 0,
            n_only_valid_values: int = 0,
            n_only_invalid_values: int = 0
    ):
        """
        Prints the statistics of a given category.

        Prints
        - the total number of elements available,
        - the total number of elements used in the prompts,
        - the total number of elements used in valid prompts,
        - the total number of elements used in invalid prompts,
        - the number of elements that are only used in valid prompts,
        - the number of elements that are only used in invalid prompts.

        Parameters
        ----------
        category : str
            The category of the elements.

        total_n_elements : int
            The total number of elements.

        n_unique_values : int
            The number of unique values.

        n_valid_unique_values : int
            The number of unique values that appear in valid prompts.

        n_invalid_unique_values : int
            The number of unique values that appear in invalid prompts.

        n_only_valid_values : int
            The number of unique values that always lead to valid prompts.

        n_only_invalid_values : int
            The number of unique values that always lead to invalid prompts.

        """

        title = f"{self.strategy} Category: {category}"

        body = (
            f"Total n° of variants: \t "
            f"{total_n_elements} \n"
            f"Variants used: \t "
            f"{n_unique_values} \n"
            f"Variants producing valid prompts: \t "
            f"{n_valid_unique_values} \n"
            f"Variants producing invalid prompts: \t "
            f"{n_invalid_unique_values} \n"
            f"Variants producing only valid prompts: \t "
            f"{n_only_valid_values} \n"
            f"Variants producing only invalid prompts: \t "
            f"{n_only_invalid_values} \n"
        )

        print_in_box(title, body)

    def print_unique_category_values_with_freqs(
            self,
            category: str,
            values: List[Tuple[str, int]] | Counter,
            validity: str = '',
            min_freq: int = 0
    ) -> None:
        """
        Prints the values of a given category.

        Parameters
        ----------
        category : str
            The category to print values for.

        values : List[Tuple[str, int]] | Counter
            The values of the category and their frequencies.

        validity : str
            The validity of the prompts, e.g. '(only) valid',
            '(only) invalid', 'discarded', or an empty string, if the
            prompts are not filtered by validity.

        min_freq : int
            The minimum frequency of the values to print.

        """

        if validity != '':
            validity = f" - {validity}"

        title = f"{self.strategy} Category: {category}{validity}"
        n_values = len(values)

        # If there are only a few values, do not filter them
        if n_values <= 10:
            if min_freq > 0:
                min_freq = 0
        # If there are many values, filter them by a minimum frequency
        # If no minimum frequency is provided, set it to 1
        elif min_freq == 0:
            min_freq = 2

        subtitle = f"{n_values} unique elements"

        filtered_values = values

        if min_freq > 0 and n_values > 10:
            while n_values > 10:
                filtered_values = [
                    filter_list_of_tuples_by_min_second_element(
                        values, min_freq
                    )
                ]
                min_freq += 1
                n_values = len(filtered_values[0])

            subtitle += (
                f" (minimum frequency displayed: {min_freq - 1})"
            )

        print_in_box(
            title,
            filtered_values,
            subtitle
        )

    def print_unique_category_values(
            self,
            category: str,
            unique_values: List[str],
            validity: str = '',
    ) -> None:
        """
        Prints the unique values of a given category.

        Parameters
        ----------
        category : str
            The category to print unique values for.

        validity : str
            The validity of the prompts. Can be 'valid' or 'invalid' or an
            empty string, if the prompts are not filtered by validity.

        unique_values : List[str]
            The unique values of the category.

        """

        title = f"{self.strategy} Unique '{category}' elements in {validity} prompts"
        subtitle = f"{len(unique_values)} unique elements:"

        print_in_box(title, unique_values, subtitle)

    def print_invalid_prompt_parts(
            self,
            invalid_prompt_parts: Dict[str, List[str]]
    ) -> None:
        """
        Prints all invalid prompt parts identified in the analysis.

        Parameters
        ----------
        invalid_prompt_parts : Dict[str, List[str]]
            The invalid prompt parts identified in the analysis.

        """

        for category, values in invalid_prompt_parts.items():
            title = f"{self.strategy} {category.capitalize()}"
            subtitle = f"{len(values)} unique invalid prompt parts"

            print_in_box(title, values, subtitle)

    def print_invalid_ingredients_in_discarded_prompts(
            self,
            invalid_ingredients: Dict[str, List[str]]
    ) -> None:
        """
        Prints all invalid ingredients in discarded prompts.

        Parameters
        ----------
        invalid_ingredients : Dict[str, List[str]]
            The invalid ingredients in discarded prompts.

        """

        title = f"{self.strategy} Invalid ingredients in discarded prompts"
        for category, values in invalid_ingredients.items():
            subtitle = f"{len(values)} unique invalid ingredients in {category}"
            sorted_values = sorted(values)
            print_in_box(title, sorted_values, subtitle)


    def print_finegrained_analysis(
            self,
            category: str,
            bad_elements: List[str],
            good_elements: List[str]
    ) -> None:
        """
        Prints results of fine-grained prompt part analysis.

        Parameters
        ----------
        category : str
            The category to print unique values for.

        bad_elements : List[str]
            The unique values that lead to invalid prompts.

        good_elements : List[str]
            The unique values that also lead to valid prompts.

        """

        self.print_unique_category_values(
            f"{category} (bad)",
            bad_elements
        )
        self.print_unique_category_values(
            f"{category} (good)",
            good_elements
        )
