"""
word_tokenizer.py
-----------------
Version 1.0, updated on 2025-05-01

"""

from typing import List

from src.nlp.tokenization.tokenizer import Tokenizer
from src.nlp.tokenization.word_strategy import WordStrategy, \
    NoPunctuationStrategy


class WordTokenizer(Tokenizer):
    """
    WordTokenizer class.

    This class implements the Tokenizer base class for word tokenization.
    It serves as the context in a strategy pattern, which allows you to
    dynamically choose a word tokenization strategy at runtime.

    The class works with any of the word tokenization strategies that implement
    the WordStrategy interface. It gives access to the tokenize method of
    the given word tokenization strategy.

    Attributes
    ----------
    strategy : WordStrategy
        The word tokenization strategy to be used.

    Static Methods
    --------------
    default_strategy() -> SentenceStrategy:
        Returns the default sentence tokenization strategy.

    Methods
    -------
    tokenize(my_string: str) -> List[str]:
        Tokenizes the given string into sentences.

    """

    def __init__(self, my_strategy: WordStrategy | None = None) \
            -> None:
        """
        Constructor.

        Sets the word tokenization strategy which is supposed to be used for
        word tokenization. If no strategy is specified when the
        WordTokenizer is called, a default word tokenization strategy is
        used.

        Parameters
        ----------
        my_strategy : WordStrategy | None
            The word tokenization strategy to be used. Default value: None.

        """

        if not my_strategy:
            my_strategy = self.default_strategy()

        super().__init__(my_strategy)

    @staticmethod
    def default_strategy() \
            -> WordStrategy:
        """
        Returns the default word tokenization strategy.

        As default, NoPunctuationStrategy is used. Its result corresponds to
        the intuitive way of splitting text into words, throwing away any
        punctuation marks but keeping hyphened words as one word and
        currency symbols together with their numbers.

        Returns
        -------
        WordStrategy
            The word tokenization strategy.

        Notes
        -----
        This method is used instead of a class constant to ensure lazy
        instantiation. This approach avoids the overhead of creating a default
        strategy object until it is actually needed.

        """

        return NoPunctuationStrategy()

    def tokenize(self, input_string: str) \
            -> List[str]:
        """
        Tokenizes the given string into words.

        Parameters
        ----------
        input_string : str
            The string to tokenize.

        Returns
        -------
        List[str]
            The list of words extracted from the input string.

        """

        result = self.strategy.tokenize(input_string)

        return result
