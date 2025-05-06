"""
sentence_strategy.py
---------------------
Version 1.0, validated on 2024-09-14

This module contains classes for sentence tokenization, namely the
SentenceStrategy base class and concrete sentence strategy subclasses.

Classes
-------
SentenceStrategy(TokenizationStrategy, LoggingMixin)
    Base class for sentence tokenization.

NltkSentenceStrategy(SentenceStrategy)
    Sentence tokenization strategy using the standard NLTK sentence tokenizer.

RegexWithColonsSentenceStrategy(SentenceStrategy)
    Sentence tokenization strategy using a regex that considers colons to be
    end-of-sentence characters to identify sentences within the input
    string.

"""

from __future__ import annotations

import re
from abc import abstractmethod
from typing import List

import nltk

from src.nlp.tokenization.sentence_tokenization_regex import regex_with_colons
from src.nlp.tokenization.tokenization_strategy import TokenizationStrategy
from src.utils.string_search_utils import find_all_matches


class SentenceStrategy(TokenizationStrategy):
    """
    SentenceStrategy class.

    The SentenceStrategy interface declares operations common to all supported
    sentence tokenization strategies.

    The Context uses this interface to call the algorithm defined by concrete
    strategies.


    Methods
    -------
    clean_and_log_result(self, sentences: List[str]) -> List[str]:
        Removes leading and trailing whitespace from the sentences.

    log_tokenization_result(self, sentences: List[str]) -> None:
        Logs the tokenization result if the verbose property is set to True.
    
    tokenize_by_regex(self, input_string: str, regex: re.Pattern) -> List[str]:
        Tokenizes the input string into sentences using the given regex.
    
    Abstract Methods
    ----------------
    tokenize(self, self, input_string: str) -> List[str]:
        Tokenizes the input string.

    """

    def __init__(self):
        super().__init__()

    # region --- Public Methods

    def clean_and_log_result(self, sentences: List[str]) \
            -> List[str]:
        """
        Removes leading and trailing whitespace from the sentences.

        Removes leading and trailing whitespace from the sentences and
        calls the log_tokenization_result method to log the sentences.

        Parameters
        ----------
        sentences : List[str]
            The list of sentences.

        Returns
        -------
        List[str]
            The list of sentences stripped of leading and trailing whitespace
            whitespace.

        """

        # Remove leading and trailing whitespace from each sentence
        clean_sentences = [sentence.strip() for sentence in sentences]
        self.log_tokenization_result(clean_sentences)

        return clean_sentences

    def tokenize_by_regex(
            self,
            input_string: str,
            regex: re.Pattern
    ) -> List[str]:
        """
        Tokenizes the input string into sentences using the given regex.

        Tokenizes the input string into sentences using the given regular
        expression. Cleans the sentences from unwished whitespace before
        returning them.

        Parameters
        ----------
        input_string : str
            The string to tokenize into sentences.

        regex : re.Pattern
            The regular expression to use to identify a sentence.

        Returns
        -------
        List[str]
            The resulting list of cleaned sentences.

        """

        results, _ = find_all_matches(
            input_string, regex, verbose=self.verbose
        )

        # If no sentences could be identified in the input string, clean the
        # input string and return it as a single sentence.
        if not results:
            sentence = input_string.strip()
            return [sentence]

        # Get the found sentences from the results sequence.
        sentences = [str(r['match']) for r in results]

        return self.clean_and_log_result(sentences)

    def log_tokenization_result(self, sentences: List[str]) \
            -> None:
        """
        Logs the tokenization result if the verbose property is set to True.

        Parameters
        ----------
        sentences : List[str]
            The sentences the inputs string has been tokenized into.

        """

        if self.verbose:
            msg = ("%d sentences tokenized by %s"
                   % (len(sentences), self.__class__.__name__))
            self._log(msg, 'info')

    # endregion --- Public Methods

    # region --- Abstract Methods

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
            The string to tokenize into sentences.

        Returns
        -------
        List[str]
            The sentences extracted by the tokenizer from the input_string.

        Raises
        ------
        NotImplementedError
            If the concrete sentence strategy class has not implemented this
            abstract method.

        """

        raise NotImplementedError(
            "The 'tokenize' method must be implemented by subclasses."
        )

    # endregion --- Abstract Methods


class NltkSentenceStrategy(SentenceStrategy):
    """
    This sentence tokenization strategy uses the standard NLTK sentence
    tokenizer.

    """

    def tokenize(self, input_string: str) \
            -> List[str]:
        """
        Split into sentences using NLTK sent_tokenize method.

        Parameters
        ----------
        input_string : str
            The text to split into sentences.

        Returns
        -------
        List[str]
            The resulting list of sentences.

        """

        sentences = nltk.sent_tokenize(input_string)
        self.log_tokenization_result(sentences)

        return sentences


class RegexWithColonsSentenceStrategy(SentenceStrategy):
    """
    This sentence tokenization strategy uses a custom regular expression
    to split the text into sentences.

    It considers colons to be end-of-sentence characters.

    """

    def tokenize(self, input_string: str) \
            -> List[str]:
        """
        Splits a string into sentences using a custom regular expression.

        Keeps the punctuation marks.

        This strategy considers colons to be end-of-sentence characters.

        Parameters
        ----------
        input_string : str
            The text to split into sentences.

        Returns
        -------
        List[str]
            The resulting list of sentences.

        Notes
        -----
        The split into sentences is done by matching the text with a regular
        expression and not by a split at end-of-sentence characters or
        character sequences, as this way the punctuation information (Question,
        exclamation, etc.) is preserved.

        """

        self.verbose = False

        regex = regex_with_colons()

        return self.tokenize_by_regex(input_string, regex)
