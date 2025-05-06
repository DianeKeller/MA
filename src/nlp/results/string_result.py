"""
string_result.py
----------------
Version 1.0, updated on 2024-12-17

"""

from pprint import pprint

from constants import MAX_STRING_LENGTH
from src.nlp.results.result import Result


class StringResult(Result):
    """
    StringResult class.

    This class implements the abstract Result class, managing string results.

    Attributes
    ----------
    string : str
        The string representing the result.

    """

    def __init__(self, string: str) \
            -> None:
        """
        Constructor.

        Initializes the StringResult class with the provided string.

        Parameters
        ----------
        string : str
            The result string to be managed and printed.

        """

        super().__init__()

        self.__string = None
        self.string = string

    # region --- Properties
    @property
    def string(self) \
            -> str:
        """
        Retrieves the result string.

        Returns
        -------
        str
            The managed result string.

        """

        return self.__string

    @string.setter
    def string(self, string: str) \
            -> None:
        """
        Sets the result string.

        """

        self.__string = string

    # endregion --- Properties

    # region --- Methods

    def print(self, n_elements: int = MAX_STRING_LENGTH):
        """
        Prints the result string.

        If the string's length exceeds the specified maximum, the output
        is restricted to a predefined length.

        Parameters
        ----------
        n_elements : int, optional
            Maximum number of elements to print, default is
            MAX_STRING_LENGTH, which is set in the settings file.

        """

        if len(self.string) < n_elements:
            print(self.string)
        else:
            self.restrict_print_length()

    def restrict_print_length(
            self
    ) -> None:
        """
        Prints the result string using pretty-print.

        This method is called when the string length exceeds the maximum
        allowed length for direct printing.

        """

        pprint(self.string)

    # endregion --- Methods
