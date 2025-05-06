"""
history.py
----------
Version 1.0, updated on 2025-05-01

"""

from typing import Dict

from src.serialization.data_serialization_mixin import DataSerializationMixin
from type_aliases import HistoryDataType


class History(DataSerializationMixin):
    """
    History class for storing and managing historical data.

    Attributes
    ----------
    data : HistoryDataType
        The historical data.

    file_name : str
        The name of the file in which to save the history.

    file_type : str
        The type of the file in which to save the history.

    name : str
        The name of the history.

    Methods
    -------
    add(entry: Dict[str, str]) -> None:
        Adds an entry to the history and saves it.

    contains(element: Dict[str, str]) -> bool:
        Checks whether the history already contains the element.

    get_nr(self, element: Dict[str, str]) -> int:
        Gets the index of the element in the history.

    reduce(self, limit: int) -> None:
        Reduces the length of the history to the maximum number of entries.

    """

    def __init__(
            self,
            data: HistoryDataType = None,
            name: str = ''
    ) -> None:
        """
        Initializes the History class with data and name.

        Parameters
        ----------
        data : HistoryDataType
            The initial data for the history (default is None).

        name : str
            The name of the history (default is '').

        """

        if data is None:
            data = []

        # Set the file type and file name for saving and loading the
        # previously processed data.
        self._data = data
        self._name = name

        self.file_name = self.name
        self.file_type = 'json'

        if self.can_load():
            self.load()

    # region --- Properties

    @property
    def name(self) \
            -> str:
        """
        Gets the name of the data.
        """

        return self._name

    @name.setter
    def name(self, name: str) \
            -> None:
        """
        Sets the name of the data.
        """

        self._name = name

    @property
    def data(self) \
            -> HistoryDataType:
        """
        Gets the data.
        """

        return self._data

    @data.setter
    def data(self, data: HistoryDataType) \
            -> None:
        """
        Sets the data.
        """

        self._data = data

    # endregion --- Properties

    # region --- Public Methods
    def add(self, entry: Dict[str, str]) \
            -> None:
        """
        Adds an entry to the history and saves it.

        Parameters
        ----------
        entry : Dict[str, str]
            The entry to add to the history.

        """

        self._data.append(entry)
        self.save()

    def contains(self, element: Dict[str, str]) -> bool:
        """
        Checks whether the history already contains the element.

        Parameters
        ----------
        element : Dict[str, str]
            The element to check.

        Returns
        -------
        bool
            True if the element is in the history, False otherwise.

        """

        return element in self._data

    def get_nr(self, element: Dict[str, str]) -> int:
        """
        Gets the index of the element in the history.

        Parameters
        ----------
        element : Dict[str, str]
            The element to find.

        Returns
        -------
        int
            The index of the element in the history.

        """

        return self._data.index(element)

    def get_entry(self, entry_nr: int) \
            -> Dict[str, str]:

        return self.data[entry_nr-1]

    def reduce(self, limit: int) -> None:
        """
        Reduces the length of the history to the maximum number of entries.

        Saves the history file.

        This method can be used to undo the adding of history entries after
        the intended number of prompts has already been reached.

        Parameters
        ----------
        limit : int
            The maximum number of entries.

        """

        if len(self._data) > limit:
            self._data = self._data[:limit]
            self.save()

    # endregion --- Public Methods
