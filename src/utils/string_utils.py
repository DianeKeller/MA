"""
string_utils.py
---------------
Version 1.0, updated on 2024-12-04

"""

import re
from typing import List, Set

import unicodedata
from pandas import Series

from logger import Logger
from src.decorators.data_check_decorators import input_not_none_or_empty
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)

logger = Logger(__name__).get_logger()
log = LoggingMixin().log


class StringUtils(LoggingMixin):
    """
    StringUtils class.

    Static class for handling strings.

    Class Methods
    -------------
    all_end_with_underscore_and_numbers(lst: List[str]) -> bool:
        Checks if all strings in the list end with an underscore and numbers.

    convert_class_name_into_module_name(class_name: str) -> str:
        Returns the module name of a given class.

    first_char_to_upper(string: str) -> str:
        Converts the first character of a string to uppercase.

    get_first_sentence(input_string: str) -> str:
        Extracts the first sentence from the provided input string.

    get_int_behind_last_underscore(s: str) -> int:
        Returns the number behind the last underscore in a string.

    get_prefixes(elements: Union[List[str], pandas.core.series.Series])
            -> List[str]:
        Extracts prefixes separated by underscores from strings.

    get_str_before_last_underscore(s: str) -> str:
        Returns the string before the last underscore in a string.

    get_unique_prefixes(elements: Union[List[str], pandas.core.series.Series])
            -> Set[str]:
        Extracts a list of unique prefixes from strings.

    normalize_string(s: str) -> str:
        Normalizes a string.

    remove_extension_from_file_name(file_name: str) -> str:
        Removes the file extension from a given file name.

    shorten_string_by_n_chars(s: str, n_chars: int) -> str:
        Shortens a string by the specified number of characters.

    trim(s: str) -> str:
        Removes leading and trailing whitespace from a string.

    """

    @classmethod
    def convert_class_name_into_module_name(cls, class_name: str) \
            -> str:
        """
        Returns the module name of a given class.

        Converts the CamelCase class name to its snake_case module name.

        Parameters
        ----------
        class_name: str
            The name of the class whose module is requested.

        Returns
        -------
        str
            The module name of the given class.

        Examples
        --------

        .. code-block:: python

            >>> convert_class_name_into_module_name('TxtStrategy')
            'txt_strategy'

            >>> convert_class_name_into_module_name('MyClass1')
            'my_class_1'

            >>> convert_class_name_into_module_name('MyClassV20')
            'my_class_v_20'

            >>> convert_class_name_into_module_name('Class2023Update')
            'class_2023_update'

            >>> convert_class_name_into_module_name('HTTPRequest')
            'http_request'

            >>> convert_class_name_into_module_name('JSONParser')
            'json_parser'
            >>> convert_class_name_into_module_name('IDNumber')
            'id_number'

        Notes
        -----
        Explanation of the regex per line:

        [1] Set x flag to allow comments at the end of the lines.
        [2] Find a position before an uppercase letter that is preceded by
            a lowercase letter or a digit,
        [3] Or a position before an uppercase letter followed by a
            lowercase letter when preceded by another uppercase letter (e.g.,
            HTTPRequest -> http_request),
        [4] Or a position before a digit that is preceded by a letter.
        [5] Use the regex (to find a position that needs to be modified) in the
            class_name string, insert an underscore at that position and
            convert the resulting string to lower case.

        """

        regex = r'''(?x)                        # [1]
            (?<=[a-z0-9])(?=[A-Z])          # [2]
            | (?<=[A-Z])(?=[A-Z][a-z])      # [3]
            | (?<=[a-zA-Z])(?=\d)        # [4]
    '''

        return re.sub(regex, '_', class_name).lower()  # [5]

    @classmethod
    def trim(cls, s: str) \
            -> str:
        """
        Removes leading and trailing whitespace from a string.

        Parameters
        ----------
        s
            The string to be trimmed.

        Returns
        -------
        str
            The trimmed string.

        """

        return s.strip()

    @classmethod
    def normalize_string(cls, s: str) \
            -> str:
        """
        Normalizes a string.

        Normalizes a string by converting it to lowercase and replacing
        diacritics with their base form.

        Parameters
        ----------
        s
            The string to be normalized.

        Returns
        -------
        str
            The normalized string.

        """

        s = s.lower()

        # Normalize diacritics to separate characters
        s = unicodedata.normalize("NFKD", s)

        # Remove diacritic marks
        s = ''.join(
            c for c in s if not unicodedata.combining(c)
        )
        return s

    @classmethod
    @input_not_none_or_empty('File name')
    def remove_extension_from_file_name(cls, file_name: str) \
            -> str:
        """
        Removes the file extension from a given file name.

        1Splits the file name at the last dot and only returns the first
        part of the string.

        Parameters
        ----------
        file_name

        Returns
        -------
        str
            The file name without the file extension.

        Notes
        -----
        - If the file name does not contain a dot, the entire file name will be
          returned.

        - If the file name contains multiple dots, only the last extension will
          be removed.

        - Make sure you pass a real file name not strings like one or two dots
          only. The latter will return unexpected results.

        """
        # Check if the file name consists only of dots
        if file_name.strip('.') == '':
            raise CriticalException(
                cls.logger,
                "The file name cannot consist only of dots."
            )

        # For hidden files, ensure the file name is not split at the first dot
        if file_name.startswith('.') and file_name.count('.') == 1:
            # If it's a hidden file without an extension, return it as is
            return file_name

        # In other cases, split the file name from the right side into a
        # maximum of two parts
        parts = file_name.rsplit('.', 1)
        return parts[0]

    @classmethod
    def shorten_string_by_n_chars(cls, s: str, n_chars: int) \
            -> str:
        """
        Shortens a string by the specified number of characters.

        Removes the given number of characters from the end of the string.

        Parameters
        ----------
        s : str
            The string that is to be shortened.

        n_chars : int
            The number of characters to remove from the end of the string.

        Returns
        -------
        str
            The shortened string.

        Notes
        -----
        If the number of characters to remove is larger than the number of
        characters in the string, an empty string is returned.

        """

        if len(s) > n_chars:
            return s[:-n_chars]

        return ''

    @classmethod
    def all_end_with_underscore_and_numbers(cls, lst: List[str]) \
            -> bool:
        """
        Checks if all strings in the list end with an underscore and numbers.

        Checks if all strings in the list end with an underscore followed by
        one or more numbers.

        Parameters
        ----------
        lst : List[str]
            List of strings to check.

        Returns
        -------
        bool
            True if all strings match the pattern, False otherwise.

        """

        pattern = re.compile(r"_\d+$")

        return all(pattern.search(s) for s in lst)

    @classmethod
    def get_str_before_last_underscore(cls, s: str) \
            -> str:
        """
        Returns the string before the last underscore in a string.

        Extracts the string before the last underscore using the
        get_int_behind_last_underscore method.

        Parameters
        ----------
        s : str
            The string from which to extract the part before the last
            underscore. The string must contain at least one underscore
            and a number as last part of the
            string, e.g. "attempt_1".

        Returns
        -------
        str
            The extracted string part.

        Raises
        ------
        CriticalException
            If the last part of the string cannot be converted into an integer.

        """

        nr: int = cls.get_int_behind_last_underscore(s)
        return s.replace(f"_{str(nr)}", "")

    @classmethod
    def get_first_sentence(cls, input_string: str) \
            -> str:
        """
        Extracts the first sentence from the provided input string.

        Parameters
        ----------
        input_string : str
            The string from which to extract the first sentence.

        Returns
        -------
        str
            The first sentence of the input string, or an empty string if no
            sentence is found.

        """

        if not input_string:
            return ""

        # Split the input string by '.', take the first part as the first
        # sentence.
        first_sentence = input_string.split('.')[0].strip()
        return first_sentence + '.' if first_sentence else ""

    @classmethod
    def get_int_behind_last_underscore(cls, s: str) \
            -> int:
        """
        Returns the number behind the last underscore in a string.

        Splits the string at the underscores and tries to convert the last part
        into an integer.

        Parameters
        ----------
        s : str
            The string from which to extract the integer number. The
            string must contain an underscore and a number as last part of the
            string, e.g. "attempt_1".

        Returns
        -------
        int
            The extracted integer value.

        Raises
        ------
        CriticalException
            If the last part of the string cannot be converted into an integer.

        """

        parts = s.split('_')
        try:
            return int(parts[-1])
        except ValueError as err:
            raise CriticalException(
                cls.logger,
                "%s cannot be converted into a number" % parts[-1]
            ) from err

    @classmethod
    def get_prefixes(cls, elements: List[str] | Series) \
            -> List[str]:
        """
        Extracts prefixes separated by underscores from strings.

        Returns the first part of each string in the provided list or Series,
        up to the first underscore.

        Parameters
        ----------
        elements : List[str] | Series
            List or Series of strings from which to extract the prefixes.

        Returns
        -------
        List[str]
            List of extracted prefixes.

        """
        prefixes = elements.str.split('_').str.get(0)
        return prefixes

    @classmethod
    def get_unique_prefixes(cls, elements: List[str] | Series) \
            -> Set[str]:
        """
        Extracts a list of unique prefixes from strings.

        Uses the get_prefixes function to extract all prefixes, then converts
        the list into a set containing each element only once.

        Parameters
        ----------
        elements : List[str] | Series
            List or Series of strings from which to extract the prefixes.

        Returns
        -------
        Set[str]
            A set of unique prefixes extracted from the elements.
            .
        """

        prefixes = cls.get_prefixes(elements)
        return set(prefixes)

    @classmethod
    def first_char_to_upper(cls, string: str) \
            -> str:
        """
        Converts the first character of a string to uppercase.

        Parameters
        ----------
        string : str
            The string to be converted.

        Returns
        -------
        str
            The converted string.

        Notes
        -----
        In contrast to the inbuilt "capitalize" method that converts the
        whole string to lower case before capitalizing the first character,
        this method leaves the characters in the string untouched and only
        capitalizes the very first character.

        """

        return string[0].upper() + string[1:]
