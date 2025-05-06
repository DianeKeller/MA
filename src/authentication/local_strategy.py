"""
local_strategy.py
-----------------
Version 1.0, updated on 2024-12-01

"""

import os
from typing import Any

from pandas import DataFrame

from src.authentication.authentication_strategy import AuthenticationStrategy
from src.serialization.serialization_factory import get_serializer
from src.serialization.serializer import Serializer


class LocalStrategy(AuthenticationStrategy):
    """
    This class provides data fetching methods for locally stored files.

    It is a concrete implementation of the AuthenticationStrategy
    interface.

    """

    def __init__(self, file_type: str = 'xls'):
        """
        Initializes a new instance of the LocalStrategy class with a file type.

        Parameters
        ----------
        file_type : str
            The file type of the local file.

        """

        super().__init__()

        self.file_type = file_type

    # region --- Properties

    @property
    def serializer(self) \
            -> Serializer:
        """
        Returns the serializer that must be set in this strategy to load the
        data from the local file.

        Returns
        -------
        Serializer
            The serializer for loading the data from the local file.

        """

        if getattr(self, '_serializer', None) is None:
            setattr(self, '_serializer', get_serializer(
                file_type=self.file_type, file_name=''
            ))

        return getattr(self, '_serializer')

    @serializer.setter
    def serializer(self, serializer: Serializer) \
            -> None:
        setattr(self, '_serializer', serializer)

    # endregion --- Properties

    # region --- Methods

    def _authenticate(self) \
            -> None:
        """
        This method implements the abstract method of the
        AuthenticationStrategy interface.

        """

        msg = 'No authentication needed...'
        self._log(msg, 'info')

    def _fetch(self, **kwargs: Any) \
            -> DataFrame:
        """
        This method implements the abstract method of the
        AuthenticationStrategy interface.

        """

        self._set_serializer(**kwargs)
        data = self._load()

        return data

    def _load(self):
        return self.serializer.load()

    def _set_serializer(self, **kwargs: Any) \
            -> None:
        file_name = str(kwargs.get('file_name'))
        file_type = self.file_type

        serializer: Serializer = get_serializer(
            file_type=file_type,
            file_name=file_name
        )

        if serializer is None or serializer.file is None:
            msg = "Serializer cannot be set for file %s of type %s" \
                  % (file_name, file_type)
            self._log(msg, 'error')
            raise FileNotFoundError(msg)

        serializer.file.path = os.path.join(serializer.file.path, self.source)

        self.serializer = serializer

    # endregion --- Methods
