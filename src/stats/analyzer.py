"""
analyzer.py
------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

from matplotlib import pyplot as plt

from src.data_structures.item_list import ItemList
from src.stats.statistics_strategy import StatisticsStrategy


class Analyzer:
    """
    This class serves as the context in a strategy pattern, which allows you to
    dynamically choose a statistics strategy at runtime.

    The class works with any of the statistics strategies that implement the
    StatisticsStrategy interface.

    Attributes
    ----------
    strategy : StatisticsStrategy
        The current statistics strategy in use.

    """

    def __init__(self, my_strategy: StatisticsStrategy | None = None) \
            -> None:
        """
        Constructor.

        Sets the statistics strategy which is supposed to be used for
        statistical analyses.

        Parameters
        ----------
        my_strategy : StatisticsStrategy | None
            The statistics strategy to be used. Default value: None.

        """

        self.strategy = my_strategy

    @property
    def strategy(self) -> StatisticsStrategy:
        """
        Gets the current serialization strategy.

        Returns
        -------
        SerializationStrategy
            The statistics strategy currently in use.

        """

        return self._strategy

    @strategy.setter
    def strategy(self, strategy: StatisticsStrategy) \
            -> None:
        """
        Sets the statistics strategy to be used.

        The strategy can be changed at runtime.

        Parameters
        ----------
        strategy : StatisticsStrategy
            The statistics strategy to be used for statistical analyses.

        """

        self._strategy = strategy

    # endregion --- Properties

    # region --- Methods

    def analyze(self, items: ItemList):
        """
        Analyzes the given items.

        Parameters
        ----------
        items : ItemList
            ItemList object containing the list of items to be analyzed.

        """

        self.strategy.analyze(items)

    def visualize(self, ax: plt.Axes | None = None):
        self.strategy.visualize(ax)

    # endregion --- Methods
