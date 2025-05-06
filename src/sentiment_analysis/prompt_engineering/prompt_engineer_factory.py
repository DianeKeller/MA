"""
prompt_engineer_factory.py
-----------------------------
Version 1.0, updated on 2025-02-06

This module provides a function to create a prompt engineer with a specified
strategy number.

Functions
---------
get_prompt_engineer(strategy_nr: int) -> PromptEngineer:
    Creates a PromptEngineer instance based on the specified strategy number.

"""

from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.prompt_engineering.prompt_engineer import (
    PromptEngineer
)
from src.sentiment_analysis.prompt_engineering.prompt_engineering_strategy \
    import PromptEngineeringStrategy
from src.utils.class_utils import instantiate_class_from_module_name
from src.utils.string_utils import StringUtils

log = LoggingMixin().log


def get_prompt_engineer(strategy_nr: int = 1) \
        -> PromptEngineer:
    """
    Creates a PromptEngineer instance based on the specified strategy number.

    Dynamically creates and returns an instance of the PromptEngineer
    class using the specified strategy number that corresponds to the number
    appended to the prompt engineering strategy names.

    Parameters
    ----------
    strategy_nr : int
        An integer designing the strategy number. Defaults to 1.

    Returns
    -------
    PromptEngineer
        An instance of the PromptEngineer class that uses the prompt
        engineering strategy that corresponds to the specified strategy number.

    """

    strategy = _get_strategy(strategy_nr)

    return PromptEngineer(strategy)


def _get_strategy(strategy_nr: int) \
        -> PromptEngineeringStrategy:
    """
    Creates a PromptEngineeringStrategy instance based on the specified
    strategy number.

    Dynamically creates and returns an instance of the prompt engineering
    strategy that corresponds to the specified strategy number.

    Parameters
    ----------
    strategy_nr: int
        An integer designing the strategy number.

    Returns
    -------
    An instance of the specified strategy class.

    """

    strategy_name = "PromptEngineeringStrategy" + str(strategy_nr)
    converted_name = StringUtils.convert_class_name_into_module_name(
        strategy_name
    )

    module_name = (f"src.sentiment_analysis.prompt_engineering."
                   f"{converted_name}")

    return instantiate_class_from_module_name(
        module_name, strategy_name
    )
