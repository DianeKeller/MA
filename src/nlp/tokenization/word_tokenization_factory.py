"""
word_tokenization_factory.py
----------------------------
Version 1.0, validated on 2024-12-04

This module provides a function to create a word tokenizer that uses a
given tokenization strategy.

Functions
---------
get_word_tokenizer(strategy_name: str) -> WordTokenizer:
    Returns a WordTokenizer using the specified tokenization strategy.

"""

import importlib
import inspect

from logger import Logger

from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.nlp.tokenization.word_strategy import WordStrategy
from src.nlp.tokenization.word_tokenizer import WordTokenizer


def get_word_tokenizer(strategy_name: str) \
        -> WordTokenizer:
    """
    Dynamically creates and returns an instance of the WordTokenizer
    class using the specified word tokenization strategy.

    Parameters
    ----------
    strategy_name : str
        A string designing the strategy. This is supposed to be the first
        part of the name of the word strategy to use, e.g. 'NoPunctuation'
        for NoPunctuationStrategy.

    Returns
    -------
    WordTokenizer
        An instance of the WordTokenizer class that uses the specified
        word tokenization strategy.

    """

    strategy = _get_word_tokenization_strategy(strategy_name)
    return WordTokenizer(strategy)


def _get_word_tokenization_strategy(strategy_name: str) \
        -> WordStrategy:
    """
    Returns an instance of the specified word tokenization strategy.

    Dynamically creates and returns an instance of the word
    strategy that corresponds to the specified strategy name.

    Parameters
    ----------
    strategy_name : str
        A string designing the strategy. This is supposed to be the first
        part of the name of the word strategy to use, e.g. 'NoPunctuation'
        for NoPunctuationStrategy.


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

    strategy_name += "Strategy"
    module_name = "src.nlp.tokenization.word_strategy"

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
