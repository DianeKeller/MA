"""
samples_manager.py
-------------------
Version 1.0, updated on 2024-12-14

"""

from typing import TypeVar, List, Dict

from src.data_structures.my_data_frame import MyDataFrame
from src.decorators.data_check_decorators import requires_property
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.samples.balanced_samples_provider import (
    BalancedSamplesProvider
)
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.sentiment_analysis.samples.unbalanced_samples_provider import (
    UnbalancedSamplesProvider
)
from src.utils.data_utils import is_none_or_empty

T = TypeVar('T', bound='DataSourceSuite')
S = TypeVar('S', bound='DataSourceStrategy')


class SamplesManager(LoggingMixin):
    """
    SamplesManager class.



    """

    def __init__(
            self,
            suite: T,
            languages: List[str] = None,
            cols: List[str] = None
    ):
        """
        Constructor.

        Initializes the SamplesManager class with the specified parameters.

        Parameters
        ----------
        suite : DataSourceSuite
            Data source suite that provides the samples.

        languages : List[str]
            List of languages for which the samples are to be retrieved.

        Notes
        -----
        The languages specified when the class is initialized do not
        necessarily correspond to all the languages in the data source suite
        from which the samples are to be retrieved. Instead, they can be a
        subset of the suite's languages, depending on the languages the LLM
        supports.

        """

        # Protected variables to store the property values of this class
        self._suite: T = suite
        self._languages: List[str] = languages if languages else []
        self._cols: List[str] = cols if cols else []

        self._balanced_samples: Dict[str, MyDataFrame] = {}
        self._unbalanced_samples: Dict[str, MyDataFrame] = {}

        # The sentiment analysis configuration contains all the information
        # for the SamplesManager which samples it should collect.
        self.config = SentimentAnalysisConfig()

        # Get needed settings from the sentiment analysis configuration
        self.data_offset: int = self.config.get('data_offset')
        self.balance: int = self.config.get('balance')
        self.balanced: bool = self.config.get('balanced')

        self.bal_provider = BalancedSamplesProvider(self)
        self.unbal_provider = UnbalancedSamplesProvider(self)

    # region --- Properties

    @property
    def languages(self) \
            -> List[str]:
        """
        Retrieves the languages of the data to manage.

        Returns
        -------
        List[str]
            A list of language codes.

        """

        if is_none_or_empty(self._languages):
            self._set_default_languages()

        return self._languages

    @languages.setter
    def languages(self, languages: List[str]) \
            -> None:
        """
        Sets the languages of the data to manage.

        Parameters
        ----------
        languages: List[str]
            A list of language codes

        """

        self._languages = languages

    @property
    def suite(self) \
            -> T:
        """
        Returns the suite from which to retrieve the samples.

        Returns
        ----------
        DataSourceSuite
            The suite from which to retrieve the samples.

        Raises
        ------
        CriticalException
            If the suite is not set.

        """

        if not self._suite:
            raise CriticalException(
                self.logger,
                "The data source suite is missing. Cannot proceed."
            )

        return self._suite

    @suite.setter
    def suite(self, suite: T) \
            -> None:
        """
        Sets the suite from which to retrieve the samples.

        Parameters
        ----------
        suite : DataSourceSuite
            The suite from which to retrieve the samples.

        """

        self._suite = suite

    @property
    def suite_name(self) \
            -> str:
        """
        Retrieves the suite's name from the suite's class name.

        Returns
        -------
        str
            The suite's name.

        Notes
        -----
        Computed property without setter.

        """

        return self.suite.__class__.__name__

    @property
    def cols(self) \
            -> List[str]:
        """
        Returns the non-query column names in the dataset.

        """

        if not self._cols:
            raise CriticalException(
                self.logger,
                "The column names are missing. Cannot proceed."
            )

        return self._cols

    @cols.setter
    def cols(self, cols: List[str]) \
            -> None:
        """
        Sets the non-query column names for the dataset.

        """

        self._cols = cols

    @property
    def provenience(self) \
            -> str:
        """
        Retrieves the LLM's name.

        Returns
        -------
        str
            The LLM's name.

        Notes
        -----
        Computed property without setter.

        """

        return self.config.get('llm').__class__.__name__

    @property
    def balanced_samples(self) \
            -> Dict[str, MyDataFrame]:
        """
        Returns the balanced samples for all languages.

        Returns the balanced samples for all languages that the LLM and the
        data suite have in comman.

        Returns
        -------
        Dict[str, MyDataFrame]:
            The balanced samples, where the key is the language and the
            value is the balanced samples for the language.

        """

        if is_none_or_empty(self._balanced_samples):
            self._set_balanced_samples()

        return self._balanced_samples

    @balanced_samples.setter
    def balanced_samples(self, samples: Dict[str, MyDataFrame]) \
            -> None:
        """
        Sets the balanced samples for all languages.

        Sets the balanced samples for all languages that the LLM and the
        data suite have in comman..

        Parameters
        ----------
        samples : Dict[str, MyDataFrame]
            The balanced samples to set the property with, where the key is the
            language and the value is the balanced samples for the respective
            language.

        """

        self._balanced_samples = samples

    @property
    def unbalanced_samples(self) \
            -> Dict[str, MyDataFrame]:
        """
        Returns the unbalanced samples for all languages.

        Returns the unbalanced samples for all languages that the LLM and the
        data suite have in comman.

        Returns
        -------
        Dict[str, MyDataFrame]:
            The unbalanced samples, where the key is the language and the
            value is the unbalanced samples for the language.

        """

        if is_none_or_empty(self._unbalanced_samples):
            self._set_unbalanced_samples()

        return self._unbalanced_samples

    @unbalanced_samples.setter
    def unbalanced_samples(self, samples: Dict[str, MyDataFrame]) \
            -> None:
        """
        Sets the unbalanced samples for all languages.

        Sets the unbalanced samples for all languages that the LLM and the
        data suite have in comman..

        Parameters
        ----------
        samples : Dict[str, MyDataFrame]
            The unbalanced samples to set the property with, where the key is
            the language and the value is the unbalanced samples for the
            respective language.

        """

        self._unbalanced_samples = samples

    # endregion --- Properties

    # region --- Public Methods

    def get_samples(self, language: str) \
            -> MyDataFrame:
        """
        Retrieves the samples for the specified language.

        Retrieves the samples for the specified language, depending on the
        settings in the sentiment analysis configuration.

        Parameters
        ----------
        language : str
            The language for which to retrieve the required samples.

        Returns
        -------
        MyDataFrame
            The samples for the specified language, selected according to
            the settings in the sentiment analysis configuration.

        """

        if self.balanced:
            return self.balanced_samples[language]
        else:
            return self.unbalanced_samples[language]

    @requires_property('suite')
    def get_suite_languages(self) \
            -> List[str]:
        """
        Retrieves the languages of the data source suite.

        Returns
        -------
        List[str]
            A list of language codes containing the languages of the suite.

        """

        return self.suite.languages

    # endregion --- Public Methods

    # region --- Protected Methods
    def _set_default_languages(self) \
            -> None:
        """
        Sets the languages of the samples to the languages of the suite.

        This method provides a fallback in case the list of languages
        provided at initialization of the SamplesManager is empty.

        """

        self.languages = self.get_suite_languages()

    def _set_balanced_samples(self) \
            -> None:
        """
        Sets the balanced_samples property.

        Sets the balanced_samples property with the balanced samples of
        all languages.

        """

        self.balanced_samples = self.bal_provider.get_samples()

    @requires_property('languages')
    def _set_unbalanced_samples(self) \
            -> None:
        """
        Sets the unbalanced_samples property.

        Sets the unbalanced_samples property with the complete unbalanced
        samples of all languages, but removing unwanted rows and columns
        from the original data subset according to the data offset given in
        the sentiment analysis configuration.

        """

        self.unbalanced_samples = self.unbal_provider.get_samples()

    # endregion --- Protected Methods
