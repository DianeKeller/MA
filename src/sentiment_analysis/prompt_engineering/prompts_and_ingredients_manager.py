"""
prompts_and_ingredients_manager.py
----------------------------------
Version 1.0, updated on 2025-02-07

"""

from typing import Dict

from logger import Logger
from src.data_structures.my_data_frame import MyDataFrame
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.prompt_engineering import (
    previous_ingredients_sets_provider as prev_ingr_sets_provider
)
from src.sentiment_analysis.prompt_engineering.ingredients_sets_provider \
    import IngredientsSetsProvider
from src.sentiment_analysis.prompt_engineering.previous_prompts_provider \
    import PreviousPromptsProvider
from src.sentiment_analysis.prompt_engineering.prompts import Prompts
from src.sentiment_analysis.prompt_engineering.prompts_provider import (
    PromptsProvider
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)


class PromptsAndIngredientsManager(LoggingMixin):
    """
    PromptsAndIngredientsManager class.



    """

    VALID_PROMPTS_NAME = "valid_prompts"
    INVALID_PROMPTS_NAME = "invalid_prompts"
    ALL_PROMPTS_NAME = "all_prompts"

    VALID_INGREDIENTS_SETS_NAME = "valid_ingredients_sets"
    INVALID_INGREDIENTS_SETS_NAME = "invalid_ingredients_sets"
    ALL_INGREDIENTS_SETS_NAME = "all_ingredients_sets"

    def __init__(
            self,
            language: str = 'en',
            chunks: Dict[int, MyDataFrame] = None
    ):
        """
        Constructor.

        Initializes the PromptsAndIngredientsManager class with the specified
        parameters.

        Parameters
        ----------
        language : str
           Language code (default is 'en').

        chunks : Dict[int, MyDataFrame]
            Data chunks dictionary, where the keys are the integer numbers
            of the chunks and the value is a MyDataFrame with the chunk data.

        """

        # Protected variables to store the property values of this class

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.language: str = language
        self.chunks: Dict[int, MyDataFrame] = chunks

        # Configs used in this class
        self.config = SentimentAnalysisConfig()

        self.chunk_size: int = self.config.get('chunk_size')

        # Providers
        self.prompts_provider = PromptsProvider(self)

        self.ingredients_sets_provider = IngredientsSetsProvider(self)

        self.previous_prompts_provider = PreviousPromptsProvider(self)

        self.previous_ingredients_sets_provider = (
            prev_ingr_sets_provider.PreviousIngredientsSetsProvider(self)
        )

        # Whether previous_prompts_provider and
        # previous_ingredients_sets_provider should be used
        # Default is False, value is set to true by the prompt optimizer.
        self.check_previous: bool = False

    # region --- Properties
    @property
    def all_prompts(self) \
            -> Prompts:
        """
        Retrieves all prompts from the PromptsAndIngredientsProvider class.

        Returns
        -------
        Prompts
            All prompts.

        Notes
        -----
        Computed property without setter for lazy loading.

        """

        return self.prompts_provider.get_prompts('all')

    @property
    def discarded_prompts(self) \
            -> Prompts:
        """
        Retrieves the discarded prompts from the PromptsAndIngredientsProvider.

        Returns
        -------
        Prompts
            The discarded prompts.

        Notes
        -----
        Computed property without setter for lazy loading.

        """

        return self.prompts_provider.get_prompts('discarded')

    @property
    def valid_prompts(self) \
            -> Prompts:
        """
        Retrieves the valid prompts from the PromptsAndIngredientsProvider.

        Returns
        -------
        Prompts
            The valid prompts.

        Notes
        -----
        Computed property without setter for lazy loading.

        """

        return self.prompts_provider.get_prompts('valid')

    @property
    def invalid_prompts(self) \
            -> Prompts:
        """
        Retrieves the invalid prompts from the PromptsAndIngredientsProvider.

        Returns
        -------
        Prompts
            The invalid prompts.

        Notes
        -----
        Computed property without setter for lazy loading.

        """

        return self.prompts_provider.get_prompts('invalid')

    @property
    def previous_valid_prompts(self) \
            -> Prompts:
        """
        Retrieves the previous valid prompts.

        Returns
        -------
        Prompts
            The previous valid prompts.

        Notes
        -----
        Computed property without setter for lazy loading.

        """

        return self.previous_prompts_provider.get_prompts('valid')

    @property
    def all_ingredients_sets(self) \
            -> Prompts:
        """
         Retrieves all prompt ingredients sets.

         Returns
         -------
         Prompts
             The prompt ingredients sets.

         Notes
         -----
         Computed property without setter for lazy loading.

         """

        return self.ingredients_sets_provider.get_prompts('all')

    @property
    def valid_ingredients_sets(self) \
            -> Prompts:
        """
        Retrieves the valid prompt ingredients sets.

        Returns
        -------
        Prompts
            The valid prompt ingredients sets.

        Notes
        -----
        Computed property without setter for lazy loading.

        """

        return self.ingredients_sets_provider.get_prompts('valid')

    @property
    def invalid_ingredients_sets(self) \
            -> Prompts:
        """
        Retrieves the invalid prompt ingredients sets.

        Returns
        -------
        Prompts
            The invalid prompt ingredients sets.

        Notes
        -----
        Computed property without setter for lazy loading.

        """

        return self.ingredients_sets_provider.get_prompts('invalid')

    @property
    def previous_valid_ingredients_sets(self) \
            -> Prompts:
        """
        Retrieves the previous valid prompt ingredients sets.

        Returns
        -------
        Prompts
            The previous valid prompt ingredients sets.

        Notes
        -----
        Computed property without setter for lazy loading.

        """

        return self.previous_ingredients_sets_provider.get_prompts('valid')

    # endregion --- Properties

    # region --- Public Methods

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
