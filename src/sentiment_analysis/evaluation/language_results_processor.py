"""
language_results_processor.py
-----------------------------
Version 1.0, updated on 2025-01-01

"""

from typing import Dict, List

from logger import Logger
from src.data_structures.my_data_frame import MyDataFrame
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.chunk import Chunk
from src.sentiment_analysis.chunk_loader import ChunkLoader
from src.sentiment_analysis.evaluation.deep_prompt_evaluation import (
    DeepPromptEvaluation
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.utils.data_utils import is_none_or_empty


class LanguageResultsProcessor(LoggingMixin):
    """
    LanguageResultsProcessor class.

    This class processes managing and processing sentiment analysis results
    for a given language. It evaluates metrics, analyzes prompts, and
    facilitates comparison of results. 
    
    Attributes
    ----------
    language : str
        The language being processed (e.g., "en" for English).

    
    config : SentimentAnalysisConfig
        Configuration settings for sentiment analysis and associated tasks
        (prompt engineering, evaluation of predictions, etc.)

    metrics : MyDataFrame
        The metrics for the current language.

    data : Chunk
        The data with the batch samples and query and answer columns.

    evaluation : DeepPromptEvaluation
        A DeepPromptEvaluation instance, providing detailed prompt evaluation.
    
    
    Methods
    -------
    analyze_prompts(partial_metrics: List[str] | None = None) -> None:
        Analyzes the prompts.

    get_best_query_nrs() -> List[str]:
        Retrieves the indices of the best-performing queries.

    process_language() -> None:
        Processes the language results.

    show_best_prompts(partial_metrics: List[str] | None = None) -> None:
        Displays the best-performing prompts based on the evaluation metrics.

    show_partial_metrics(partial_metrics: List[str], show_best: bool = False,
            show_worst: bool = False) -> None:
        Displays specified metrics for the best and/or worst prompts.

    show_worst_prompts(partial_metrics: List[str] | None = None) -> None:
        Displays the worst-performing prompts based on the evaluation metrics.

    verify_metrics_are_equal(metric_1: str, metric_2: str) -> bool:
        Compares two metrics and verifies if they are equal.

    """

    def __init__(
            self,
            language: str
    ) -> None:
        """
        Constructor.
        
        Initializes the LanguageResultsProcessor class with the provided 
        language.
        
        Parameters
        ----------
        language : str
            The language to process.

        """

        self._evaluation = None
        self._metrics = None
        self._data = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.config = SentimentAnalysisConfig()

        self.language: str = language

    # region --- Properties

    @property
    def metrics(self) \
            -> MyDataFrame:
        """
        Returns the metrics for the current language.

        Returns
        -------
        MyDataFrame
            A MyDataFrame instance containing the sorted metrics DataFrame.

        Notes
        -----
        The metrics DataFrame is sorted in ascending order (from best to
        worst rank) by the ranks of the prompts.

        """

        return self._metrics

    @metrics.setter
    def metrics(self, metrics: MyDataFrame) \
            -> None:
        """
        Sets the metrics for the current language.

        Parameters
        ----------
        metrics : MyDataFrame
            A MydataFrame instance containing a DataFrame with
            language-specific metrics.

        """

        self._metrics = metrics

    @property
    def data(self) \
            -> Chunk:
        """
        Retrieves the data with the batch samples and query and answer columns.

        Returns
        -------
        Chunk
            A chunk object containing the data.

        """

        if is_none_or_empty(self._data):
            self.data = self.evaluation.data
        return self._data

    @data.setter
    def data(self, data: Chunk) \
            -> None:
        """
        Sets the data with the batch samples and query and answer columns.

        Parameters
        ----------
        data : Chunk
            A chunk object containing the he data including the batch samples
            and query and answer columns.

        """

        self._data = data

    @property
    def answer_cols(self) \
            -> List[str]:

        self.data

    @property
    def evaluation(self) \
            -> DeepPromptEvaluation:
        """
        Provides access to the evaluation instance.

        Returns
        -------
        DeepPromptEvaluation
            The evaluation instance for analyzing metrics and prompts.

        """

        return self._evaluation

    @evaluation.setter
    def evaluation(self, evaluation: DeepPromptEvaluation) \
            -> None:
        """
        Sets the evaluation instance.

        Parameters
        ----------
        evaluation : DeepPromptEvaluation
            The evaluation instance to set.

        """

        self._evaluation = evaluation

    # endregion --- Properties

    # region --- Public Methods

    def process_language(self) \
            -> None:
        """
        Processes the language results.

        Processes the language results by loading data chunks, creating an
        evaluation instance, and computing sorted metrics.

        """

        data = self._get_data_from_chunks()

        self.evaluation = DeepPromptEvaluation(
            data,
            self.language
        )

        self.metrics = self.evaluation.metrics.sorted('rank')
        print(self.metrics)

    def show_best_prompts(
            self,
            partial_metrics: List[str] | None = None
    ) -> None:
        """
        Displays the best-performing prompts based on the evaluation metrics.

        Parameters
        ----------
        partial_metrics : List[str] | None
            A list of specific metrics to display for the best prompts. If
            None, only overall metrics are shown.

        """

        self.evaluation.show_best()
        if not is_none_or_empty(partial_metrics):
            self.show_partial_metrics(partial_metrics, show_best=True)

    def show_worst_prompts(
            self,
            partial_metrics: List[str] | None = None
    ) -> None:
        """
        Displays the worst-performing prompts based on the evaluation metrics.

        Parameters
        ----------
        partial_metrics : List[str] | None
            A list of specific metrics to display for the worst prompts. If
            None, only overall metrics are shown.

        """

        self.evaluation.show_worst()
        if not is_none_or_empty(partial_metrics):
            self.show_partial_metrics(partial_metrics, show_worst=True)

    def show_partial_metrics(
            self,
            partial_metrics: List[str],
            show_best: bool = False,
            show_worst: bool = False
    ) -> None:
        """
        Displays specified metrics for the best and/or worst prompts.

        Parameters
        ----------
        partial_metrics : List[str]
            A list of metrics to display.

        show_best : bool
            Whether to show the metrics for the best prompts.

        show_worst : bool
            Whether to show the metrics for the worst prompts.

        """

        for metric in partial_metrics:
            self.evaluation.show_partial_metric(metric, show_best, show_worst)

    def verify_metrics_are_equal(self, metric_1: str, metric_2: str) \
            -> bool:
        """
        Compares two metrics and verifies if they are equal.

        This method can be used to check two metrics that are supposed to be
        identical.

        Parameters
        ----------
        metric_1 : str
            Name of the first metric. Should equal the column name of the
            respective metric values in the metrics DataFrame.

        metric_2 : str
            Name of the second metric to compare. Should equal the column
            name of the respective metric values in the metrics DataFrame.

        Returns
        -------
        bool
            True if the values of the metrics are equal, False otherwise.

        """

        if not self.evaluation.metrics_are_equal(metric_1, metric_2):
            msg = "%s and %s are not the same in %s" % (
                metric_1.capitalize(),
                metric_2,
                self.language.upper()
            )
            self._log(msg, 'info')

            return False

        print("%s and %s are the same for all prompts in %s!" %
              (
                  metric_1.capitalize(),
                  metric_2,
                  self.language.upper()
              ))

        return True

    def get_best_query_nrs(self) \
            -> List[str]:
        """
        Retrieves the indices of the best-performing queries.

        Returns
        -------
        List[str]
            A list of indices corresponding to the best queries.

        """

        return self.evaluation.get_best().index.values.tolist()

    def analyze_prompts(self, partial_metrics: List[str] | None = None) \
            -> None:
        """
        Analyzes the prompts.

        Finds best and worst prompts and correlations of prompt ingredients
        with valid/invalid prompts if there are enough different prompts to
        perform such an analysis.

        Parameters
        ----------
        partial_metrics : List[str]
            List of partial metrics to show for the best and worst prompts.
            Defaults to None. If no partial metrics are provided,
            the show_best_prompts and show_worst_prompts methods will just
            show the best and worst prompt overall metrics values but will not
            display any partial metrics diagrams.

        """

        if self.config.get('target_n_prompts') > 1:

            self.evaluation.analyze_correlation()

            # If the total number of prompts is larger than the number of
            # best or worst prompts to show, perform a correlation analysis
            # for the prompt ingredients and show best and worst prompts:
            if self.config.get('target_n_prompts') > self.config.get(
                    'n_best_prompts'
            ):
                self.show_best_prompts(partial_metrics)
                self.show_worst_prompts(partial_metrics)

        elif self.config.get('target_n_prompts') == 1:
            msg = ("Only one prompt to analyze: Correlation analysis and "
                   "analysis of best vs. worst prompts are not possible.")
            self._log(msg, "info")

        else:
            # Total number of prompts is 0 or non-existent:
            msg = "No prompts to analyze: Something must have gone wrong."
            self._log(msg, "error")

    # endregion --- Public Methods

    # region --- Protected Methods

    def _get_data_from_chunks(self) \
            -> Chunk:
        """
        Uses the ChunKLoader to retrieve a valid queries chunk.

        Returns
        -------
        Chunk
            A chunk object with valid queries.

        """

        chunk_loader = ChunkLoader(self.language)
        return chunk_loader.valid_queries_chunk

    # endregion --- Protected Methods
