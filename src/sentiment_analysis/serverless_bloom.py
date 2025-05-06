"""
serverless_bloom.py
-------------------
Version 1.0, updated on 2024-12-14

"""

from typing import List

from src.data_sources.mad_tsc_workflow import MadTscWorkflow
from src.sentiment_analysis.bloom_fact_sheet_mixin import BloomFactSheetMixin
from src.sentiment_analysis.llm import Llm, T
from src.sentiment_analysis.serverless_bloom_prompt_validation_mixin import (
    ServerlessBloomPromptValidationMixin
)
from src.utils.data_utils import is_none_or_empty


class ServerlessBloom(
    Llm,
    BloomFactSheetMixin,
    ServerlessBloomPromptValidationMixin
):
    """
    ServerlessBloom class.

    This class implements the Llm class with properties and methods specific
    to the serverless use of BLOOM.

    Attributes
    ----------
    languages: List[str]
        The list of languages the LLM supports.

    suite: DataSourceSuite
        The data source suite from which to get the data samples.

    """

    def __init__(self):
        """
        Constructor.

        Initializes the class.

        """

        super().__init__()

        self._languages = None
        self._suite = None

    # region --- Properties

    @property
    def languages(self) \
            -> List[str]:
        """
        Returns the list of languages the LLM supports.

        If the languages have not been initialized, it retrieves them from
        the AVAILABLE_LANGUAGES attribute set in the BloomFactSheetMixin.

        Returns
        -------
        List[str]
            A list of language codes, corresponding to the supported languages.

        """

        if is_none_or_empty(self._languages):
            # Languages the LLM supports
            self.languages = self.AVAILABLE_LANGUAGES

        return self._languages

    @languages.setter
    def languages(self, languages: List[str]) \
            -> None:
        """
        Sets the list of languages the LLM supports.

        Parameters
        ----------
        languages : List[str]
            A list of language codes representing the supported languages.

        """

        self._languages = languages

    @property
    def suite(self) \
            -> T:
        """
        Returns the data source suite from which to get the data samples.

        Returns
        -------
        DataSourceSuite
            The initialized data suite providing the data samples.

        """

        if not self._suite:
            self._set_suite()

        return self._suite

    @suite.setter
    def suite(self, suite: T) \
            -> None:
        """
        Sets the data source suite from which to get the data samples.

        Resets the samples_manager property because the suite is used in the
        initialisation of the SamplesManager class.

        Parameters
        ----------
        suite : DataSourceSuite
            The initialized data source suite.

        """

        self._suite = suite
        self.reset_samples_manager()

    # endregion --- Properties

    # region --- Public Methods

    # endregion --- Public Methods

    # region --- Protected Methods

    def _set_suite(self) \
            -> None:
        """
        Loads the data suite and makes it available via the suite property.

        Initializes the suite and loads its subsets using the MadTscWorkflow.

        Notes
        -----
        This method must be changed if the user wants to use another
        suite with BLOOM.

        """

        mad_wf = MadTscWorkflow()
        mad_wf.load_subsets()
        self.suite = mad_wf.suite

    def _add_api_to_config(self) \
            -> None:
        """
        Adds the the LLM-specific API to the configuration settings.

        Adds the LLM-specific API to the _config variable, which is passed
        to the different sentiment retrieval processors, so that it is
        accessible from the query processor that needs it for sending the
        queries.

        """

        self.config.set('api', self.API)

    # endregion --- Protected Methods
