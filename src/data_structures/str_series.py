"""
str_series.py
-------------
Version 1.0, updated on 2025-05-01

"""

from typing import List

import pandas as pd

from src.data_structures.item_series import ItemSeries
from type_aliases import StatsType


class StrSeries(ItemSeries):
    """
    StrSeries class.

    Class representing a pandas Series of strings (objects). This
    class implements the ItemSeries class and inherits its attributes and
    methods.

    Attributes
    ----------
    elements : Series
        The elements of the Series.

    name : str
        The name of the Series.

    dev_frequency : float
        The standard deviation of the frequency of the unique elements.

    least_frequent_unique_elements : List[str]
        The least frequent unique elements in the Series.

    max_frequency : int
        The frequency of the most frequent unique element.

    max_percentage_of_occurrences : float
        The percentage of occurrences of the most frequent unique element.

    mean_frequency : float
        The mean frequency of the unique elements.

    mean_percentage_of_occurrences : float
        The mean percentage of occurrences of the unique elements.

    median_frequency : float
        The median frequency of the unique elements.

    median_percentage_of_occurrences : float
        The median percentage of occurrences of the unique elements.

    min_frequency : int
        The frequency of the least frequent unique element.

    min_percentage_of_occurrences : float
        the percentage of occurrences of the least frequent element.

    most_frequent_unique_elements : List[str]
        The most frequent unique elements in the Series.

    n_least_frequent_unique_elements : int
        The number of unique elements with the lowest frequency.

    n_most_frequent_unique_elements : int
        The number of unique elements with the highest frequency.

    stats : StatsType
        A dictionary representation of the StrSeries instance.

    std_dev_percentage_of_occurrences : float
        The standard deviation of the percentage of occurrences.


    See Also
    --------
    ItemSeries
        Parent class of the present class.

    """

    def __init__(
            self,
            elements: pd.Series,
            name: str
    ):
        """
        Constructor.

        Initializes a new instance of the StrSeries class with a pandas Series
        of type object.

        Parameters
        ----------
        elements : pd.Series
            The elements of the Series.

        name : str
            The name of the Series.

        """

        super().__init__(elements, name)

    def __str__(self):
        """
        Returns a string representation of the StrSeries instance.
        """

        elements_preview = ', '.join(str(el) for el in self.elements.head(5))
        more_elements = '' if len(self.elements) <= 5 else ', ...'
        return (f"StrSeries '{self.name}': \n"
                f"{len(self.elements)} elements, "
                f"unique elements: {self.n_unique_elements} \n"
                f"number of unique elements with highest frequency: "
                f"{self.n_most_frequent_unique_elements} \n"
                f"number of unique elements with least frequency: "
                f"{self.n_least_frequent_unique_elements} \n"
                f"most frequent: {self.most_frequent_unique_elements} \n"
                f"least frequent: {self.least_frequent_unique_elements} \n"
                f"max frequency: {self.max_frequency} \n"
                f"min frequency: {self.min_frequency} \n"
                f"mean frequency: {self.mean_frequency} \n"
                f"median frequency: {self.median_frequency} \n"
                f"standard deviation: {self.dev_frequency} \n"
                f"max percentage of occurrences: "
                f"{self.max_percentage_of_occurrences} \n"
                f"min percentage of occurrences: "
                f"{self.min_percentage_of_occurrences} \n"
                f"mean percentage of occurrences: "
                f"{self.mean_percentage_of_occurrences} \n"
                f"median percentage of occurrences: "
                f"{self.median_percentage_of_occurrences} \n"
                f"standard deviation of percentage of occurrences: "
                f"{self.std_dev_percentage_of_occurrences} \n"
                f"Preview: [{elements_preview}{more_elements}]")

    # region --- Properties

    @property
    def n_most_frequent_unique_elements(self) \
            -> int:
        """
        Gets the number of unique elements with the highest frequency.

        Returns
        -------
        int
            The number of unique elements with the highest frequency.

        """

        return sum(
            1 for count in self.frequencies.values()
            if (count == self.max_frequency)
        )

    @property
    def n_least_frequent_unique_elements(self) \
            -> int:
        """
        Gets the number of unique elements with the lowest frequency.

        Returns
        -------
        int
            The number of unique elements with the lowest frequency.

        """

        return sum(
            1 for count in self.frequencies.values()
            if (count == self.min_frequency)
        )

    @property
    def most_frequent_unique_elements(self) \
            -> List[str]:
        """
        Gets the most frequent unique elements in the Series.

        Returns
        -------
        str
            The most frequent unique element in the Series.

        """

        return self.elements.value_counts().head(3).keys().to_list()

    @property
    def least_frequent_unique_elements(self) \
            -> List[str]:
        """
        Gets the least frequent unique elements in the Series.

        Returns
        -------
        pd.Series
            The least frequent unique elements in the Series.

        """

        return self.elements.value_counts().tail(3).keys().to_list()

    @property
    def max_frequency(self) \
            -> int:
        """
        Gets the frequency of the most frequent unique element.

        Returns
        -------
        int
            The frequency of the most frequent unique element.

        """

        return self.elements.value_counts().head(1).values[0]

    @property
    def min_frequency(self) \
            -> int:
        """
        Gets the frequency of the least frequent unique element.

        Returns
        -------
        int
            The frequency of the least frequent unique element.

        """

        return self.elements.value_counts().tail(1).values[0]

    @property
    def mean_frequency(self) \
            -> float:
        """
        Gets the mean frequency of the unique elements.

        Returns
        -------
        float
            The mean frequency of the unique elements.

        """

        return self.elements.value_counts().mean()

    @property
    def median_frequency(self) \
            -> float:
        """
        Gets the median frequency of the unique elements.

        Returns
        -------
        float
            The median frequency of the unique elements.

        """

        return self.elements.value_counts().median()

    @property
    def dev_frequency(self) \
            -> float:
        """
        Gets the standard deviation of the frequency of the unique elements.

        Returns
        -------
        float
            The standard deviation of the frequency of the unique elements.

        """

        return self.elements.value_counts().std()

    @property
    def max_percentage_of_occurrences(self) \
            -> float:
        """
        Gets the percentage of occurrences of the most frequent unique element.

        Returns
        -------
        float
            The percentage of occurrences of the most frequent unique element.

        """

        return self.max_frequency / len(self.elements)

    @property
    def min_percentage_of_occurrences(self) \
            -> float:
        """
        Gets the percentage of occurrences of the least frequent element.

        Returns
        -------
        float
            The percentage of occurrences of the least frequent unique element.

        """

        return self.min_frequency / len(self.elements)

    @property
    def mean_percentage_of_occurrences(self) \
            -> float:
        """
        Gets the mean percentage of occurrences of the unique elements.

        Returns
        -------
        float
            The mean percentage of occurrences of the unique elements.

        """

        return self.mean_frequency / len(self.elements)

    @property
    def median_percentage_of_occurrences(self) \
            -> float:
        """
        Gets the median percentage of occurrences of the unique elements.

        Returns
        -------
        float
            The median percentage of occurrences of the unique elements.

        """

        return self.median_frequency / len(self.elements)

    @property
    def std_dev_percentage_of_occurrences(self) \
            -> float:
        """
        Gets the standard deviation of the percentage of occurrences.

        Returns
        -------
        float
            The standard deviation of the percentage of occurrences of the
            unique elements.

        """

        return self.dev_frequency / len(self.elements)

    @property
    def stats(self) \
            -> StatsType:
        """
        Returns a dictionary representation of the StrSeries instance.

        Returns a dictionary that can be used to build a DataFrame
        representation of the StrSeries instance.

        The dictionary includes
        - the name of the StrSeries instance
        - the number of elements in the Series
        - the number of unique elements in the Series
        - the number of unique elements with the highest frequency
        - the number of unique elements with the lowest frequency
        - the frequency of the most frequent unique element
        - the frequency of the least frequent unique element
        - the mean frequency of the unique elements
        - the median frequency of the unique elements
        - the standard deviation of the frequency of the unique elements
        - the percentage of occurrences of the most frequent unique element
        - the percentage of occurrences of the least frequent unique element
        - the mean percentage of occurrences of the unique elements
        - the median percentage of occurrences of the unique elements
        - the standard deviation of the percentage of occurrences

        Returns
        -------
        StatsType

            The dictionary representation of the StrSeries instance.

        """

        return {
            'n_elements': len(self.elements),
            'n_unique_elements': self.n_unique_elements,
            'n_most_frequent_unique_elements':
                self.n_most_frequent_unique_elements,
            'n_least_frequent_unique_elements':
                self.n_least_frequent_unique_elements,
            'most_frequent_unique_elements':
                self.most_frequent_unique_elements,
            'least_frequent_unique_elements':
                self.least_frequent_unique_elements,
            'max_frequency': self.max_frequency,
            'min_frequency': self.min_frequency,
            'mean_frequency': self.mean_frequency,
            'median_frequency': self.median_frequency,
            'dev_frequency': self.dev_frequency,
            'max_percentage_of_occurrences':
                self.max_percentage_of_occurrences,
            'min_percentage_of_occurrences':
                self.min_percentage_of_occurrences,
            'mean_percentage_of_occurrences':
                self.mean_percentage_of_occurrences,
            'median_percentage_of_occurrences':
                self.median_percentage_of_occurrences,
            'std_dev_percentage_of_occurrences':
                self.std_dev_percentage_of_occurrences

        }

    # endregion --- Properties
