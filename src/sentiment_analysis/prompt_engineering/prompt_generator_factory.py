"""
prompt_generator_factory.py
---------------------------
Version 1.0, updated on 2025-01-25

This module provides a function to create a prompt generator with a specified
strategy number.

Functions
---------
get_prompt_generator(strategy_nr: int) -> PromptGenerator:
    Creates a PromptGenerator instance based on the specified strategy number.

"""

from typing import Dict

from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.prompt_engineering.prompt_generating_strategy \
    import PromptGeneratingStrategy
from src.sentiment_analysis.prompt_engineering.prompt_generator import \
    PromptGenerator
from src.utils.class_utils import instantiate_class_from_module_name
from src.utils.string_utils import StringUtils

log = LoggingMixin().log


def get_prompt_generator(
        ingredients: Dict[str, str],
        strategy_nr: int = 1,
) -> PromptGenerator:
    """
    Creates a PromptGenerator instance based on the specified strategy number.

    Dynamically creates and returns an instance of the PromptGenerator
    class using the specified strategy number that corresponds to the number
    appended to the prompt generating strategy names.

    Parameters
    ----------
    ingredients : Dict[str, str]
        Ingredients to use when generating the intended prompt. The
        dictionary keys are the ingredients categories, the values are the
        selected values for these categories.

    strategy_nr : int
        An integer designing the strategy number. Defaults to 1.

    Returns
    -------
    PromptGenerator
        An instance of the PromptGenerator class that uses the prompt
        generating strategy that corresponds to the specified strategy number.

    """

    strategy = _get_strategy(ingredients, strategy_nr)

    return PromptGenerator(strategy)


def _get_strategy(ingredients: Dict[str, str], strategy_nr: int) \
        -> PromptGeneratingStrategy:
    """
    Creates a PromptGeneratingStrategy instance based on the specified
    strategy number.

    Dynamically creates and returns an instance of the prompt generating
    strategy that corresponds to the specified strategy number.

    Parameters
    ----------
    ingredients : Dict[str, str]
        Ingredients to use when generating the intended prompt. The
        dictionary keys are the ingredients categories, the values are the
        selected values for these categories.

    strategy_nr: int
        An integer designing the strategy number.

    Returns
    -------
    An instance of the specified strategy class.

    """

    strategy_name = "PromptGeneratingStrategy" + str(strategy_nr)
    converted_name = StringUtils.convert_class_name_into_module_name(
        strategy_name
    )

    module_name = (f"src.sentiment_analysis.prompt_engineering."
                   f"{converted_name}")

    return instantiate_class_from_module_name(
        module_name, strategy_name, ingredients
    )
