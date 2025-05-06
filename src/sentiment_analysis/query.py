"""
query.py
--------
Version 1.0, updated on 2024-12-04

"""

from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.utils.data_utils import is_none_or_empty
from src.utils.string_utils import StringUtils


class Query(LoggingMixin):
    """
    Query class.

    This class serves to store and convert the different query identifiers a
    query might need to be assigned in the sentiment analysis workflow.
    
    """

    def __init__(
            self,
            col_name: str = "",
            nr: int = 0
    ):
        self._nr_with_version = ''
        self._nr: int = nr
        self._col_name: str = col_name

    # region --- Properties

    @property
    def col_name(self) \
            -> str:
        """
        Gets the name of the column in which is stored the query.

        Notes
        -----
        Usually, the column name is a string in the format: "query_x", where x
        is the integer query number.

        """
        return self._col_name

    @col_name.setter
    def col_name(self, col_name: str) \
            -> None:
        """
        Sets the name of the column in which is stored the query.
        """

        self._col_name = col_name

    @property
    def nr(self) \
            -> int:
        """
        Gets the integer number of the query.

        Notes
        -----
        The query numbers start with 1. If the number is 0, the property is
        not set yet.

        """

        if self._nr == 0:
            self._set_nr()
        return self._nr

    @nr.setter
    def nr(self, nr: int) \
            -> None:
        """
        Sets the integer number of the query.
        """

        self._nr = nr

    @property
    def nr_with_version(self) \
            -> str:
        """
        Gets the a string identifier with the version and the query number.

        Notes
        -----
        - The version and the query number are joined in a string with the
          format: "version_nr".

        - Adding the version to the query number accounts for the fact that
          queries with the same query numbers from different prompt
          engineering versions need to be distinguished when assembled
          together.

        """

        if is_none_or_empty(self._nr_with_version):
            self._set_nr_with_version()

        return self._nr_with_version

    @nr_with_version.setter
    def nr_with_version(self, nr_with_version: str) \
            -> None:
        """
        Sets the a string identifier with the version and the query number.
        """

        self._nr_with_version = nr_with_version

    # endregion --- Properties

    # region --- Public Methods

    # endregion --- Public Methods

    # region --- Protected Methods
    def _set_nr(self) \
            -> None:
        """
        Sets the query number.

        Extracts the query number from the column name of the query and sets
        the nr property.

        """

        if self._col_name:
            self.nr = StringUtils.get_int_behind_last_underscore(
                self._col_name
            )

    def _set_nr_with_version(self) \
            -> None:
        """
        Sets the nr_with_version property.

        """

        version = SentimentAnalysisConfig().get('version')
        self._nr_with_version = f"{version}_{self.nr}"

    # endregion --- Protected Methods
