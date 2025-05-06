"""
plotter.py
----------
Version 1.0, updated on 2025-05-01

"""

from src.stats.visualization.plotting_strategy import PlottingStrategy


class Plotter:
    """
    This class serves as the context in a strategy pattern, which allows you to
    dynamically choose a plotting strategy at runtime.

    The class works with any of the plotting strategies that implement the
    PlottingStrategy interface. It gives access to the plot method of the
    given plotting strategy.

    Attributes
    ----------
    strategy : PlottingStrategy
        The current plotting strategy in use.

    Methods
    -------
    plot() -> None:
        Plots the data using the plotting strategy currently in use.

    """

    def __init__(self, strategy: PlottingStrategy):
        self._strategy = strategy

    @property
    def strategy(self) -> PlottingStrategy:
        """
        Gets the current plotting strategy.

        Returns
        -------
        PlottingStrategy
            The plotting strategy currently in use.

        """

        return self._strategy

    @strategy.setter
    def strategy(self, strategy: PlottingStrategy) \
            -> None:
        """
        Sets the serialization strategy to be used.

        The strategy can be changed at runtime.

        Parameters
        ----------
        strategy : PlottingStrategy
            The plotting strategy to be used for plotting operations.

        """

        self._strategy = strategy

    def plot(self) \
            -> None:
        """
        Plots the data using the plotting strategy currently in use.

        """
        self.strategy.plot()
