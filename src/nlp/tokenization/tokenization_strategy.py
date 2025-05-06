"""
tokenization_strategy.py
------------------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from logger import Logger
from src.logging_mixin import LoggingMixin


class TokenizationStrategy(ABC, LoggingMixin):
    """
    TokenizationStrategy class.

    The TokenizationStrategy interface declares operations common to all
    supported tokenization strategies.

    The Context uses this interface to call the algorithm defined by concrete
    Strategies.

    Attributes
    ----------
    logger : Logger
        A Logger instance for logging messages related to the operations
        performed by the class and its subclasses.

    verbose : bool
        Whether the tokenized elements should be printed to the
        console.

    Abstract Methods
    ----------------
    tokenize(self, input_string: str) -> List[str]:
        Tokenizes the input string.

    """

    def __init__(self) \
            -> None:
        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self._verbose = False

    @property
    def verbose(self) \
            -> bool:
        """
        Indicates whether the tokenized elements should be printed.

        Indicates whether the tokenized elements should be printed to
        the console.

        """

        return self._verbose

    @verbose.setter
    def verbose(self, value: bool) \
            -> None:
        """
        Sets the verbose property.
        """

        self._verbose = value

    @abstractmethod
    def tokenize(self, input_string: str) \
            -> List[str]:
        """
        Tokenizes the input string.

        Parameters
        ----------
        input_string : str
            The string to tokenize.

        Returns
        -------
        List[str]
            List of strings (sentences, words, characters) the input string
            was tokenized into.

        """
