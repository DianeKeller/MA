"""
plotting_strategy.py
----------
Version 1.0, updated on 2024-09-09

"""

from abc import ABC, abstractmethod


class PlottingStrategy(ABC):
    """
    This class serves as an interface within the framework of
    a strategy pattern. It enables a dynamic change of plotting
    strategies according to the kind of environment the program is running
    in. The class declares the common plot method used by all supported
    plotting strategies.

    Abstract Methods
    ----------------
    plot() -> None:
        Plots data using the plotting strategy currently in use.

    """

    @abstractmethod
    def plot(self) \
            -> None:
        """
        Plots data using the plotting strategy currently in use.
        """
