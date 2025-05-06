"""
all_languages_evaluation.py
---------------------------
Version 1.0, updated on 2024-12-14

"""

from typing import Dict, List, Tuple

from pandas import DataFrame

from logger import Logger
from src.data_structures.data_frame_factory import DataFrameFactory
from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.chunk import Chunk
from src.sentiment_analysis.evaluation.metrics_visualization_mixin import (
    MetricsVisualizationMixin
)
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.utils.data_utils import is_none_or_empty
from src.utils.print_utils import print_in_box, restrict_length


class AllLanguagesEvaluation(MetricsVisualizationMixin, LoggingMixin):
    """
    AllLanguagesEvaluation class
    
    """

    def __init__(self):
        """
        Constructor.

        Initializes the AllLanguagesEvaluation class.

        """

        super().__init__()

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.config = SentimentAnalysisConfig()

        self.overall_metrics: MyDataFrame | None = None
        self.overall_sentiment_data: MyDataFrame | None = None

        # Dictionary for all prediction frequencies for all prompts in all
        # languages
        self.all_lang_pred_freq_dict: Dict[
            str,  # language
            Dict[
                str,  # prompt
                List[Tuple[str, int]]  # frequencies
            ]
        ] = {}

        # Dictionary for all metrics for all prompts in all languages
        self.all_lang_prompt_metrics: Dict[
            str,  # language
            Dict[
                str,  # prompt
                Dict[
                    str,  # metric
                    float
                ]
            ]
        ] = {}

        # DataFrame for all prompt rankings in all languages
        self.overall_ranking: DataFrame = DataFrameFactory.create(None)

        # DataFrame for prompt metrics aggregated across all languages (sums
        # over all processed languages)
        self.aggregated_metrics: DataFrame | None = None

        # DataFrame for aggregated and averaged prompt metrics across all
        # languages
        self.mean_metrics: DataFrame | None = None

        self.__freqs_by_prompt_dict: Dict[
            str, Dict[str, List[Tuple[str, int]]]
        ] = {}

    # region --- Properties

    # endregion --- Properties

    # region --- Public Methods

    def add_to_overall_metrics(self, metrics: MyDataFrame) \
            -> None:
        if is_none_or_empty(self.overall_metrics):
            self.overall_metrics = metrics.copy()
        else:
            self.overall_metrics.do_with_row(
                "add_rows",
                data=metrics,
                ignore_index=False
            )

    def add_to_overall_sentiment_data(self, data: Chunk) \
            -> None:
        data = data.copy()
        language = self.config.get('language')

        cols_map: Dict[str, str] = {
            'sentence_normalized': f"{language}_sentence",
            'mention': f"{language}_mention",
            'polarity': f"{language}_polarity", 'query_1': f"{language}_query",
            'answer_1': f"{language}_answer"
        }

        data.rename_cols(cols_map)

        if is_none_or_empty(self.overall_sentiment_data):
            self.overall_sentiment_data = (
                MyDataFrameFactory.create(data.df.copy())
            )
        else:
            self.overall_sentiment_data.do_with_column(
                "merge",
                other=data
            )

    def show_overall_rankings(self) \
            -> None:
        if is_none_or_empty(self.overall_ranking):
            raise CriticalException(
                self.logger,
                "The overall ranking is not yet computed. Run the "
                "evaluation before you retry this method."
            )

        df = self.overall_ranking

        print(df.T.describe().T)
        title = ('Average Ranks of the Different Prompts Across All '
                 'Languages')
        y_label = 'Rank'
        x_label = 'Prompt'
        invert_y_axis = True

        self.diagram.box_plot(
            df.T,
            title,
            y_label,
            x_label,
            invert_y_axis
        )

        print_in_box(
            title,
            df
        )

        self.diagram.line_plot(
            df,
            title,
            y_label,
            x_label,
            None,
            invert_y_axis)

    def show_mean_metrics(self) \
            -> None:
        pass

    def _compute_mean_metrics(self) \
            -> None:
        """
        Computes the mean metrics DataFrame.

        Computes the mean metrics from the aggregated metrics and stores the
        resulting DataFrame in the mean_metrics property of this class.

        """

        self.mean_metrics = self.get_mean_data_frame(
            self.aggregated_metrics, len(self.languages)
        )

    def get_mean_data_frame(self, df: DataFrame, divisor) \
            -> DataFrame:
        """
        Computes the means of all values in the DataFrame.

        Uses the provided divisor to calculate the means.

        Returns
        -------
        DataFrame
            The mean data.

        """

        return df.div(divisor)

    def show_freqs_comparisons_by_prompt(self):
        self._compute_freqs_by_prompt()
        freqs_by_prompt_list = []

        for _, value in self.__freqs_by_prompt_dict.items():
            freqs_by_prompt_list.append(DataFrameFactory.create(value))
            # self.show_freqs_comparison_by_prompt(value)

        self.diagram.all_multiple_frequencies_by_prompt_diagrams(
            freqs_by_prompt_list,
            'Frequencies by Prompt'
        )

    def show_freqs_comparison_by_prompt(
            self,
            freqs_by_language: Dict[str, List[Tuple[str, int]]]
    ) -> None:
        df = DataFrameFactory.create(freqs_by_language)
        self.diagram.multiple_frequencies_by_prompt_diagram(df)

    def _show_pairwise_freqs_comparisons(self) \
            -> None:
        for lang in self.languages:
            self._show_pairwise_freqs_comparison(lang)

    def _show_pairwise_freqs_comparison(self, language: str) \
            -> None:
        self.diagram.all_pairwise_frequency_comparison_diagrams(
            self._freqs_df(language),
            true_col='correct',
            n_rows=15,
            title=f'{restrict_length(language, 20)}'
        )

    def lang_pred_freq_dict(self, language: str) \
            -> Dict[str, List[Tuple[str, int]]]:

        return self.all_lang_pred_freq_dict.get(language)

    def _freqs_df(self, language: str) \
            -> DataFrame:
        return DataFrameFactory.create(self.lang_pred_freq_dict(language))

    def _compute_freqs_by_prompt(self):
        for i in range(1, len(self._prompts) + 1):
            freqs_dict: Dict[str, List[Tuple[str, int]]] = {}

            col_name = 'correct'
            freqs_dict[col_name] = self.lang_pred_freq_dict('en').get(col_name)

            for lang in self.languages:
                col_name = f"{lang}_{str(i)}"
                freqs_dict[col_name] = self.lang_pred_freq_dict(lang).get(
                    col_name)

            self.__freqs_by_prompt_dict[str(i)] = freqs_dict

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
