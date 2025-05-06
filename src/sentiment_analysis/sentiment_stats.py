"""
sentiment_stats.py
------------------
Version 1.0, updated on 2025-05-01

"""

from collections import Counter
from math import ceil

from pandas import DataFrame

from src.data_structures.item_series import ItemSeries
from src.stats.visualization.command_line_strategy import CommandLineStrategy
from src.stats.visualization.diagram import Diagram
from src.stats.visualization.plotter import Plotter
from src.utils.print_utils import print_in_box


def normalize_polarities(data: DataFrame) \
        -> DataFrame:
    """
    Replaces the numerical values of the original MAD_TSC polarity values.

    Replaces the numerical values of the original MAD_TSC polarity values
    in the 'polarity' column by the values used by the sentiment
    prediction.

    Parameters
    ----------
    data : DataFrame
        The DataFrame object in which the DataFrame is mapped.

    Returns
    -------
    DataFrame
        The DataFrame with the normalized 'polarity' column.

    """

    sentiment_map = {
        6.0: 'positive',
        4.0: 'neutral',
        2.0: 'negative'
    }
    data['polarity'] = data['polarity'].replace(sentiment_map)

    # Assign pandas string data type
    data['polarity'] = data['polarity'].astype(object)

    return data


class SentimentStats:
    """
    SentimentStats class.

    """

    def __init__(self, df: DataFrame):
        self._n_batches = 0
        self._df = None
        self.df = normalize_polarities(df)
        self.diagram: Diagram = Diagram(Plotter(CommandLineStrategy()))
        self._all_sentiment_distributions = DataFrame()

    @property
    def df(self) \
            -> DataFrame:
        return self._df

    @df.setter
    def df(self, df: DataFrame) \
            -> None:
        self._df = df

    @property
    def n_batches(self) \
            -> int:
        return self._n_batches

    @n_batches.setter
    def n_batches(self, n_batches: int) \
            -> None:
        self._n_batches = n_batches

    def compute_sentiment_distribution(self, df) \
            -> Counter:
        polarities = ItemSeries(df['polarity'], '')
        return polarities.frequencies

    def sentiment_distributions_for_all_batches(
            self,
            batch_size: int
    ) -> DataFrame:
        self.n_batches = ceil(len(self.df) / batch_size)

        for batch_nr in range(1, self.n_batches):
            batch_df = self.df.iloc[(batch_nr - 1) * 100: batch_nr * 100]
            self._all_sentiment_distributions[str(batch_nr)] = (
                self.compute_sentiment_distribution(batch_df)
            )

        return self._all_sentiment_distributions.T

    def show_sentiment_distributions(self) \
            -> None:
        distributions = self._all_sentiment_distributions.T
        title = f'Sentiment distributions in {self.n_batches} batches'

        print_in_box(
            title,
            distributions.describe()
        )

        y_label = "Percentage"
        x_label = "Polarity"
        self.diagram.box_plot(distributions, title, y_label, x_label)
