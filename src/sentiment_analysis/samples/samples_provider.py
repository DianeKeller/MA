"""
samples_provider.py
-------------------
Version 1.0, updated on 2025-05-01

"""

from abc import ABC, abstractmethod
from typing import Dict, TypeVar
from typing import TYPE_CHECKING

from logger import Logger
from src.data_structures.my_data_frame import MyDataFrame
from src.logging_mixin import LoggingMixin

if TYPE_CHECKING:
    from src.sentiment_analysis.samples.samples_manager import SamplesManager

T = TypeVar('T', bound='DataSourceSuite')
S = TypeVar('S', bound='DataSourceStrategy')


class SamplesProvider(ABC, LoggingMixin):
    """
    SamplesProvider class.

    This is the base class for the BalancedSamplesProvider and the
    UnbalancedSamplesProvider classes. It provides logging functionality and
    defines the methods both classes must implement.

    Attributes
    ----------
    logger : Logger
        The logger instance used for logging within the samples provider
        subclasses.

    Methods
    -------
    get_samples(self)
            -> Dict[str, src.data_structures.my_data_frame.MyDataFrame]:
        Retrieves and returns samples for sentiment analysis.

    """

    def __init__(
            self,
            samples_manager: "SamplesManager"
    ):
        self.samples_manager: "SamplesManager" = samples_manager

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    @abstractmethod
    def get_samples(self) \
            -> Dict[str, MyDataFrame]:
        """
        Retrieves and returns samples for sentiment analysis.

        Returns
        -------
        Dict[str, MyDataFrame]
            A Dictionary where the keys are the languages and the values
            are the samples for the respective languages.

        Raises
        ------
        NotImplementedError
            If the subclass does not implement this abstract method.

        """

        raise NotImplementedError