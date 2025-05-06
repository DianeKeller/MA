"""
tokenization_mixin.py
---------------------
Version 1.0, validated on 2024-09-17

"""

from src.nlp.tokenization.sentence_tokenization_factory import \
    get_sentence_tokenizer
from src.nlp.tokenization.sentence_tokenizer import SentenceTokenizer
from src.nlp.tokenization.word_tokenization_factory import get_word_tokenizer
from src.nlp.tokenization.word_tokenizer import WordTokenizer
from src.utils.data_utils import is_none_or_empty


class TokenizationMixin:
    """
    TokenizationMixin class.

    This mixin provides tokenization capabilities for text data.

    It provides getters and setters for different types of tokenizers (word
    tokenizer, sentence tokenizer, ...), which can be set to use different
    tokenization strategies (nltk, custom strategies, ...).

    It also provides default strategies for the different types of tokenizers.
    The default strategy is 'NoPunctuation' for word tokenization and 'nltk'
    for sentence tokenization.


    Attributes
    ----------
    DEFAULT_SENTENCE_STRATEGY : str
        The name of the default sentence strategy.

    DEFAULT_WORD_STRATEGY : str
        The name of the default word strategy.

    sentence_tokenizer : SentenceTokenizer
        The sentence tokenizer.

    word_tokenizer : WordTokenizer
        The word tokenizer.


    Methods
    -------
    set_sentence_tokenizer(tokenization_strategy_name: str = '') -> None:
        Sets the sentence tokenizer using the specified strategy.

    set_word_tokenizer(tokenization_strategy_name: str = '') -> None:
        Sets the word tokenizer using the specified strategy.

    """

    DEFAULT_SENTENCE_STRATEGY: str = 'Nltk'

    # The nltk "word_tokenize" function counts punctuation as separate
    # words. Therefore, this class chooses to use the 'NoPunctuation' word
    # tokenization strategy by default.

    DEFAULT_WORD_STRATEGY: str = 'NoPunctuation'

    @property
    def sentence_tokenizer(self) \
            -> SentenceTokenizer:
        """
        Gets the sentence tokenizer.

        If no sentence tokenizer has been set, a default sentence strategy is
        used to set it.

        Returns
        -------
        SentenceTokenizer
            The sentence tokenizer.

        """

        if not hasattr(self, '_sentence_tokenizer'):
            self.set_sentence_tokenizer(self.DEFAULT_SENTENCE_STRATEGY)

        return getattr(self, '_sentence_tokenizer', SentenceTokenizer())

    @sentence_tokenizer.setter
    def sentence_tokenizer(self, tokenizer: SentenceTokenizer) \
            -> None:
        """
        Sets the sentence tokenizer.
        """

        setattr(self, '_sentence_tokenizer', tokenizer)

    @property
    def word_tokenizer(self) \
            -> WordTokenizer:
        """
        Gets the word tokenizer.

        If no word tokenizer has been set, the default word tokenization
        strategy is used to set it.

        Returns
        -------
        WordTokenizer
            The word tokenizer.

        """

        if not hasattr(self, '_word_tokenizer'):
            self.set_word_tokenizer(self.DEFAULT_WORD_STRATEGY)

        return getattr(self, '_word_tokenizer', WordTokenizer())

    @word_tokenizer.setter
    def word_tokenizer(self, tokenizer: WordTokenizer) \
            -> None:
        """
        Sets the word tokenizer.
        """

        setattr(self, '_word_tokenizer', tokenizer)

    def set_word_tokenizer(self, tokenization_strategy_name: str = '') \
            -> None:
        """
        Sets the word tokenizer using the specified strategy.

        Parameters
        ----------
        tokenization_strategy_name : str
            The name of the tokenization strategy to use.

        """

        if is_none_or_empty(tokenization_strategy_name):
            tokenization_strategy_name = self.DEFAULT_WORD_STRATEGY

        self.word_tokenizer = get_word_tokenizer(tokenization_strategy_name)

    def set_sentence_tokenizer(self, tokenization_strategy_name: str = '') \
            -> None:
        """
        Sets the sentence tokenizer using the specified strategy.

        Parameters
        ----------
        tokenization_strategy_name : str
            The name of the tokenization strategy to use.

        """

        if is_none_or_empty(tokenization_strategy_name):
            tokenization_strategy_name = self.DEFAULT_SENTENCE_STRATEGY

        self.sentence_tokenizer = get_sentence_tokenizer(
            tokenization_strategy_name)
