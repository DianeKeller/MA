"""
prompts_and_ingredients_provider.py
-----------------------------------
Version 1.0, updated on 2025-05-01

"""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

from logger import Logger
from src.sentiment_analysis.prompt_engineering.prompt_engineer_factory import \
    get_prompt_engineer
from src.sentiment_analysis.sentiment_analysis_config import \
    SentimentAnalysisConfig
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.prompt_engineering.prompts import Prompts
from src.utils.data_utils import is_none_or_empty

if TYPE_CHECKING:
    from src.sentiment_analysis.prompt_engineering import (
        prompts_and_ingredients_manager as manager
    )


class PromptsAndIngredientsProvider(ABC, LoggingMixin):
    """
    PromptsAndIngredientsProvider class.

    This is the base class for different prompts providers, such as the
    PromptsProvider, the DiscardedPromptsProvider and the
    PreviousPromptsProvider classes. It provides logging functionality and
    defines the methods all subclasses must implement and attributes and
    common default methods the subclasses use.

    Attributes
    ----------
    logger : Logger
        The logger instance used for logging within the samples provider
        subclasses.

    Methods
    -------
    def get_prompts(**kwargs) -> Prompts:
        Retrieves and returns prompts for prompt evaluation and optimization.

    """

    def __init__(
            self,
            prompts_manager: "manager.PromptsAndIngredientsManager"
    ):
        """
        Constructor.

        Initializes a new PromptsAndIngredientsProvider instance with a
        PromptsManager instance.

        Parameters
        ----------
        prompts_manager : manager.PromptsAndIngredientsManager
            The PromptsAndIngredientsManager instance that called the
            PromptsProvider to delegate the retrieval of prompts.

        """

        self._invalid_prompt_nrs = None
        self._valid_prompt_nrs = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.prompts_manager: "manager.PromptsAndIngredientsManager" = (
            prompts_manager
        )

        self.config = SentimentAnalysisConfig()

        strategy_nr = int(self.config.get('version'))

        self.prompt_engineer = get_prompt_engineer(strategy_nr)

    # region --- Properties

    @property
    def invalid_prompt_nrs(self) \
            -> List[int]:
        """
        Retrieves the list of invalid prompt numbers.

        Returns
        -------
        List[int]
            The list of invalid prompt numbers.

        """

        if is_none_or_empty(self._invalid_prompt_nrs):
            self._set_valid_and_invalid_prompt_nrs()

        return self._invalid_prompt_nrs

    @invalid_prompt_nrs.setter
    def invalid_prompt_nrs(self, nrs: List[int]) -> None:
        """
        Sets the invalid prompt numbers.

        Parameters
        ----------
        nrs : List[int]
            A list of integers representing invalid prompt numbers.

        """

        self._invalid_prompt_nrs = nrs

    @property
    def valid_prompt_nrs(self) \
            -> List[int]:
        """
        Retrieves the list of valid prompt numbers.

        Returns
        -------
        List[int]
            The list of valid prompt numbers.

        """

        if is_none_or_empty(self._valid_prompt_nrs):
            self._set_valid_and_invalid_prompt_nrs()

        return self._valid_prompt_nrs

    @valid_prompt_nrs.setter
    def valid_prompt_nrs(self, nrs: List[int]) -> None:
        """
        Sets the valid prompt numbers.

        Parameters
        ----------
        nrs : List[int]
            A list of integers representing valid prompt numbers.

        """

        self._valid_prompt_nrs = nrs

    # endregion --- Properties

    # region --- Public Methods

    @abstractmethod
    def get_prompts(self, **kwargs) \
            -> Prompts:
        """
        Retrieves and returns prompts for prompt evaluation and optimization.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments.

        Returns
        -------
        Prompts
            The prompts for prompt evaluation and optimization.

        Raises
        ------
        NotImplementedError
            If the subclass does not implement this abstract method.


        Notes
        -----
        A prompt is a set of prompt parts.

        """

        raise NotImplementedError

    # endregion --- Public Methods

    # region --- Protected Methods

    def _set_valid_and_invalid_prompt_nrs(self) \
            -> None:
        """
        Sets valid and invalid prompt numbers.

        Iterates through each chunk and checks whether for each query number
        exists. If it does, the query number is added to the list of valid
        prompts numbers, otherwise to the list of invalid prompt numbers.

        At the end, the valid and invalid prompt numbers are stored in the
        corresponding properties.

        """

        valid_nrs = []
        invalid_nrs = []
        prompts_manager = self.prompts_manager

        for chunk_nr, chunk in prompts_manager.chunks.items():
            for query_nr in range(
                    (chunk_nr - 1) * prompts_manager.chunk_size + 1,
                    chunk_nr * prompts_manager.chunk_size + 1
            ):
                if f"answer_{str(query_nr)}" in chunk.df.columns:
                    valid_nrs.append(query_nr)
                else:
                    invalid_nrs.append(query_nr)

        self.valid_prompt_nrs = valid_nrs
        self.invalid_prompt_nrs = invalid_nrs

    # endregion --- Protected Methods

    # region --- Private Methods

    # endregion --- Private Methods
