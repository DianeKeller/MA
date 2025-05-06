"""
tokenizer.py
------------
Version 1.0, updated on 2024-12-04

"""

from __future__ import annotations

from abc import abstractmethod, ABC
from typing import List

from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.logging_mixin import LoggingMixin
from src.nlp.tokenization.tokenization_strategy import TokenizationStrategy


class Tokenizer(ABC, LoggingMixin):
    """
    Tokenizer class.

    This class defines the interface for applying different tokenization
    strategies to input strings. It acts as a context for the
    TokenizationStrategy and enforces that any subclass must implement the
    'tokenize' method.

    Attributes
    ----------
    strategy : TokenizationStrategy
        The tokenization strategy to use for tokenizing input strings.

    Abstract Methods
    ----------------
    tokenize(self, input_string: str) -> List[str]:
        Tokenizes the input string.

    """

    def __init__(self, my_strategy: TokenizationStrategy | None = None) \
            -> None:
        """
        Constructor.

        Initializes the Tokenizer with a specific tokenization strategy.
        If no strategy is provided, an error is logged, and a ValueError
        is raised.

        Parameters
        ----------
        my_strategy : TokenizationStrategy | None
            The tokenization strategy to use. If not provided, a ValueError
            is raised.

        Raises
        ------
        CriticalException
            If no tokenization strategy is provided.

        """

        if not my_strategy:
            raise CriticalException(
                self.logger,
                "No tokenization strategy defined. Cannot tokenize."
            )

        self.strategy = my_strategy

    # region --- Properties

    @property
    def strategy(self) -> TokenizationStrategy:
        """
        Returns the current tokenization strategy used by the tokenizer.

        The strategy follows the Strategy design pattern, allowing the
        Tokenizer to work with different tokenization strategies through
        a common interface.

        Returns
        -------
        TokenizationStrategy
            The current tokenization strategy.

        """

        return self._strategy

    @strategy.setter
    def strategy(self, strategy: TokenizationStrategy) \
            -> None:
        """
        Sets the tokenization strategy.

        Allows replacing a Strategy object at runtime.

        Parameters
        ----------
        strategy : TokenizationStrategy
            The tokenization strategy to use.

        """

        self._strategy = strategy

    # endregion --- Properties

    # region --- Methods

    @abstractmethod
    def tokenize(self, input_string: str) \
            -> List[str]:
        """
        Tokenizes the input string.

        Abstract method that must be implement by subclasses. Takes a
        string and returns a list of tokens based on the specific
        tokenization strategy.

        Parameters
        ----------
        input_string : str
            The input string to tokenize.

        Returns
        -------
        List[str]: A list of tokens generated from the input string.

        """

    # endregion --- Methods
