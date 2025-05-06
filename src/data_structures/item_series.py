"""
item_series.py
------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

import sys
from collections import Counter
from typing import List, Tuple, Any, cast

import pandas as pd
from matplotlib import pyplot as plt
from pandas import Series

from src.data_structures.item_collection import ItemCollection, T
from src.stats.analyzer import Analyzer
from src.stats.statistics_factory import get_analyzer
from src.utils.string_utils import StringUtils


class ItemSeries(ItemCollection[T]):
    """
    ItemSeries class representing a pandas Series.

    Attributes
    ----------
    elements : Series
        The elements of the Series.

    name : str
        The name of the Series.

    distinct_objects : Series
        The distinct elements in the Series when dealing with objects (such as
        lists).

    distinct_elements : List[Any]
        A list of distinct elements in the Series.

    first_element : T | None
        The first element in the Series. Returns None if the Series is empty.

    frequencies : Counter
        The frequencies of the elements in the Series. Computed property
        without setter.

    frequencies_in_alpha_order : List[Tuple[str, int]]
        The elements sorted alphabetically along with their frequencies.
        Computed property without setter.

    frequencies_in_freq_order : List[Tuple[str, int]]
        The elements sorted by frequency, and alphabetically within equal
        frequencies. Computed property without setter.

    last_element : T | None
        The last element in the Series. Returns None if the Series is empty.
        Computed property without setter.

    n_unique_elements : int
        The number of unique elements in the Series. Computed property without
        setter.

    sorted_elements : Series
        The sorted elements of the Series. Computed property without setter.

    stats : Analyzer
        The statistical analysis of the Series. Computed property without
        setter.

    Methods
    -------
    get_element_by_id(element_id) -> T:
        Gets an element from the Series using its index number.

    print_frequencies(order) -> None:
        Prints the frequencies of the elements in alphabetical or frequency
        order.

    to_strings() -> Series:
        Converts the elements of the Series into strings.

    """

    def __init__(
            self,
            elements: Series,
            name: str
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the ItemSeries class.

        """

        super().__init__(elements, name)

    # region --- Properties

    @property
    def distinct_objects(self) \
            -> Series:
        """
        Gets the distinct elements of the Series in case they are objects.

        Sorts the elements in ascending order.

        This is useful when dealing with columns that contain lists of
        values because the unique() method used in the distinct_elements
        property cannot compare lists.

        Returns
        -------
        Series
            The sorted distinct elements of the Series.

        """

        return Series(self._elements).drop_duplicates().sort_values()

    @property
    def distinct_elements(self) \
            -> List[Any]:
        """
        Gets the distinct elements of the Series.

        Implements the corresponding abstract method of the parent class.

        Returns
        -------
        List[Any]
            A list of unique objects in the Series.

        Notes
        -----
        This method uses the unique() method to get the distinct elements,
        which is faster than the 'drop_duplicates()' method used in the
        'distinct_objects' property. However, as it does not support lists,
        it will call the 'distinct_objects' property when the elements in
        the Series are of dtype 'object'.

        """

        try:
            return sorted(self._elements.unique().tolist())

        except Exception as err:

            if self._elements.dtype == 'object':
                return self.distinct_objects.tolist()

            # Raise a new exception of the same type with enhanced message
            # Ensure the original traceback is preserved
            err_type, _, err_traceback = sys.exc_info()
            msg = (
                    "Unexpected error occurred while trying to get the "
                    "distinct elements of the Series: %s" % self
            )
            new_exception = err_type(msg)  # type: ignore

            raise new_exception.with_traceback(err_traceback) from err

    @property
    def n_unique_elements(self) \
            -> int:
        """
        Gets the number of unique elements in the Series.

        Returns
        -------
        int
            The number of unique elements in the Series.

        """

        return self.elements.nunique()

    @property
    def sorted_elements(self) \
            -> Series:
        """
        Gets the sorted elements of the Series
        """

        return Series(self._elements).dropna().sort_values()

    @property
    def first_element(self) \
            -> T | None:
        """
        Gets the first element of the Series.

        Implements the corresponding abstract method of the parent class.

        Returns
        -------
        T | None
           The first element, which is of type T. None if the Series is
           empty.

        """

        return self._elements.iloc[0] if not self._elements.empty else None

    @property
    def last_element(self) \
            -> T | None:
        """
        Gets the last element of the Series.

        Implements the corresponding abstract method of the parent class.

        Returns
        -------
        T | None
           The last element, which is of type T. None if the Series is
           empty.

        """

        return self._elements.iloc[-1] if not self._elements.empty else None

    @property
    def frequencies(self) \
            -> Counter:
        """
        Gets the frequencies of the elements in the Series.

        Returns
        -------
        Counter
            The frequencies of the elements in the Series.

        """

        return self._count_frequencies()

    @property
    def frequencies_in_alpha_order(self) \
            -> List[Tuple[str, int]]:
        """
        Gets the elements sorted alphabetically along with their frequencies.

        Returns
        -------
        List[Tuple[str, int]]
            A list of tuples, each containing an element and its frequency,
            sorted alphabetically.

        """

        return sorted(
            self.frequencies.items(),
            key=lambda item: StringUtils.normalize_string(item[0])
        )

    @property
    def frequencies_in_freq_order(self) \
            -> List[Tuple[str, int]]:
        """
        Gets the elements sorted by frequency.

        Gets the elements sorted by frequency, with ties being sorted
        alphabetically.

        Returns
        -------
        List[Tuple[str, int]]
            A list of tuples, each containing an element and its frequency,
            sorted by frequency in descending order.

        """

        return sorted(
            self.frequencies.items(),
            key=lambda item: (-item[1], StringUtils.normalize_string(item[0]))
        )

    @property
    def stats(self) \
            -> Analyzer:
        """
        Returns statistical analysis of the Series.

        """

        freqs = get_analyzer('frequency', self)
        return freqs

    def frequencies_diagram(
            self,
            x_label: str,
            min_freq: int = 0,
            max_n: int = 1000
    ) -> None:
        """
        Plots the frequencies of the elements in the Series.

        Limits the number of included elements to max_n.

        Limits the displayed elements to those with a frequency greater than
        or equal to min_freq.

        Parameters
        ----------
        x_label : str
            The label of the x-axis. Also used to set the title of the diagram.

        min_freq : int
            The minimum frequency to be displayed. Default is 0.

        max_n : int
            The maximum number of frequencies to be displayed. Default is 1000.

        """

        freqs = self.frequencies_in_freq_order[:max_n]

        freqs = [
            freq
            for freq in freqs
            if freq[1] >= min_freq
        ]

        # Unpack the tuples in the sorted list of frequencies into two lists
        # (one for the labels and one for the frequencies).
        labels, counts = zip(*freqs)

        # Plot the frequencies as a bar chart
        # alpha = 0.5 to turn the colors slightly transparent
        plt.figure(figsize=(8, 6))
        plt.bar(labels, counts, alpha=1.0)

        # Rotate the labels diagonally
        plt.xticks(rotation=45, size=10, horizontalalignment='right')

        # Adjust the subplot layout to ensure there's space for labels
        plt.tight_layout()

        # Increase the margins
        plt.subplots_adjust(left=0.10, right=0.95, top=0.95, bottom=0.25)

        plt.title(f"{max_n} Most Frequent {self.name}")
        plt.xlabel(x_label)
        plt.ylabel("Frequency")

        plt.show()

    # endregion --- Properties

    # region --- Methods

    def get_element_by_id(self, element_id: int) \
            -> T:
        """
        Gets an element from the Series using its index number.

        Parameters
        ----------
        element_id : int
           The index of the element to find and return.

        Returns
        -------
        T
           The element at the specified index.

        Notes
        -----
        This method overrides the same method in the ItemCollection base class,
        because an element of o Series is accessed by other means than an
        element of a list.

        """

        return self._elements.iloc[element_id]

    def print_frequencies(self, order: str = 'alpha') \
            -> None:
        """
        Prints the frequencies of elements in the Series.

        Parameters
        ----------
        order : str
           The order in which to print the frequencies. Can be 'freq' for
           frequency order or any other value for alphabetical order.
           Default is 'alpha', which will result in an alphabetically sorted
           frequency list.

        """

        match order:
            case 'freq':
                sorted_freqs = self.frequencies_in_freq_order
            case _:
                sorted_freqs = self.frequencies_in_alpha_order

        for key, value in sorted_freqs:
            print(f"{key}: {value}")

    def to_strings(self) \
            -> Series:
        """
        Converts the elements of the Series to strings.

        Returns
        -------
        Series
            The Series, with its elements converted to strings.

        """
        return cast(Series, self._elements.astype(str))

    # endregion --- Methods

    # region --- Protected Methods

    def _add(self, element: T) \
            -> None:
        """
        Add the given element to the Series.

        Parameters
        ----------
        element : T
            The element to add to the Series.

        Notes
        -----
        This method does not return any values. Instead, the Series is
        modified in place.

        """

        self._elements = pd.concat(
            [
                self._elements,
                Series([element])
            ],
            ignore_index=True
        )

    def _count_frequencies(self) \
            -> Counter[T]:
        """
        Counts the frequencies of the elements in the item list.

        Sorts the frequency list first by descending frequency order and then
        alphabetically by name.

        Returns
        -------
        Counter[T]
            The frequencies of the elements in the item list, where the
            unique elements are the keys and the frequencies are the values.

        Notes
        -----
        - The Counter class is a subclass of dict, so it can be used in the
          same way as a dict.

        - Using the Counter class has been tested to be much more efficient
          than a custom implementation.

        """

        sorted_freqs = self._sort_by_frequency_and_name()
        return Counter(dict(sorted_freqs))

    def _remove(self, element: T) \
            -> None:
        """
        Removes the given element from the Series.

        Parameters
        ----------
        element : T
           The element to be removed from the Series.

        Notes
        -----
        This method does not return any values. Instead, the Series
        is modified in place.

        """
        self._elements = self._elements[
            self._elements != element].reset_index(drop=True)

    def _sort_by_frequency_and_name(self):
        """Sort by frequency descending, then alphabetically."""

        freqs = Counter(self._elements)
        return sorted(freqs.items(), key=lambda x: (-x[1], x[0]))

    # endregion --- Protected Methods
