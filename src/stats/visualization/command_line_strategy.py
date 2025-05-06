"""
command_line_strategy.py
"""

from matplotlib import pyplot as plt

from src.stats.visualization.plotting_strategy import PlottingStrategy


class CommandLineStrategy(PlottingStrategy):
    """
    This class is a concrete implementation of the PlottingStrategy
    interface for plotting graphs. This strategy is used for plotting in
    non-interactive environments, such as python IDEs or command line
    environments, where plots are not displayed automatically.

    """

    def plot(self):
        # In non-interactive environments, we need to explicitly call
        # plt.show()
        plt.show()
