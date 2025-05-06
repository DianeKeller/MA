"""
word_strategy.py
----------------
Version 1.0, updated on 2024-09-18

This module contains classes for word tokenization, namely the
WordStrategy base class and concrete word strategy subclasses.

Classes
-------
WordStrategy(TokenizationStrategy, LoggingMixin)
    Base class for word tokenization.

NoPunctuationStrategy(WordStrategy)
    Word tokenization strategy that eliminates the punctuation.

"""

from __future__ import annotations

from abc import abstractmethod
from typing import List

from src.nlp.tokenization.tokenization_strategy import TokenizationStrategy
from src.nlp.tokenization.word_tokenization_regex import (
    regex_penn_treebank_wo_punctuation
)
from src.utils.string_search_utils import find_all_matches


class WordStrategy(TokenizationStrategy):
    """
    WordStrategy class.

    The WordStrategy interface declares operations common to all supported word
    tokenization strategies.

    The Context uses this interface to call the algorithm defined by Concrete
    Strategies.

    Methods
    -------
    log_tokenization_result(self, words: List[str]) -> None:
        Logs the tokenization result if the verbose property is set to True.

    Abstract Methods
    ----------------
    tokenize(self, self, input_string: str) -> List[str]:
        Tokenizes the input string.

    """

    def log_tokenization_result(self, words: List[str]) \
            -> None:
        """
        Logs the tokenization result if the verbose property is set to True.

        Parameters
        ----------
        words : List[str]
            The words the inputs string has been tokenized into.

        """

        if self.verbose:
            msg = ("%d words tokenized by %s"
                   % (len(words), self.__class__.__name__))
            self._log(msg, 'info')

    @abstractmethod
    def tokenize(self, input_string: str) \
            -> List[str]:
        """
        Tokenizes the input string.

        Abstract method that needs to be implemented by the concrete
        sentence strategy class.

        Parameters
        ----------
        input_string : str
            The string to tokenize into words.

        Returns
        -------
        List[str]
            The words extracted by the tokenizer from the input_string.

        Raises
        ------
        NotImplementedError
            If the concrete sentence strategy class has not implemented this
            abstract method.

        """

        raise NotImplementedError(
            "The 'tokenize' method must be implemented by subclasses."
        )


class NoPunctuationStrategy(WordStrategy):
    """
    This word tokenization strategy eliminates punctuation marks.

    """

    def tokenize(self, input_string: str) \
            -> List[str]:
        """
        Splits string into words.

        Splits string into words only, throws away the punctuation.
        Preserves
            - abbreviations
            - hyphened words
            - floats
            - currency and percent, together with number
            - ellipses.


        Split examples:

        'the idea is good. but that u.s.a. poster-print costs $12.40...'
        => ['the', 'idea', 'is', 'good', 'but', 'that', 'u.s.a.',
            'poster-print', 'costs', '$12.40', '...']),

        'This is a - very short but nice - little text. It contains but 2 ' \
        'sentences.'
        => ['this', 'is', 'a', 'very', 'short', 'but', 'nice', 'little',
            'text', 'it', 'contains', 'but', '2', 'sentences']
        
        """

        regex = regex_penn_treebank_wo_punctuation()
        results, _ = find_all_matches(input_string, regex)

        # Using list comprehension:
        words = [str(r['match']) for r in results]

        self.log_tokenization_result(words)

        return words
