"""
single_prompt_evaluation.py
---------------------------
Version 1.0, updated on 2024-12-15

"""

from typing import Any, Tuple, List

from pandas import Series

from logger import Logger
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.evaluation.classification_evaluation import (
    ClassificationEvaluation
)
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.stats.labels import Labels
from src.utils.print_utils import print_in_box


class SinglePromptEvaluation(LoggingMixin):
    """
    SinglePromptEvaluation class
    
    """

    def __init__(
            self,
            correct_labels: Labels,
            col: Series,
            language: str = 'en',
            col_name: str = ''
    ):
        """
        Initializes the SinglePromptEvaluation class with the given parameters.

        Parameters
        ----------
        correct_labels : Labels
            The correct labels the predicted labels are to be compared to.

        col : Series
            The column containing the predicted labels.

        language : str
            The language for which the prompt is used.

        col_name : str
            The name of the column with the classification results to evaluate.

        """

        self._predicted_labels = None
        self._correct_labels = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.correct_labels: Labels = correct_labels
        self.predicted_labels: Labels = Labels(col, col_name)

        self.language = language
        self.col_name = col_name

        # Variable for the current prompt name
        self.prompt_name = f'{language}_{col_name[7:]}'

    # region --- Properties

    @property
    def correct_labels(self) \
            -> Labels:
        """
        Gets the correct labels.

        Raises
        ------
        CriticalException
            If no correct labels are set.

        """

        if not self._correct_labels:
            raise CriticalException(
                self.logger,
                "Correct labels are not set. Cannot perform evaluation!"
            )

        return self._correct_labels

    @correct_labels.setter
    def correct_labels(self, labels: Labels) \
            -> None:
        """
        Sets the correct labels.
        """

        self._correct_labels = labels

    @property
    def predicted_labels(self) \
            -> Series:
        """
        Gets the predicted labels.
        """

        return self._predicted_labels

    @predicted_labels.setter
    def predicted_labels(self, labels: Labels) \
            -> None:
        """
        Sets the predicted labels.
        """

        self._predicted_labels = labels

    @property
    def predicted_freqs(self) \
            -> Tuple[str, List[Tuple[str, int]]]:
        """
        Returns the prompt name and the frequencies of the predicted labels.

        Returns
        -------
        Tuple[str, List[Tuple[str, int]]]
            A tuple, where the first element is a string representing a
            prompt's name und the second element a list of tuples where the
            first element is a sentiment label and the second element the
            frequency of the first element.


        """

        return self.prompt_name, self.predicted_labels.freqs

    # endregion --- Properties

    # region --- Public Methods

    def compute_metrics(self) \
            -> Any:
        """
        Computes the metrics for the answer column passed to this class.

        Computes the metrics of the predicted labels based on the correct
        labels.

        """

        evaluation = ClassificationEvaluation(
            self.prompt_name,
            self.correct_labels.elements,
            self.predicted_labels.elements
        )

        evaluation.compute_metrics()
        return evaluation.metrics

    def compare_freqs(self) \
            -> None:
        """
        Compares the frequencies of correct labels and predicted labels.

        Outputs the comparison result to the console.

        """
        title = (f"Frequencies of {self.predicted_labels.name} "
                 f"labels")
        subtitle = f"Correct: \n{self.correct_labels.freqs}\nPredicted:"
        body = self.predicted_labels.freqs

        print_in_box(title, body, subtitle)

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
