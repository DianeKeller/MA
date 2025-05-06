"""
alphabet.py
-----------
Version 1.0, updated on 2024-12-26

"""
from typing import Set, Dict, List, Tuple

from src.data_structures.str_series import StrSeries
from logger import Logger


class Alphabet:
    """
    Alphabet class.
    
    """

    def __init__(self, text_collection: StrSeries):
        self._text_collection = text_collection

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    # region --- Properties
    @property
    def text_collection(self) \
            -> StrSeries:
        """
        Returns the text collection.

        Returns
        -------
        StrSeries
            A StrSeries object containing a series of strings representing a
            text collection.

        """

        return self._text_collection

    @text_collection.setter
    def text_collection(self, text_collection: StrSeries) \
            -> None:
        """
        Sets the text_collection to analyze.

        Parameters
        ----------
        text_collection : StrSeries
            A StrSeries object containing a series of strings representing a
            text collection.

        """

        self._text_collection = text_collection

    @property
    def chars(self) \
            -> Set[str]:
        """
        Returns the sorted unique characters in the collection of texts.

        Returns
        -------
        Set[str]
            The sorted unique characters in the collection of texts.

        Notes
        -----
        Computed property without setter.

        """

        # Combine all text in the series into a single string and extract
        # unique characters
        unique_chars = set(''.join(
            self.text_collection.elements.dropna()))  # Drop NaN values,

        # Sort characters and return as a set
        return set(sorted(unique_chars))

    @property
    def chars_with_codes(self) \
            -> Dict[str, int]:
        """
        Returns the alphabet of the texts with the corresponding Unicode codes.

        Returns a dictionary of the unique characters in the text collection
        along with their corresponding Unicode codes.

        Returns
        -------
        Dict[str, int]
            A dictionary unique characters in the text collection, where the
            keys are the characters and the values are their corresponding
            Unicode codes.

        Notes
        -----
        Computed property without setter.

        """

        return {char: ord(char) for char in self.chars}

    # endregion --- Properties

    # region --- Public Methods

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
