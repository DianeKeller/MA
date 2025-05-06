"""
sentiment_analysis_config.py
----------------------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

import inspect
from typing import TypeVar, Dict, Any

from logger import Logger
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.print_utils import print_in_box

T = TypeVar('T', bound='Llm')


class SentimentAnalysisConfig:
    """
    SentimentAnalysisConfig class.

    This static class is used to store and manage user-defined and other
    settings for the sentiment analysis workflows. It follows a singleton
    pattern, which ensures that only one instance of this class exists at any
    time throughout the application while being accessible globally from all
    classes.

    Attributes
    ----------
    _instance : SentimentAnalysisConfig
        The singleton instance of the class.

    _settings : Dict[str, Any]
        A dictionary to store the configuration settings.

    _initialized : bool
        A flag indicating whether the configuration has been initialized.

    Methods
    -------
    get(cls, key: str) -> Any:
        Retrieves the value associated with a given key from the settings.

    set(cls, key: str, val: Any) -> None:
        Sets the value for a given key in the settings.

    remove(cls, key: str) -> None:
        Removes a key-value pair from the settings.

    update(cls, **kwargs) -> None:
        Updates multiple settings at once based on provided keyword arguments.

    print(cls) -> None:
        Prints the current settings.

    to_str(cls) -> str:
        Returns a string representation of the current settings.

    """

    _instance: SentimentAnalysisConfig | None = None
    _settings: Dict[str, Any] = {}
    _initialized: bool = False

    log = LoggingMixin().log

    def __new__(cls, *args: Any, **kwargs: Any) \
            -> SentimentAnalysisConfig:
        """
        Creates and initializes a singleton instance of this class.

        Creates a new instance of this class if one does not already exist and
        initializes it with any provided parameters.

        Returns
        -------
        SentimentAnalysisConfig
            The singleton instance of the class.

        Notes
        -----
        For the arguments and keyword arguments that can be passed as
        parameters, see the parameters of the _initialize method.

        """

        if cls._instance is None:
            cls._instance = super(SentimentAnalysisConfig, cls).__new__(cls)

        cls._initialize(*args, **kwargs)
        return cls._instance

    @classmethod
    def _initialize(
            cls,
            api: str = '',
            llm: T | None = None,
            from_sample: int = 0,
            to_sample: int = 9999999,
            batch_size: int = 100,
            data_offset: int = 0,
            n_batches: int = 1,
            chunk_size: int = 15,
            version: str = '00',
            balance: int = 33,
            balanced: bool = False,
            n_best_prompts: int = 5,
            target_n_prompts: int = 150,
            with_validation: bool = True,
    ) -> None:
        """
        Initializes the configuration settings with the provided values.

        Parameters
        ----------
        - api : str
            API for the queries to the LLM. Will be set when a concrete Llm
            instance like ServerlessBloom is initiated.

        - llm : T | None
            A concrete Llm instance like ServerlessBloom. Is set when a
            concrete Llm instance is created.

        - from_sample : int
            Sample number from which to start any operations. Defines the
            first part of the subdirectory's name where the data are stored.

        - to_sample : int
            Sample number at which to stop any operations. Defines the
            second part of the subdirectory's name where the data are stored.

        - batch_size : int
            Number of samples to process in a batch. Defaults to 100. If the
            "balanced" parameter is set to "True", the batch size should
            accordingly be set to a multiple of 3 times the "balance"
            parameter value.

        - data_offset : int
            Sample number from which to start any operations. Data in the
            samples DataFrame will be removed before the rest of the data is
            processed. Has no implications regarding the (sub)directory where
            the data are stored.

        - n_batches : int
            Number of batches to process. Defaults to 1.

        - chunk_size : int
            Number of queries to include in one chunk. Defaults to 15.

        - version : str
            Version of prompt sets/validated queries to use to build chunks
            from.

        - balanced : bool
            Whether to construct and use a balanced dataset where each
            sentiment category appears as often as the other sentiment
            categories.

        - balance : int
            Number of samples of the same sentiment category (positive/
            negative/neutral) to use to build a balanced dataset.
            Defaults to 33. If the "balanced" parameter is set to "True" The
            batch size should accordingly be set to a multiple of the
            "balance" value.

        - n_best_prompts : int
            The number of prompts that are to be included in the lists of
            best and worst prompts. The analysis will show the n
            best prompts and the n worst prompts.

        - target_n_prompts : int
            The total number of prompt variants to generate or to load from
            the JSON files (prompt_sets_history, validated_queries).
            Defaults to 150, because each query applied on 100 samples takes
            about 1 minute. The rate limit being approximately 1500 prompts,
            thus 15 different queries for 100 samples, and the waiting time
            being set to 63 minutes, 15 queries need about 80 minutes. So,
            extracting 150 examples and processing them will take about 13.5
            hours, which is feasible if it is only done for one language.

        - with_validation : bool
            Whether the retrieval results should be checked for validity,
            rejecting 'invalid' results. Should be set to True for prompt
            engineering, and to "False" for production. Default: True.

        """

        if not cls._initialized:
            cls.set('api', api)
            cls.set('llm', llm)
            cls.set('from_sample', from_sample)
            cls.set('to_sample', to_sample)
            cls.set('batch_size', batch_size)
            cls.set('data_offset', data_offset)
            cls.set('n_batches', n_batches)
            cls.set('chunk_size', chunk_size)
            cls.set('version', version)
            cls.set('balance', balance)
            cls.set('balanced', balanced)
            cls.set('n_best_prompts', n_best_prompts)
            cls.set('target_n_prompts', target_n_prompts)
            cls.set('with_validation', with_validation)

            cls._initialized = True

    @classmethod
    def get(cls, key: str) \
            -> Any:
        """
        Retrieves the value associated with a given key from the settings.

        Parameters
        ----------
        key : str
            The key to get from the settings.

        """

        return cls._settings.get(key)

    @classmethod
    def set(cls, key: str, val: Any) \
            -> None:
        """
        Sets the value for a given key in the settings.

        Parameters
        ----------
        key : str
            The key to set in the settings.

        val : Any
            The value to associate with the key.

        """

        cls._settings[key] = val

    @classmethod
    def validate(cls) \
            -> None:
        """
        Validates config settings for logical consistency.

        Raises
        ------
        CriticalException
            If the config settings are invalid.

        Usage
        -----
        >>> SentimentAnalysisConfig.validate()

        """

        batch_size = cls.get('batch_size')
        balance = cls.get('balance')
        balanced = cls.get('balanced')

        if balanced and batch_size % (3 * balance) != 0:
            raise CriticalException(
                Logger(
                    f"{inspect.currentframe().f_code.co_name}"
                ).get_logger(),
                (
                    "Batch size must be a multiple of 3 times the balance "
                    "value when balanced=True."
                )
            )

    @classmethod
    def remove(cls, key: str) \
            -> None:
        """
        Removes a key-value pair from the settings.

        Parameters
        ----------
        key : str
            The key to remove from the settings.

        """

        if key in cls._settings:
            del cls._settings[key]

    @classmethod
    def update(cls, **kwargs) \
            -> None:
        """
        Updates multiple settings at once based on provided keyword arguments.

        Parameters
        ----------
        kwargs : Any
            Key-value pairs of settings to update.

        Examples
        --------
        >>> config = SentimentAnalysisConfig()
        >>> config.update(version='01', balanced=True)

        """

        for key, value in kwargs.items():
            cls.set(key, value)

    @classmethod
    def reset_instance(cls) \
            -> None:
        """
        Resets the single instance of this class.

        This method is needed to reinitialize the class for test purposes.

        """

        cls._instance = None
        cls._initialized = False

    @classmethod
    def print(cls) \
            -> None:
        """
        Prints the current settings.
        """

        title = "Settings in SentimentAnalysisConfig"
        body = cls.to_str()
        print_in_box(title, body)

    @classmethod
    def to_str(cls) \
            -> str:
        """
        Returns a string representation of the settings.

        Returns
        -------
        str
            The string representation of the settings.

        """

        string = ''
        for key, val in cls._settings.items():
            string = f"{string}{key}:\t{val}\n"

        return string
