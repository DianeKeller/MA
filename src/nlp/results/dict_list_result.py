"""
dict_list_result.py
-------------------
Version 1.0, updated on 2025-05-01

"""

from pprint import pprint
from typing import Dict, List, Sequence

from constants import MAX_ITEMS
from src.nlp.results.result import Result


class DictListResult(Result):
    """
    This class implements the Result class for lists of dictionaries.

    Attributes
    ----------
    matches_dictionaries : List[Dict[str, Sequence[object]]]
        A list of dictionaries representing matches resulting from string
        search operations.

    Methods
    -------
    print(self, n_elements: int = MAX_ITEMS)
        Prints the elements in the matches_dictionaries.

    restrict_print_length(self, max_items: int = MAX_ITEMS)
        Restricts the length of printed items to a specified maximum.

    """

    def __init__(
            self,
            matches_dictionaries: List[Dict[str, Sequence[object]]]
    ) -> None:
        """
        Initializes the object with a list of dictionaries representing
        matches.

        Parameters
        ----------
        matches_dictionaries : List[Dict[str, Sequence[object]]]
            A list of dictionaries representing matches resulting from string
            search operations.

        """

        super().__init__()

        self.__matches_dictionaries = matches_dictionaries

    # region --- Properties
    @property
    def matches_dictionaries(self) \
            -> List[Dict[str, Sequence[object]]]:
        """
        Gets the list of dictionaries if it exists.

        Returns
        -------
        List[Dict[str, Sequence[object]]]
            The list of dictionaries.

        Raises
        ------
        AttributeError
            If the list of dictionaries does not exist.

        """

        if not self.__matches_dictionaries:
            raise AttributeError("No dictionaries given!")

        return self.__matches_dictionaries

    @matches_dictionaries.setter
    def matches_dictionaries(
            self,
            matches_dictionaries: List[Dict[str, Sequence[object]]]
    ) -> None:
        """
        Sets the matches_dictionaries.
        """

        self.__matches_dictionaries = matches_dictionaries

    # endregion --- Properties

    # region --- Methods

    def print(self, n_elements: int = MAX_ITEMS) \
            -> None:
        """
        Prints the elements in the matches_dictionaries.

        If there are only a few dictionaries in the list (up to twice the
        maximum number of elements specified in the settings), they are
        printed entirely using pretty print (pprint). Otherwise,
        the restrict_print_length method is used to output a reduced list.

        Parameters
        ----------
        n_elements : int
            An integer representing the maximum number of elements to print
            (default value is MAX_ITEMS, which is specified in the NUM
            category section in the settings file).

        """

        if len(self.matches_dictionaries) <= 2 * n_elements:
            pprint(self.matches_dictionaries)
        else:
            self.restrict_print_length(n_elements)

    def restrict_print_length(
            self,
            max_items: int = MAX_ITEMS
    ) -> None:
        """
        Restricts the length of printed items to a specified maximum.

        If the number of dictionaries exceeds twice the maximum number of
        items, it prints the first max_items items, followed by an
        ellipsis, and then the last max_items items.

        Parameters
        ----------
        max_items : int
            The maximum number of elements to print (default value is
            MAX_ITEMS, which is specified in the NUM category section in the
            settings file).

        """

        if len(self.matches_dictionaries) > 2 * max_items:
            for i in range(0, max_items):
                print(self.matches_dictionaries[i])
            print('...')
            for i in range(
                len(self.matches_dictionaries) - max_items,
                len(self.matches_dictionaries)
            ):
                print(self.matches_dictionaries[i])

    # endregion --- Methods
