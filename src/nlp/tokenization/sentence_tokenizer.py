"""
sentence_tokenizer.py
---------------------
Version 1.0, updated on 2025-05-01

"""

from typing import List

from src.nlp.tokenization.sentence_strategy import NltkSentenceStrategy, \
    SentenceStrategy
from src.nlp.tokenization.tokenizer import Tokenizer


class SentenceTokenizer(Tokenizer):
    """
    SentenceTokenizer class.

    This class implements the Tokenizer base class for sentence tokenization.
    It serves as the context in a strategy pattern, which allows you to
    dynamically choose a sentence tokenization strategy at runtime.

    The class works with any of the sentence tokenization strategies that
    implement the SentenceStrategy interface. It gives access to the tokenize
    method of the given sentence tokenization strategy.

    Attributes
    ----------
    my_strategy : SentenceStrategy
        The sentence tokenization strategy to be used.

    Static Methods
    --------------
    default_strategy() -> SentenceStrategy:
        Returns the default sentence tokenization strategy.

    Methods
    -------
    tokenize(my_string: str) -> List[str]:
        Tokenizes the given string into sentences.

    """

    def __init__(self, my_strategy: SentenceStrategy | None = None) \
            -> None:
        """
        Constructor.

        Sets the sentence tokenization strategy which is supposed to be used
        for sentence tokenization. If no strategy is specified when the
        SentenceTokenizer is called, a default sentence tokenization
        strategy is used.

        Parameters
        ----------
        my_strategy : SentenceStrategy | None
            The sentence tokenization strategy to be used. Default value: None.

        """

        if not my_strategy:
            my_strategy = self.default_strategy()

        super().__init__(my_strategy)

    @staticmethod
    def default_strategy() \
            -> SentenceStrategy:
        """
        Returns the default sentence tokenization strategy.

        As default, NltkSentenceStrategy is used. It is the standard
        sentence tokenization method of the nltk library and works reasonably
        well.

        Returns
        -------
        SentenceStrategy
            The sentence tokenization strategy.

        Notes
        -----
        This static method is used instead of a class constant to ensure lazy
        instantiation. This approach avoids the overhead of creating a default
        strategy object until it is actually needed.

        """

        return NltkSentenceStrategy()

    def tokenize(self, input_string: str) \
            -> List[str]:
        """
        Tokenizes the given string into sentences.

        Parameters
        ----------
        input_string : str
            The string to tokenize.

        Returns
        -------
        List[str]
            The list of sentences extracted from the input string.

        """

        result = self.strategy.tokenize(input_string)

        return result
