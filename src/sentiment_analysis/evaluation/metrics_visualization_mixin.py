"""
metrics_visualization_mixin.py
------------------------------
Version 1.0, updated on 2025-01-02

"""

from copy import deepcopy
from typing import List, no_type_check

from pandas import Series, DataFrame

from src.decorators.ensure_implements_decorator import ensure_implements
from src.loggable import Loggable
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.stats.visualization.command_line_strategy import CommandLineStrategy
from src.stats.visualization.diagram import Diagram
from src.stats.visualization.plotter import Plotter
from src.utils.data_utils import is_none_or_empty
from src.utils.print_utils import print_in_box
from type_aliases import ThresholdsType


class MetricsVisualizationMixin(LoggingMixin):
    def __init__(self):
        self.config = SentimentAnalysisConfig()

    # region --- Properties

    @property
    def diagram(self) \
            -> Diagram:
        """
        Gets an instance of the Diagram class.
        """

        if not getattr(self, '_diagram', None):
            self._set_diagram()

        return getattr(self, '_diagram', [])

    @diagram.setter
    def diagram(self, diagram: Diagram) \
            -> None:
        setattr(self, '_diagram', diagram)

    @property
    def submetrics(self) \
            -> List[str]:
        """
        Gets the list of available submetrics.
        """

        if not getattr(self, '_submetrics', None):
            self._set_submetrics()

        return getattr(self, '_submetrics', [])

    @submetrics.setter
    def submetrics(self, submetrics: List[str]) \
            -> None:
        """
        Sets the list of available submetrics.
        """

        setattr(self, '_submetrics', submetrics)

    @property
    def thresholds(self) \
            -> ThresholdsType:
        """
        Gets the thresholds for the different metrics.
        """

        if is_none_or_empty(getattr(self, '_thresholds', None)):
            self._set_thresholds()

        return getattr(self, '_thresholds', {})

    @thresholds.setter
    def thresholds(self, thresholds: ThresholdsType) \
            -> None:
        """
        Sets the thresholds for the different metrics.
        """

        setattr(self, '_thresholds', thresholds)

    # endregion --- Properties

    # region --- Public Methods

    @no_type_check
    @ensure_implements(Loggable)
    def show_partial_metric(
            self,
            metric: str = 'macro',
            show_best: bool = False,
            show_worst: bool = False
    ) -> None:
        """
        Shows a diagram for the specified group of metrics.

        The possible groups are defined by the submetrics property of this
        class.

        Parameters
        ----------
        metric : str
            The group of metrics to show corresponding to one of the
            submetrics defined in the list returned by the submetrics
            property of this class.

        show_best : bool
            Whether to show the best queries. Defaults to False.

        show_worst : bool
            Whether to show the worst queries. Defaults to False.


        Raises
        ------
        CriticalException
            If the given metric is not contained in the submetrics list.

        """

        if metric not in self.submetrics:
            raise CriticalException(
                self.logger,
                "Unknown submetric %s" % metric
            )

        df = self.get_partial_metrics(metric).df

        if show_best:
            df = df[:self.n_prompts]
            best_or_worst = "- Best Prompts"
        elif show_worst:
            df = df[-self.n_prompts:]
            best_or_worst = "- Worst Prompts"
        else:
            # Use df as it is
            best_or_worst = ""

        language = df.index[0][:2].upper()
        version = self.config.get('version')

        if not hasattr(self, "sub_dir") or self.sub_dir is None:
            samples = ' (v_%s)' % version
        else:
            samples = '(Samples %s (v_%s))' % (self.sub_dir, version)

        title = (
            f"{language}: "
            f"{metric.capitalize()} Metrics for Different Prompts "
            f"{best_or_worst}"
            f"{samples}"
        )

        print_in_box(
            title,
            df
        )
        y_label = 'Value'
        x_label = 'Metric'

        thresholds = self.thresholds

        if metric in thresholds:
            self.diagram.line_plot(
                df.T,
                title,
                y_label,
                x_label,
                thresholds[metric]
            )

            x_label = 'Prompt'

            self.diagram.line_plot(
                df,
                title,
                y_label,
                x_label,
                thresholds[metric]
            )

        else:
            self.diagram.line_plot(df.T, title, y_label, x_label)

            x_label = 'Prompt'
            self.diagram.line_plot(df, title, y_label, x_label)

    def show_best(self) \
            -> None:
        """
        Displays a DataFrame containing the best queries.

        Prints the DataFrame in a formatted box in the console.

        """

        df = self.get_best()
        title = "Best %d queries" % self.n_prompts
        print_in_box(title, df)

    def get_best(self) \
            -> DataFrame:
        return self.best.do_with_column(
            'extract_columns', col_names=['rank', 'query']
        )

    def show_worst(self) \
            -> None:
        """
        Displays a DataFrame containing the worst queries.

        Prints the DataFrame in a formatted box in the console.

        """

        df = self.worst.do_with_column(
            'extract_columns', col_names=['rank', 'query']
        )
        title = "Worst %d queries" % self.n_prompts
        print_in_box(title, df)

    def show_correlation_heatmap(self, correlation_data: Series | DataFrame) \
            -> None:
        """
        Displays a correlation heatmap using the provided correlation data.

        This method generates a heatmap based on the input data to visually
        represent correlation values between variables. It supports both
        pandas Series and pandas DataFrame objects. If a Series is provided,
        it uses a single dimension to plot the heatmap. If a DataFrame is
        given, it processes the data to construct a multi-dimensional heatmap.

        Parameters
        ----------
        correlation_data : Series or DataFrame
            The data containing correlation values. Accepts either a pandas
            Series, which represents one-dimensional data, or a pandas
            DataFrame for multi-dimensional correlation values.

        Notes
        -----
        This method does not return any values. The methods it calls directly
        display the generated heatmap.

        """

        # Prevent that correlation_data is modified globally:
        corr_data = deepcopy(correlation_data)

        if isinstance(corr_data, Series):
            self.diagram.heatmap(corr_data)
        else:
            self.diagram.heatmap_from_df(corr_data)

    # endregion --- Public Methods

    # region --- Protected Methods

    def _set_thresholds(self) \
            -> None:
        # Thresholds for the different metrics to show in the diagrams:
        standard_thresholds = {
            'Poor': 0,
            'Fair': 0.5,
            'Good': 0.6,
            'Very good': 0.7,
            'Excellent': 0.8
        }
        # Slightly higher thresholds for the accuracy compared to the other
        # metrics because class imbalance might lead to a misleadingly high
        # accuracy if only the most frequent class is mostly classified
        # correctly.
        self.thresholds = {
            'acc':
                {
                    'Poor': 0,
                    'Fair': 0.6,
                    'Good': 0.7,
                    'Very good': 0.8,
                    'Excellent': 0.9
                },
            'macro':
                standard_thresholds,
            'f1':
                standard_thresholds,
            'precision':
                standard_thresholds,
            'recall':
                standard_thresholds,
            'positive':
                standard_thresholds,
            'negative':
                standard_thresholds,
            'neutral':
                standard_thresholds,
        }

    def _set_submetrics(self) \
            -> None:

        # Metrics groups to visualize:
        self.submetrics = [
            'macro',
            'f1',
            'precision',
            'recall',
            'positive',
            'negative',
            'neutral',
        ]

    def _set_diagram(self) \
            -> None:

        self.diagram = Diagram(Plotter(CommandLineStrategy()))

    # endregion --- Protected Methods
