"""
item_collection.py
------------------
Version 1.0, updated on 2025-05-01

"""

from abc import ABC, abstractmethod
from collections import Counter
from typing import Generic, TypeVar, List, Any

from logger import Logger
from src.logging_mixin import LoggingMixin

T = TypeVar('T')


class ItemCollection(Generic[T], LoggingMixin, ABC):
    """
    Abstract base class representing a collection of items.

    Attributes
    ----------
    name : str
       The name of the collection.

    elements : Any
       The elements in the collection.

    element_type : str
        The type of the elements in the collection, derived from the first
        element. Computed property without setter.

    n_elements : int
        The total number of elements in the collection. Computed property
        without setter.

    n_distinct_elements : int
        The number of distinct elements in the collection. Computed property
        without setter.


    Abstract Attributes
    -------------------
    distinct_elements : List[T]
        A list of distinct elements in the collection.

    first_element : T | None
        The first element in the collection.

    last_element : T | None
        The last element in the collection.

    sorted_elements : Any
        The sorted version of the elements in the collection.


    Methods
    -------
    add_element(element: T) -> None:
       Adds an element to the collection.

    remove_element(element: T) -> None:
       Removes an element from the collection.

    get_element_by_id(element_id: int) -> T:
       Gets an element by its index.

    to_strings() -> List[str]:
       Converts the elements to strings.


    Abstract Methods
    ----------------
    to_strings(self) -> List[str]:
        Converts the elements of the collection into strings.

    _add(self, element: T) -> None:
        Adds an element to the item collection.

    _remove(self, element: T) -> None:
        Removes an element from the item collection.

    """

    def __init__(
            self,
            elements: Any,
            name: str
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the ItemCollection class.

         Parameters
        ----------
        name : str
           The name of the collection.

        elements : Any
           The elements of the collection.

        """

        self._elements = elements
        self._name = name
        self._distinct_elements = None
        self._sorted_elements = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    def __str__(self) -> str:
        """
        Returns a string representation of the concrete item collection
        instance.

        The string includes
        - the name of the instance
        - the number of elements
        - the number of distinct elements
        - a preview of the elements

        """

        elements_preview = ', '.join(str(el) for el in self._elements[:5])
        more_elements = '' if len(self._elements) <= 5 else ', ...'
        return (f"{self.__class__.__name__} '{self._name}': \n"
                f"{self.n_elements} elements, "
                f"{self.n_distinct_elements} distinct \n"
                f"Preview: [{elements_preview}{more_elements}]")

    # region --- Properties

    @property
    def name(self) -> str:
        """
        Returns the name of the collection.

        """

        return self._name

    @name.setter
    def name(self, name: str) \
            -> None:
        """
        Sets the name of the collection.

        """

        self._name = name

    @property
    def elements(self) \
            -> Any:
        """
        Returns the elements of the collection.

        """

        return self._elements

    @elements.setter
    def elements(self, elements: Any) \
            -> None:
        """
        Sets the elements of the collection.

        """

        self._elements = elements
        self._reset_computed_properties()

    @property
    def element_type(self) \
            -> str:
        """
        Gets the type of the elements in the item collection as a string.

        Uses the first element to determine the type of all elements.

        Returns
        -------
        str
            The type of the elements in the item collection as a string. If the
            collection is empty, an empty string is returned.

        """

        return type(self.first_element).__name__ if self._elements else ''

    @property
    def n_elements(self) -> int:
        """
        Gets the number of elements in the collection.

        Computed property without setter.

        """

        return len(self._elements)

    @property
    def n_distinct_elements(self) \
            -> int:
        """
        Gets the number of distinct elements in the item collection.

        Computed property without setter.

        """

        return len(self.distinct_elements)

    @property
    @abstractmethod
    def distinct_elements(self) \
            -> List[T]:
        """
        Gets the distinct elements of the item collection.

        This abstract method needs to be implemented by the subclasses.

        """

    @property
    @abstractmethod
    def sorted_elements(self) \
            -> Any:
        """
        Gets the sorted elements of the item collection.

        This abstract method needs to be implemented by the subclasses.

        """

    @property
    @abstractmethod
    def first_element(self) \
            -> T | None:
        """
        Gets the first element of the item collection.

        This abstract method needs to be implemented by the subclasses.

        Returns
        -------
        T | None
            The first element, which is of type T. None if the item collection
            is empty.

        """

    @property
    @abstractmethod
    def last_element(self) \
            -> T | None:
        """
        Gets the last element of the item collection.

        This abstract method needs to be implemented by the subclasses.

        Returns
        -------
        T | None
           The last element, which is of type T. None if the item collection is
           empty.

        """

    # endregion --- Properties

    # region --- Public Methods

    def add_element(self, element: T) \
            -> None:
        """
        Adds the specified element to the item collection.

        Adds the specified element to the item collection ensuring
        that all computed properties are reset so that they will be
        updated the next time they are accessed.

        Parameters
        ----------
        element : T
            The element to be added to the item collection.

        Notes
        -----
        This method does not return any values. Instead, the item collection
        is modified in place.

        """

        self._add(element)
        self._reset_computed_properties()

    def remove_element(self, element: T) \
            -> None:
        """
        Removes the specified element from the item collection.

        Removes the specified element from the item collection, ensuring
        that all computed properties are reset so that they will be
        updated the next time they are accessed.

        Parameters
        ----------
        element : T
            The element to be removed from the item collection.

        Notes
        -----
        This method does not return any values. Instead, the item collection
        is modified in place.

        """

        self._remove(element)
        self._reset_computed_properties()

    def get_element_by_id(self, element_id: int) \
            -> T:
        """
        Gets the element by its ID (= index number) in the collection.

        Parameters
        ----------
        element_id : int
            The ID (= index number) of the element to retrieve.

        Returns
        -------
        T
            The element at the given index in the collection.

        """

        return self._elements[element_id]

    # endregion --- Public Methods

    # region --- Abstract Public Methods

    @abstractmethod
    def to_strings(self) \
            -> List[str]:
        """
        Converts the elements of the collection into strings.

        This abstract method needs to be implemented by the subclasses.

        Returns
        -------
        List[str]
           The list of the  elements converted into strings.

        """

    # endregion --- Abstract Public Methods

    # region --- Protected Methods

    def _reset_computed_properties(self) \
            -> None:
        """
        Resets the properties 'distinct_elements' and 'sorted_elements'.

        This should be called whenever the collection is modified.

        """

        self._distinct_elements = None
        self._sorted_elements = None

    def _count_frequencies(self) \
            -> Counter[T]:
        """
        Counts the frequency of each element in the collection.

        Uses the sorted elements wrapped in this class to compute the
        frequencies of the elements so that the frequencies are sorted
        alphabetically by default.

        Returns
        -------
        Counter[T]
            A Counter object with the frequency of each element in the
            collection.

        """

        return Counter(self.sorted_elements)

    # endregion --- Protected Methods

    # region --- Abstract Protected Methods

    @abstractmethod
    def _add(self, element: T) \
            -> None:
        """
        Adds an element to the item collection.

        Parameters
        ----------
        element : T
            The element to add to the item collection

        Notes
        -----
        This method does not return any values. Instead, the item collection
        is modified in place.

        """

    @abstractmethod
    def _remove(self, element: T) \
            -> None:
        """
        Removes an element from the item collection.

        Parameters
        ----------
        element : T
            The element to remove from the item collection.

        Notes
        -----
        This method does not return any values. Instead, the item collection
        is modified in place.

        """

    # endregion --- Abstract Protected Methods
