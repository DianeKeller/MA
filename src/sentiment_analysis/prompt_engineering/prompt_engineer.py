"""
prompt_engineer.py
------------------
Version 1.0, updated on 2025-05-01

"""

from typing import List, Tuple

from pandas import DataFrame

from logger import Logger
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.prompt_engineering.prompt_engineering_strategy \
    import PromptEngineeringStrategy
from src.sentiment_analysis.prompt_engineering.prompt_engineering_strategy_1 \
    import PromptEngineeringStrategy1
from type_aliases import PromptsDictType, PromptIngredientsType


class PromptEngineer(LoggingMixin):
    """
    This class serves as the context in a strategy pattern, which allows you to
    dynamically choose a prompt engineering strategy at runtime.

    The class works with any of the prompt engineering strategies that
    implement the PromptEngineeringStrategy interface. It gives access to the
    prompt engineering methods of the given prompt engineering strategy.

    Attributes
    ----------
    logger : Logger
        Overrides the default logger of the 'LoggingMixin' class.

    strategy : PromptEngineeringStrategy
        The current prompt engineering strategy in use.

    Methods
    -------
    add_query_cols(samples: DataFrame, chunk: Dict[str, Dict[str, str]])
            -> DataFrame:
        Delegates the task of adding query columns to the provided samples.

    decompose_prompt_part(category: str, prompt_part: str)
            -> List[Tuple[str, str]]:
        Decomposes a prompt part into its basic ingredients.

    default_strategy() -> PromptEngineeringStrategy:
        Returns the default prompt engineering strategy.

    get_all_ingredients() -> Dict[str, List[str]]:
        Returns all prompt ingredients.

    get_basic_and_composed_ingredients() -> List[Tuple[str, str]]:
        Returns a list of tuples of basic and composed ingredients types.

    get_basic_ingredients() -> Dict[str, List[str]]:
        Returns the basic ingredients used in the current strategy.

    get_discarded_prompts() -> Dict[str, Dict[str, str]]:
        Retrieves discarded prompts from the prompt engineering strategy.

    get_prompt_ingredients_sets() -> Dict[str, Dict[str, str]]:
        Returns all prompt ingredients sets.

    get_prompts() -> Dict[str, Dict[str, str]]:
        Retrieves prompts from the current prompt engineering strategy.

    """

    def __init__(
            self,
            my_strategy: PromptEngineeringStrategy | None = None
    ) -> None:
        """
        Constructor.

        Sets the prompt engineering strategy which is supposed to be used for
        prompt engineering. If no strategy is specified when the
        PromptEngineer is called, a default prompt engineering strategy is
        used.

        Parameters
        ----------
        my_strategy : PromptEngineeringStrategy | None
            The prompt engineering strategy to be used. Default value: None.

        """

        # Override the default logger of the 'LoggingMixin' class.
        self.logger: Logger = Logger(self.__class__.__name__).get_logger()

        self._strategy = my_strategy or self.default_strategy()

    # region --- Properties

    @property
    def strategy(self) -> PromptEngineeringStrategy:
        """
        Gets the current prompt engineering strategy.

        Returns
        -------
        PromptEngineeringStrategy
            The prompt engineering strategy currently in use.

        """

        return self._strategy

    @strategy.setter
    def strategy(self, strategy: PromptEngineeringStrategy) \
            -> None:
        """
        Sets the prompt engineering strategy to be used.

        The strategy can be changed at runtime.

        Parameters
        ----------
        strategy : PromptEngineeringStrategy
            The strategy to be used for prompt engineering.

        """

        self._strategy = strategy

    # endregion --- Properties

    # region --- Public Methods

    def get_prompts(self) \
            -> PromptsDictType:
        """
        Retrieves prompts from the current prompt engineering strategy.

        Returns
        -------
        PromptsDictType
            A dictionary with the prompts, where the keys are
            consecutive prompt numbers starting from 1 and the values are
            dictionaries where the keys are position labels and the values
            are the texts to insert at the indicated positions.

        """

        return self.strategy.prompts

    def get_discarded_prompts(self) \
            -> PromptsDictType:
        """
        Retrieves discarded prompts from the prompt engineering strategy.

        Returns
        -------
        PromptsDictType
            A dictionary with the prompts, where the keys are
            consecutive prompt numbers starting from 1 and the values are
            dictionaries where the keys are position labels and the values
            are the texts to insert at the indicated positions.

        """

        return self.strategy.discarded_prompts

    def add_query_cols(self, samples: DataFrame, chunk: PromptsDictType) \
            -> DataFrame:
        """
        Delegates the task of adding query columns to the provided samples.

        Delegates the task of adding query columns to the provided samples
        to the prompt engineering strategies.

        Parameters
        ----------
        samples : DataFrame
            A samples DataFrame to which to add query columns.

        chunk : PromptsDictType
            Chunk of different prompts to use to create queries for each of
            the samples and add them in columns in the samples DataFrame.

        Returns
        -------
        DataFrame
            The provided samples DataFrame with the different query columns
            added.

        """
        return self.strategy.add_query_cols(samples, chunk)

    def get_all_ingredients(self) \
            -> PromptIngredientsType:
        """
        Returns all prompt ingredients.

        Returns
        -------
        PromptIngredientsType
            A dictionary where the keys are prompt ingredients categories
            and the values are lists of possible values the categories can
            have.

        """

        return self.strategy.prompt_ingredients

    def get_prompt_ingredients_sets(self) \
            -> PromptsDictType:
        """
        Returns all prompt ingredients sets.

        Returns
        -------
        PromptsDictType
            A dictionary where the keys are prompt ingredients categories and
            the values are lists of possible values the categories can have.

        """

        return self.strategy.prompt_ingredients_sets

    def get_basic_ingredients(self) \
            -> PromptIngredientsType:
        """
        Returns the basic ingredients used in the current strategy.

        Returns
        -------
        PromptIngredientsType
            A dictionary where the keys are basic prompt ingredients categories
            and the values are lists of possible values the categories can
            have.
        """

        return self.strategy.basic_ingredients

    def get_basic_and_composed_ingredients(self) \
            -> List[Tuple[str, str]]:
        """
        Returns a list of tuples of basic and composed ingredients types.

        Returns
        -------
        List[Tuple[str, str]]
            The list of tuples of basic and composed ingredients types.
            The first element of each tuple is a basic ingredient type and
            the second a composed ingredient type the basic ingredient
            type contributes to compose. A basic ingredient type can
            be used in various composed ingredients types and a composed
            ingredient type usually is composed of multiple basic
            ingredients types.

        """

        return self.strategy.basic_and_composed_ingredients

    def decompose_prompt_part(self, category: str, prompt_part: str) \
            -> List[Tuple[str, str]]:
        """
        Decomposes a prompt part into its basic ingredients.

        Parameters
        ----------
        category : str
            The category of the prompt part to be decomposed.

        prompt_part : str
            The prompt part to be decomposed.

        Returns
        -------
        List[Tuple[str, str]]


        """

        return self.strategy.decompose_prompt_part(category, prompt_part)

    # endregion --- Public Methods

    # region --- Static Methods

    @staticmethod
    def default_strategy() \
            -> PromptEngineeringStrategy:
        """
        Returns the default prompt engineering strategy.

        As default, PromptEngineeringStrategy1 is used.

        Returns
        -------
        PromptEngineeringStrategy
            The PromptEngineeringStrategy1.

        Notes
        -----
        This method is used instead of a class constant to ensure lazy
        instantiation. This approach avoids the overhead of creating a default
        strategy object until it is actually needed.

        """

        return PromptEngineeringStrategy1(1)

    # endregion --- StaticMethods

    # region --- Protected Methods

    # endregion --- Protected Methods
