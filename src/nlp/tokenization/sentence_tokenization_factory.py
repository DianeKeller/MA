"""
sentence_tokenization_factory.py
--------------------------------
Version 1.0, validated on 2024-12-04

This module provides a function to create a sentence tokenizer that uses a
given tokenization strategy.

Functions
---------
get_sentence_tokenizer(strategy_name: str) -> SentenceTokenizer:
    Returns a SentenceTokenizer using the specified tokenization strategy.

"""

import importlib
import inspect

from logger import Logger

from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.nlp.tokenization.sentence_strategy import SentenceStrategy
from src.nlp.tokenization.sentence_tokenizer import SentenceTokenizer


def get_sentence_tokenizer(strategy_name: str) \
        -> SentenceTokenizer:
    """
    Returns a SentenceTokenizer using the specified tokenization strategy.

    Dynamically creates and returns an instance of the SentenceTokenizer
    class using the specified sentence tokenization strategy.

    Parameters
    ----------
    strategy_name : str
        A string designing the strategy. This is supposed to be the first
        part of the name of the sentence strategy to use, e.g. 'Nltk' for
        NltkSentenceStrategy.

    Returns
    -------
    SentenceTokenizer
        An instance of the SentenceTokenizer class that uses the specified
        sentence tokenization strategy.

    """

    strategy = _get_sentence_tokenization_strategy(strategy_name)
    return SentenceTokenizer(strategy)


def _get_sentence_tokenization_strategy(strategy_name: str) \
        -> SentenceStrategy:
    """
    Returns an instance of the specified sentence tokenization strategy.

    Dynamically creates and returns an instance of the sentence tokenization
    strategy that corresponds to the specified strategy name.

    Parameters
    ----------
    strategy_name : str
        A string designing the strategy. This is supposed to be the first
        part of the name of the sentence strategy to use, e.g. 'Nltk' for
        NltkSentenceStrategy.


    Returns
    -------
    An instance of the specified strategy class.

    Raises
    ------
    CriticalException
        If the specified strategy was not found.

    Notes
    -----
    It is important that the strategy name given is written exactly the
    same as the name of the strategy class, since upper and lower case
    letters cannot be predicted programmatically.

    """

    strategy_name += "SentenceStrategy"
    module_name = "src.nlp.tokenization.sentence_strategy"

    try:
        # Dynamically import the module that contains the strategy class.
        module = importlib.import_module(module_name)

        # Get the strategy class from the module
        strategy = getattr(module, strategy_name)

        # Instantiate and return the strategy
        return strategy()

    except (AttributeError, ImportError) as err:
        raise CriticalException(
            Logger(
                f"{inspect.currentframe().f_code.co_name}"
            ).get_logger(),
            "Strategy '%s' not found. Error: %s" % (strategy_name, err)
        ) from err
