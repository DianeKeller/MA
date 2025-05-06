"""
data_serialization_mixin.py
---------------------------
Version 1.0, updated on 2025-05-01

This module provides a mixin class for data serialization, offering methods
to load, save, fetch and manage data with flexible authentication strategies.

"""

import os
import sys
from typing import TypeVar, Generic, Any, no_type_check

from src.authentication.authentication_strategy import AuthenticationStrategy
from src.authentication.authenticator import Authenticator
from src.authentication.no_authentication_strategy import (
    NoAuthenticationStrategy
)
from src.decorators.attribute_chain_decorators import (
    self_attribute_chain_not_none
)
from src.decorators.data_check_decorators import (
    output_not_none_or_empty,
    requires_property
)
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.serialization.serialization_factory import get_serializer
from src.serialization.serialization_strategy import SerializationStrategy
from src.serialization.serializer import Serializer
from src.utils.data_utils import is_none_or_empty

T = TypeVar('T')


class DataSerializationMixin(Generic[T], LoggingMixin):
    """
    DataSerializationMixin class.

    This mixin provides serialization capabilities for data. It provides
    methods to load, save and fetch data from various sources.

    It also serves as the context in a strategy pattern, allowing you to
    dynamically choose an authentication strategy at runtime for accessing
    specified online data sources.

    The mixin works with any authentication strategy that implements the
    AuthenticationStrategy interface, giving access to the authentication
    functionality of the given authentication strategy.

    Attributes
    ----------
    auth_strategy : AuthenticationStrategy
        The authentication strategy used to access the data.

    source : str
        The source from which the data can be fetched, typically a URL.

    file_type : str
        The type of file used for storing the data, e.g., 'csv', 'json', 'txt'.

    file_name : str
        The name of the data file, excluding the file extension.

    sub_dir : str
        The subdirectory where the data file is stored.

    original_file_name : str
        The original file name to use for fetching data, defaulting to the
        value of file_name if not explicitly set.

    serializer : Serializer
        The serializer instance used for data serialization and
        deserialization.

    Methods
    -------
    add_or_save() -> None:
        Saves the data locally, adding it to an existing file or saving it
        as a new file.

    authenticate() -> None:
        Authenticates the user with the given authentication strategy when
        fetching data from the online source.

    can_load() -> bool:
        Checks if the data can be loaded from the local storage.

    delete() -> None:
        Deletes the data file from the local storage.

    fetch() -> None:
        Fetches the data from the original online source, using the selected
        authentication strategy.

    load() -> None:
        Loads the data from the local storage, raising a ValueError if the
        loading fails.

    load_if_possible() -> None:
        Loads the data from the local storage if available, without
        attempting to fetch or save it.

    load_or_fetch_and_save() -> None:
        Tries to load the data from the local storage. If the data is not
        found locally, fetches it from its online source and saves it locally.

    save() -> None:
        Saves the data locally.

    """

    # Cache for storing loaded data {file_path: (data, last_modified_time)}
    _cached_data = {}

    # region --- Properties

    @property
    def auth_strategy(self) \
            -> AuthenticationStrategy | NoAuthenticationStrategy | None:
        """
        Returns the authentication strategy used to access the data.

        """

        if is_none_or_empty(getattr(self, '_auth_strategy', None)):
            raise CriticalException(
                self.logger,
                "Authentication strategy is not set."
            )

        return getattr(self, '_auth_strategy', None)

    @auth_strategy.setter
    def auth_strategy(
            self,
            value: AuthenticationStrategy | NoAuthenticationStrategy
    ) -> None:
        """
        Sets the authentication strategy used to access the data.

        """

        # Use setattr to set the attribute dynamically
        setattr(self, '_auth_strategy', value)

    @property
    def source(self) \
            -> str:
        """
        Returns the source of the data.

        The source is an external link to the data, e.g. an Url from which
        the data can be downloaded.

        """

        # Use getattr to get the attribute dynamically;
        # return None if it doesn't exist
        return getattr(self, '_source', '')

    @source.setter
    def source(self, value: str) \
            -> None:
        """
        Sets the source of the data.

        The source should be an external link to the data, e.g. an Url from
        which the data can be downloaded.

        """

        # Use setattr to set the attribute dynamically
        setattr(self, '_source', value)

    @property
    def file_type(self) \
            -> str:
        """
        Returns the file type of the data.

        The file type is a string describing the format of the data, e.g.
        'csv', 'json', 'txt'.

        """

        return getattr(self, '_file_type', '')

    @file_type.setter
    def file_type(self, value: str) \
            -> None:
        """
        Sets the file type of the data.

        The file type should be a string describing the format of the data,
        e.g. 'csv', 'json', 'txt'.

        Sets the serializer accordingly.

        """

        setattr(self, '_file_type', value)
        setattr(self, '_serializer', get_serializer(
            value,
            getattr(self, '_file_name', ''),
        ))

    @property
    def file_name(self) \
            -> str:
        """
        Returns the file name of the data.

        The file name is a string describing the name of the data file
        without the file extension.

        """

        return getattr(self, '_file_name', '')

    @file_name.setter
    def file_name(self, value: str) \
            -> None:
        """
        Sets the file name of the data.

        The file name should be a string representing the name of the data file
        without the file extension.

        """

        setattr(self, '_file_name', value)
        # Reset the serializer so that it needs to get the updated file name
        setattr(self, '_serializer', None)

    @property
    def sub_dir(self) \
            -> str:
        """
        Returns the subdirectory for the data.

        """

        return getattr(self, '_sub_dir', '')

    @sub_dir.setter
    def sub_dir(self, value: str) \
            -> None:
        """
        Sets the subdirectory of the data.

        The file name should be a string representing the name of the data file
        without the file extension.

        """

        setattr(self, '_sub_dir', value)
        # Reset the serializer so that it needs to get the updated file name
        setattr(self, '_serializer', None)

    @property
    def original_file_name(self) \
            -> str:
        """
        Returns the original file name of the data.

        Returns the file name which is to be used for fetching the data. If
        no special original file name is set, the normal file name is used.

        The file name is a string describing the name of the data file
        without the file extension.

        """

        if hasattr(self, 'get_original_file_name'):
            return self.get_original_file_name()

        return self.file_name

    @property
    def serializer(self) \
            -> Serializer:
        """
        Provides lazy initialization for the serializer instance to use for
        serialization.

        """

        if (
                not hasattr(self, '_serializer') or
                not getattr(self, '_serializer', None)
        ):
            if self.file_type is None or self.file_name is None:
                raise CriticalException(
                    self.logger,
                    (
                        "File_type and file_name must be set before accessing "
                        "the serializer."
                    )
                )

            serializer = get_serializer(
                file_type=self.file_type,
                file_name=self.file_name
            )

            if self.sub_dir:
                serializer.file.path = os.path.join(  # type: ignore
                    serializer.file.path,  # type: ignore
                    self.sub_dir
                )

            # Use setattr to set the attribute dynamically
            setattr(self, '_serializer', serializer)

        return getattr(self, '_serializer')

    @serializer.setter
    def serializer(self, strategy: SerializationStrategy) \
            -> None:
        """
        Sets the serializer.

        This setter normally is not needed since the serializer is computed
        from the file_type and file_name. It is only used for testing
        purposes, when a mock or temporary file path is needed.

        Parameters
        ----------
        strategy : SerializationStrategy
            The serialization strategy to be used by the serializer.

        """

        serializer = Serializer(strategy)

        # Use setattr to set the attribute dynamically
        setattr(self, '_serializer', serializer)

    @property
    def authenticator(self) \
            -> Authenticator:
        """
        Provides lazy initialization for the authenticator instance to use for
        authentication.

        """
        if (
                not hasattr(self, '_authenticator') or
                not getattr(self, '_authenticator', None)
        ):
            authenticator = Authenticator(self.auth_strategy)
            # Use setattr to set the attribute dynamically
            setattr(self, '_authenticator', authenticator)

        return getattr(self, '_authenticator')

    @authenticator.setter
    def authenticator(self, strategy: AuthenticationStrategy) \
            -> None:
        """
        Sets the authenticator.

        Parameters
        ----------
        strategy : AuthenticationStrategy
            The authentication strategy to be used by the authenticator.

        """

        authenticator = Authenticator(strategy)

        # Use setattr to set the attribute dynamically
        setattr(self, '_authenticator', authenticator)

    # endregion --- Properties

    # region --- Public Methods

    def authenticate(self) \
            -> None:
        """
        Authenticates with the authentication strategy.

        Authenticates with the authentication strategy if it is an instance
        of AuthenticationStrategy.

        Raises
        -------
        CriticalException
            If the authentication strategy is not set.

        Notes
        ------
        If the authentication strategy is an instance of
        NoAuthenticationStrategy, no authentication is performed.

        """

        self.authenticator.authenticate()

    def save(self) \
            -> None:
        """
        Saves the data locally and invalidates the cache.

        Saves the data locally and invalidates the cache to ensure new data
        is reloaded from disk.

        Raises
        ------
        CriticalException
            If the file path is not set.

        """

        self.serializer.save(self.data)

        # Invalidate the cache
        self._invalidate_cache()

    def delete(self) \
            -> None:
        """
        Deletes the data file.
        """

        self.serializer.delete()

    def add_or_save(self) \
            -> None:
        """
        Saves the data locally.

        Saves the data locally, adding it to an existing file or saving it
        as a new file.

        """

        self.serializer.add_or_save(self.data)

    def can_load(self) \
            -> bool:
        """
        Checks if the data can be loaded from the local storage location.

        Returns
        -------
        bool
            True if the data can be loaded, False otherwise.

        """

        return self.serializer.does_path_exist()

    @self_attribute_chain_not_none('serializer.file.full_path')
    def load(self) \
            -> None:
        """
        Loads the data from the cache or the local storage.

        Loads the data from the local storage if not already loaded and
        still valid.

        The loaded data is stored in the data structure of the object
        this mixin is attached to using the object's 'data' setter.

        Raises
        -------
        CriticalException
            If the data could not be loaded from cache or the local storage.

        Notes
        ------
        - As a precondition, the self_attribute_chain_not_none decorator is
          used to ensure that the serializer provides a file path for the
          load process.

        - The _load() method is used to allow for the output_not_none_or_empty
          decorator to check the data exists before assigning it to self.data.

        - The loading process will result in a data structure defined by
          the serialization strategy. As the data needs to be wrapped in the
          object this mixin is attached to, it is up to the 'data' setter of
          the object to convert the data to the correct type.

        """

        if self._load_from_cache():
            return

        # Else: File has been modified, load from the original source
        self.data = self._load()

        if is_none_or_empty(self.data):
            raise CriticalException(
                self.logger,
                "Failed to load data!"
            )

        # Cache the newly loaded data
        file_path = self.serializer.file.full_path

        self._cached_data[file_path] = (
            self.data, os.path.getmtime(file_path)
        )


    @no_type_check
    @requires_property("source", "auth_strategy")
    def fetch(self) \
            -> None:
        """
        Fetch data from the original source.

        This method uses the methods of the authentication strategy to
        authenticate the user and fetch the data from the original source.

        Raises
        -------
        CriticalException
            If the source is not set in this class.

        Exception
            If any other exception occurs when trying to fetch and save data
            from the original source.

        Notes
        ------
        The fetched data is not returned but stored in the data structure of
        the object this mixin is attached to.

        """

        try:
            # Different authentication methods depending on the source
            # Authentication is only required for instances of
            # AuthenticationStrategy.

            self.auth_strategy.source = self.source
            self.authenticate()

            # Different load methods depending on the source
            # Using the data setter of the class this mixin is mixed in to
            # ensure the data has the correct data type
            self.data = self.authenticator.fetch(
                file_name=self.original_file_name
            )

            if is_none_or_empty(self.data):  # type: ignore
                raise CriticalException(
                    self.logger,
                    "Loading from %s was not successful." % self.source
                )

        except Exception as err:

            err_type, _, err_traceback = sys.exc_info()

            msg = f"Unexpected error trying to fetch {self.source}: {err}"
            self._log(msg, "error")

            # Raise a new exception of the same type with enhanced message
            # Ensure the original traceback is preserved

            new_exception = err_type(msg)  # type: ignore

            raise new_exception.with_traceback(err_traceback) from err

    def load_or_fetch_and_save(self) \
            -> None:
        """
        Loads the data from their local storage location.

        If the data is not found locally, this method will call the
        'fetch' method to fetch the data from its online source and save it
        locally.

        The loaded data will be stored in the data structure of the object
        this mixin is attached to.

        """
        if self.can_load():
            DataSerializationMixin.load(self)

            if is_none_or_empty(self.data):
                self.fetch()
                self.save()

        else:
            self.fetch()
            self.save()

    def load_if_possible(self) \
            -> None:
        """
        Loads the data from their local storage location.

        If the data is not found locally, this method will do nothing,
        leaving it to the caller to decide how to proceed further.

        Notes
        ------
        The loaded data is not returned but stored in the data structure of
        the object this mixin is attached to.

        """

        if self.can_load():
            DataSerializationMixin.load(self)

    # endregion --- Public Methods

    # region --- Protected Methods

    @self_attribute_chain_not_none('serializer.file.full_path')
    def _invalidate_cache(self) \
            -> None:
        """
        Invalidates the cache to ensure new data is reloaded from disk.

        """

        file_path = self.serializer.file.full_path

        if file_path in self._cached_data:
            del self._cached_data[file_path]
            self._log(
                f"Cache invalidated for {file_path} after saving.",
                "info"
            )

    @output_not_none_or_empty("Cannot load data")
    def _load(self) \
            -> Any:
        return self.serializer.load()

    def _load_from_cache(self) \
            -> bool:
        """
        Load existing data from the cache if it is still valid.

        Returns
        -------
        bool
            True if the data was loaded from the cache, False otherwise.

        """

        file_path = self.serializer.file.full_path

        # Check if the data has already been loaded and is still valid.
        if file_path in self._cached_data:
            cached_data, last_load_time = self._cached_data[file_path]
            file_modified_time = os.path.getmtime(
                file_path) if os.path.exists(
                file_path) else None

            # Check if the data is still valid
            if file_modified_time == last_load_time:
                self.data = cached_data  # Use cached data
                msg = f"Using cached data for {file_path}"
                self._log(msg, "info", "Using cached data")
                return True

        return False

    # endregion --- Protected Methods
