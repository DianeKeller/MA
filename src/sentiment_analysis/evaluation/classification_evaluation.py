"""
classification_evaluation.py
----------------------------
Version 1.0, updated on 2025-05-01

"""

from typing import List

from pandas import Series
from sklearn.metrics import (
    accuracy_score, f1_score, recall_score, precision_score
)

from src.sentiment_analysis.evaluation.metrics import Metrics


class ClassificationEvaluation:
    """
    ClassificationEvaluation class.

    This class provides the tools for the evaluation of classification results.

    """

    LABELS: List[str] = [
        "positive",
        "negative",
        "neutral"
    ]

    def __init__(
            self,
            name: str = '',
            correct_labels: Series | None = None,
            predicted_labels: Series | None = None
    ):
        """
        Initiates the ClassificationEvaluation class with the given parameters.

        Initiates the ClassificationEvaluation class with correct and
        predicted labels.

        Parameters
        ----------
        name : str
            The name of the performed classification, used to name the set
            of metrics.

        correct_labels : Series
            The correct labels to compare the classification results to.

        predicted_labels : Series
            The labels predicted in the classification process, to be
            compared to the correct labels.

        """

        self._name = name
        self._predicted_labels = None
        self._correct_labels = None

        self.metrics = Metrics()

        self.set_labels(correct_labels, predicted_labels)

    # region --- Properties

    @property
    def name(self) \
            -> str:
        return self._name

    @name.setter
    def name(self, name: str) \
            -> None:
        self._name = name

    @property
    def correct_labels(self) \
            -> Series:
        """
        Gets the correct labels.
        """

        return self._correct_labels

    @correct_labels.setter
    def correct_labels(self, labels: Series) \
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
    def predicted_labels(self, labels: Series) \
            -> None:
        """
        Sets the predicted labels.
        """

        self._predicted_labels = labels

    @property
    def accuracy(self) \
            -> float:
        """
        Gets the accuracy.

        Gets the proportion of correctly predicted labels among all labels.

        """

        return self._get_metric("accuracy", accuracy_score)

    # region --- Public Methods

    def set_labels(self, correct_labels: Series, predicted_labels: Series) \
            -> None:

        self._ensure_matching_types(correct_labels, predicted_labels)

    def compute_metrics(self) \
            -> None:
        """
        Computes the metrics for the evaluation of the sentiments prediction.

        Computes the metrics for the evaluation of the sentiments prediction
        and stores them in the dictionary of the metrics property.

        """

        self.metrics.store('info', self.name)
        self.metrics.store('acc', self.accuracy)

        for metric_name, func in [
            ('f1', f1_score),
            ('recall', recall_score),
            ('precision', precision_score)
        ]:
            self._compute_average_metrics(metric_name, func)
            self._compute_metrics_per_label(metric_name, func)

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods

    # region --- Private Methods
    def _get_metric(self, metric_name: str, metric_func, **kwargs) \
            -> float:
        """
        Generic method to get the metric.

        Computes the metric if it is not set.

        Notes
        -----
        The zero_division=0 parameter makes the precision, recall and f1
        metrics ignore samples for which no predicted label is given,
        to prevent division by zero errors.

        """

        if getattr(self, f"_{metric_name}", None) is None:
            my_kwargs = kwargs.copy()

            if metric_func in [f1_score, recall_score, precision_score]:
                my_kwargs['zero_division'] = 0

            setattr(
                self,
                f"_{metric_name}",
                metric_func(
                    self.correct_labels,
                    self.predicted_labels,
                    **my_kwargs
                )
            )

        return getattr(self, f"_{metric_name}")

    def _compute_metrics_per_label(self, metric_name: str, func) \
            -> None:
        """
        Computes metrics for each class.

        Computes metrics for each class and sets them in the metrics
        dictionary.

        Notes
        -----
        The zero_division=0 parameter makes the precision, recall and f1
        metrics ignore samples for which no predicted label is given,
        to prevent division by zero errors.

        """

        my_kwargs = {}

        if func in [f1_score, recall_score, precision_score]:
            my_kwargs['zero_division'] = 0

        metrics = func(
            self.correct_labels,
            self.predicted_labels,
            average=None,
            labels=self.LABELS,
            **my_kwargs  # Prevent UndefinedMetricWarning
        )

        for label, metric in zip(self.LABELS, metrics):
            self.metrics.store(f"{label}_{metric_name}", metric)

    def _compute_average_metrics(
            self,
            metric_name: str,
            func
    ) -> None:
        """
        Computes average metrics and sets them in the metrics dictionary.

        """
        for avg_type in ['macro']:
            metric = self._get_metric(
                f"{avg_type}_{metric_name}", func, average=avg_type
            )

            self.metrics.store(f"{avg_type}_{metric_name}", metric)

    def _ensure_matching_types(
            self,
            correct_labels: Series,
            predicted_labels: Series
    ) -> None:

        if correct_labels.dtype != predicted_labels.dtype:
            correct_labels = correct_labels.astype(str)
            predicted_labels = predicted_labels.astype(str)

        # Ensure there are no mixed types in the Series
        correct_labels = correct_labels.astype(correct_labels.dtype)
        predicted_labels = predicted_labels.astype(predicted_labels.dtype)

        predicted_labels = self._treat_none_values(predicted_labels)

        self.correct_labels = correct_labels
        self.predicted_labels = predicted_labels

    def _treat_none_values(self, labels: Series) \
            -> Series:
        """
        Replaces None values in the given Series by an empty string or 0.

        Replaces None values in the given Series by an empty string or 0,
        depending on the data type of the Series.

        Parameters
        ----------
        labels : Series
            The Series possibly containing None values.

        Returns
        -------
        Series
            The Series with None values filled.

        """

        if labels.dtype == object:
            return labels.fillna('')

        return labels.fillna(0)

    # endregion --- Private Methods
