"""
metrics.py
----------
Version 1.0, updated on 2024-12-20

"""

from typing import Dict


class Metrics:
    """
    Metrics class.

    Provides a dictionary in which to store the metrics for the evaluation
    of the results.

    """

    def __init__(self):
        """
        Initializes the class by setting up a dictionary for the different
        metrics.

        Each metric is given an initial value which will be overwritten when
        the real values are stored in the dictionary.
        """

        metrics = [
            'f1', 'recall', 'precision'
        ]

        prefixes = [
            'macro',
            'negative',
            'neutral',
            'positive'
        ]

        self.values: Dict[str, str | float] = {
            "info": "",
            "acc": -1,
        }

        # Dynamic creation of dictionary keys and initial values:
        for metric in metrics:
            for prefix in prefixes:
                self.values[f"{prefix}_{metric}"] = -1

    def store(self, metric: str, value: float | str) \
            -> None:
        """
        Stores the specified value of the specified metric in the dictionary.

        Parameters
        ----------
        metric : str
            The name of the metric whose value is to be stored.

        value : flaat
            The metric's value.

        """

        self.values[metric] = value
