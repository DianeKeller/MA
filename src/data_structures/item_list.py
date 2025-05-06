"""
item_list.py
------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

import random
from collections import Counter
from typing import List

from src.data_structures.item_collection import ItemCollection, T
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty
from src.utils.list_sort_utils import sort_list


class ItemList(ItemCollection[T]):
    """
    ItemList class representing a list of items.

    Attributes
    ----------
    elements : List[T]
        The list of elements contained in the item list.

    name : str
        The name of the item list, used to identify the item list.

    distinct_elements : List[T]
        The distinct elements in the item list. Computed property without
        setter.

    first_element : T | None
        The first element in the item list. Returns None if the list is empty.
        Computed property without setter.

    frequencies : Counter[T]
        The frequencies of the elements in the item list. Computed property
        without setter.

    last_element : T | None
        The last element in the item list. Returns None if the list is empty.
        Computed property without setter.

    random_element : T | None
        A random element from the item list. Returns None if the list is
        empty. Computed property without setter.

    sorted_elements : List[str]
        The sorted elements in the item list, represented as strings. Computed
        property without setter.


    Methods
    -------
    to_strings() -> List[str]:
        Converts the elements of the item list to strings.

    Notes
    -----
    - This class is intended to be used as a base class for more specific
      implementations, but it also allows direct usage.

    - Type consistency is ensured throughout the class utilizing Python's
      generics.

    """

    def __init__(
            self,
            elements: List[T],
            name: str
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the ItemList class.

        """

        super().__init__(elements, name)

    # region --- Properties

    @property
    def distinct_elements(self) \
            -> List[T]:
        """
        Gets the distinct elements of the item list.

        Implements the corresponding abstract method of the parent class.

        """

        if not self._distinct_elements:
            self._compute_distinct_elements()

        if not self._distinct_elements:
            raise CriticalException(
                self.logger,
                (
                    "Distinct elements could not be computed for item list "
                    "'%s'."
                ) % self.name
            )

        return self._distinct_elements

    @property
    def sorted_elements(self) \
            -> List[str]:
        """
        Gets the sorted elements of the item list as strings.

        Implements the corresponding abstract method of the parent class.

        """

        if is_none_or_empty(self._sorted_elements):
            self._compute_sorted_elements()

        if is_none_or_empty(self._sorted_elements):
            raise CriticalException(
                self.logger,
                "Sorted elements could not be computed for item list '%s'."
                % self.name
            )

        return self._sorted_elements  # type: ignore

    @property
    def random_element(self) \
            -> T | None:
        """
        Gets a random element of the item list.

        Returns
        -------
        T | None
            A random element, which is of type T. None if the item list is
            empty.

        """

        return random.choice(self.elements) if self.elements else None

    @property
    def first_element(self) \
            -> T | None:
        """
        Gets the first element of the item list.

        Implements the corresponding abstract method of the parent class.

        Returns
        -------
        T | None
            The first element, which is of type T. None if the item list is
            empty.

        """

        return self.elements[0] if self.elements else None

    @property
    def last_element(self) \
            -> T | None:
        """
        Gets the last element of the item list.

        Implements the corresponding abstract method of the parent class.

        Returns
        -------
        T | None
            The last element, which is of type T. None if the item list is
            empty.

        """

        return self.elements[-1] if self.elements else None

    @property
    def frequencies(self) \
            -> Counter[T]:
        """
        Gets the frequencies of the elements in the item list.

        Returns
        -------
        Counter[T]
            The frequencies of the elements in the item list.

        """

        return self._count_frequencies()

    # endregion --- Properties

    # region --- Methods

    def to_strings(self) \
            -> List[str]:
        """
        Converts the elements of the item list into strings.

        Calls str() on each element.

        Returns
        -------
        List[str]
            The list of the  elements converted into strings.

        """

        return [str(element) for element in self._elements]

    # endregion --- Methods

    # region --- Protected Methods

    def _add(self, element: T) \
            -> None:
        """
        Add the given element to the item list.

        Parameters
        ----------
        element : T
            The element to add to the item list.

        Notes
        -----
        This method does not return any values. Instead, the item list is
        modified in place.

        """

        self._elements.append(element)

    def _remove(self, element: T) \
            -> None:
        """
        Removes the given element from the item list.

        Parameters
        ----------
        element : T
           The element to be removed from the item list.

        Notes
        -----
        This method does not return any values. Instead, the item list
        is modified in place.

        """

        self._elements.remove(element)

    def _sort_by_frequency_and_name(self):
        """Sort by frequency descending, then alphabetically."""

        freqs = Counter(self._elements)
        return sorted(freqs.items(), key=lambda x: (-x[1], x[0]))

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

    def _compute_distinct_elements(self) \
            -> None:
        """
        Computes the distinct elements in the item list.

        To get the list of distinct elements in the item list,
        the list of elements wrapped in this class is converted into a set
        and back into a list.

        """

        self._distinct_elements = list(set(self._elements))

    def _compute_sorted_elements(self) \
            -> None:
        """
        Computes the sorted elements in the item list.

        Converts the list of elements wrapped in this class into a list
        of strings that can be handled by the sort_list function.

        """

        self._sorted_elements = sort_list(self.to_strings())

    # endregion --- Protected Methods
