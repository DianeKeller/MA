"""
llm.py
------
Version 1.0, updated on 2025-05-01

"""

from abc import abstractmethod, ABC
from typing import List, TypeVar

from logger import Logger
from src.decorators.attribute_chain_decorators import (
    self_attribute_chain_not_none
)
from src.decorators.data_check_decorators import requires_property
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.language_processor import (
    LanguageProcessor
)
from src.sentiment_analysis.samples.samples_manager import SamplesManager
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.utils.data_utils import is_none_or_empty
from src.utils.list_utils import get_common_elements

T = TypeVar('T', bound='DataSourceSuite')


class Llm(ABC, LoggingMixin):
    """
    Llm class.

    Abstract base class for LLM implementations.

    This class provides shared functionality for LLM's and enforces
    implementation of critical methods ('_set_suite' and '_add_api_to_config')
    in subclasses such as 'ServerlessBloom'.

    It provides logging functionality through the LoggingMixin.

    The Llm class and its child classes basically provide two
    functionalities: prompt engineering and sentiment retrieval from the
    LLM's API.

    Attributes
    ----------
    logger : logging.Logger
            Logger instance used for logging messages.

    compatible_languages : List[str]
        The languages that both the data suite and the llm understand.

    config : SentimentAnalysisConfig
        Configuration object that holds sentiment analysis settings.

    languages : List[str]
        The list of languages the LLM understands.

    non_query_cols : List[str]
        The list of non-query columns in the dataset.

    samples_manager : SamplesManager
        A SamplesManager instance that is needed to retrieve any samples
        from the suite.

    suite : DataSourceSuite
        The suite from which to get the data samples.


    Methods
    -------
    predict_sentiments() -> None:
        Retrieves the sentiment predictions for all languages.

    predict_sentiments_in_language(language: str = 'en') -> None:
        Retrieves the sentiment predictions for the specified language.

    """

    def __init__(self):
        """
        Constructor.

        Initializes the Llm class, setting up essential components for
        sentiment analysis and prompt engineering. It initializes internal
        properties, configures logging and prepares sentiment analysis
        settings specific to the implementation of the LLM.

        Notes
        -----
        - The method calls '_add_api_to_config' and
          '_add_llm_instance_to_config' to ensure the LLM-specific API details
          are added to the configuration and the current class instance is
          registered.

        """

        # Protected variables to store the property values of this class
        self._samples_manager = None
        self._non_query_cols = None
        self._compatible_languages: List[str] = []

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        # Make the sentiment analysis configuration available in this class
        self.config = SentimentAnalysisConfig()

        # Complete the sentiment analysis configuration with settings that
        # depend on the concrete LLM
        self._add_api_to_config()
        self._add_llm_instance_to_config()

    # region --- Properties

    @property
    def name(self) \
            -> str:
        """
        Returns the LLM instance's name.

        Notes
        -----
        Computed property without setter.

        """

        return self.__class__.__name__

    @property
    def compatible_languages(self) \
            -> List[str]:
        """
        Returns the languages that both the data suite and the llm understand.

        Returns
        -------
        List[str]
            The list of languages the data suite and the llm understand.

        Notes
        -----
        This is a computed property that has no setter method. If the
        property is not set when called, it calls the decorated
        _set_compatible_languages method to ensure the necessary properties
        and attributes are set for computing and setting the
        compatible_languages property so that the latter is available next
        time it is needed without having to compute it anew.

        """

        if is_none_or_empty(self._compatible_languages):
            self._set_compatible_languages()
            self.reset_samples_manager()

        return self._compatible_languages

    @property
    def non_query_cols(self) \
            -> List[str]:
        """
        Retrieves the list of non-query columns in the dataset.

        Retrieves the list of non-query columns the data suite offers.

        Returns
        -------
        List[str]
            List of column names of non-query column names.

        Notes
        -----
        - The non_query columns are the calumns that do not represent
          query or answer columns. They typically contain
          - the text samples for which to retrieve the sentiment class
          - the targets (= mentions) mentioned in the samples for which to
            retrieve the sentiments
          - the sentiment annotations (= polarities) for the text samples

        - This is a computed property without setter.

        """

        return self.suite.NON_QUERY_COLS

    @property
    def samples_manager(self) \
            -> SamplesManager:
        """
        Returns a SamplesManager instance needed to retrieve any samples
        from the suite.
        
        Ensures only one SamplesManager instance is created. 

        Returns
        -------
        SamplesManager
            The SamplesManager instance.

        Notes
        -----
        Computed property without setter.

        """

        if not self._samples_manager:
            self._samples_manager = SamplesManager(
                self.suite,
                self.compatible_languages,
                self.non_query_cols
            )

        return self._samples_manager

    # endregion --- Properties

    # region --- Abstract Properties

    @property
    @abstractmethod
    def languages(self) \
            -> List[str]:
        """
        Returns the list of languages the LLM understands.

        Abstract property that needs to be implemented by subclasses.

        """

    @languages.setter
    @abstractmethod
    def languages(self, languages: List[str]) \
            -> None:
        """
        Sets the list of languages the LLM understands.

        Abstract setter method that needs to be implemented by subclasses.

        Parameters
        ----------
        languages : List[str]
            The list of languages.

        """

    @property
    @abstractmethod
    def suite(self) \
            -> T:
        """
        Returns the suite from which to get the data samples.

        Returns
        -------
        DataSourceSuite
            The data suite providing the data samples.

        """

    @suite.setter
    @abstractmethod
    def suite(self, suite: T) \
            -> None:
        """
        Sets the data source suite from which to get the data samples.

        Abstract setter method that needs to be implemented by subclasses.

        Parameters
        ----------
        suite : DataSourceSuite
            The data source suite.

        """

    # endregion --- Abstract Properties

    # region --- Public Methods ---

    def reset_samples_manager(self) \
            -> None:
        """
        Resets the samples_manager property.
        
        Resets the samples_manager property so that the SamplesManager needs 
        to be re-initialized with the new attribute values. 
        
        This reset method is called if attributes are changed that affect 
        the SamplesManager's data or behavior.

        """

        self._samples_manager = None

    def predict_sentiments(self) \
            -> None:
        """
        Retrieves the sentiment predictions for all languages.

        This method retrieves the sentiment predictions for all languages in
        the data suite.

        Iterating through the languages, it calls the
        predict_sentiments_in language method to retrieve the
        predictions.

        Notes
        -----
        - ATTENTION: Before starting a new execution of this method,
          with another data_offset than before, ensure you have saved the
          checkpoints and the result files from the txt and csv data folders
          to another location! Otherwise, the existing checkpoints will
          prevent the successful execution of the sentiment prediction.

        - ATTENTION: Before attempting to run this method, ensure that
          prompt engineering was executed first.

        - If this method fails due to not existing validated queries,
          the BatchProcessor will have created a first checkpoint (e.g.
          "MadTscSuite_en_balanced_33_batch_checkpoint.txt") containing a
          "1" value in the data/txt folder. This does not have to be removed
          before restarting sentiment retrieval as the programm will restart
          from the beginning if the first checkpoint is set to 1. Just run
          prompt engineering and try to run this method again afterwards.

        """

        for language in self.compatible_languages:
            self.predict_sentiments_in_language(language)

        self.config.remove('language')

    def predict_sentiments_in_language(
            self,
            language: str = 'en'
    ) -> None:
        """
        Retrieves the sentiment predictions for the specified language.

        This method retrieves the sentiment predictions for the specified
        language in the data suite.

        Parameters
        ----------
        language : str
            Language code, e.g. 'en'. Defaults to English ('en').

        Notes
        -----
        - ATTENTION: Before attempting to run this method, ensure that
          prompt engineering was executed first.

        - If this method fails due to not existing validated queries,
          the BatchProcessor will have created a first checkpoint (e.g.
          "MadTscSuite_en_balanced_33_batch_checkpoint.txt") containing a
          "1" value in the data/txt folder. This does not have to be removed
          before restarting sentiment retrieval as the programm will restart
          from the beginning if the first checkpoint is set to 1. Just run
          prompt engineering and try to run this method again afterwards.

        - The samples for which the predictions are retrieved are provided
          by the SamplesManager, depending on the settings in the
          sentiment analysis configuration.

        - The method does not return anything. The prediction results are
          saved in a DataFrame by the QueryColumnProcessor during the
          sentiment retrieval with the various processors and serialized as a
          CSV file.

        """

        self.config.set('language', language)

        # Get language-specific samples from the samples_manager, letting the
        # manager decide whether balanced or unbalanced samples are needed and
        # which samples are taken from all available samples, depending on
        # batch size, data offset etc, which are set in the sentiment
        # analysis configuration (referenced in this class as self.config).

        samples = self.samples_manager.get_samples(language)

        processor = LanguageProcessor(language, samples)
        processor.process_language()

    # endregion --- Public Methods

    # region --- Protected Methods

    def _add_llm_instance_to_config(self) -> None:
        """Adds this LLM instance to the configuration."""
        self.config.set('llm', self)

    @requires_property("languages")
    @self_attribute_chain_not_none('suite.languages')
    def _set_compatible_languages(self) \
            -> None:
        """
        Sets the compatible_languages property.

        Sets the compatible_languages property, provided that the
        'languages' property is set and the 'suite.languages' attribute
        chain is correct.

        Notes
        -----
        The decorators ensure the needed properties and attributes exist for
        computing the compatible_languages property. If the 'languages'
        property is not set or the 'suite.languages' attribute chain is
        invalid, a ValueError is raised.

        """

        self._compatible_languages = get_common_elements(
            self.languages,
            self.suite.languages
        )

    # endregion --- Protected Methods

    # --- Abstract Protected Methods ---
    @abstractmethod
    def _add_api_to_config(self) -> None:
        """Adds LLM-specific API settings to the configuration."""
        pass
