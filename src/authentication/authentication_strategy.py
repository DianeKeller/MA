"""
authentication_strategy.py
--------------------------
Version 1.0, updated on 2024-12-01

"""

from abc import abstractmethod, ABC
from typing import Any

from logger import Logger
from src.logging_mixin import LoggingMixin


class AuthenticationStrategy(ABC, LoggingMixin):
    """
    AuthenticationStrategy class.

    Abstract base class for all authentication strategies.

    This class serves as an interface that declares common operations
    for all authentication strategies. Specifically, it defines the essential
    operations for authenticating the user and fetching data, which concrete
    strategies must implement. Within the framework of a strategy pattern,
    this design enables a dynamic change of authentication strategies
    according to the varying requirements of different data sources.

    """

    def __init__(
            self,
            source: str = ""
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the AuthenticationStrategy class.

        Parameters
        ----------
        source : str
            The path of the source from where the data is to be fetched.
            Defaults to an empty string. If not provided,
            the concrete strategy implementations must ensure that a source is
            provided before attempting any authentication or data fetching.

        """
        self.__source: str = source

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    # region --- Properties

    @property
    def source(self) \
            -> str:
        """
        Gets the source path.

        Returns
        -------
        str
            The source path string.

        Notes
        -----
        As the source might not have been provided at the moment of the
        initialization of the class, it might have defaulted to an empty
        string. Therefore, this method might return an empty string.

        """

        return self.__source

    @source.setter
    def source(self, source: str) \
            -> None:
        """
        Sets the source path.

        Parameters
        ----------
        source : str
            The source path string.

        """

        self.__source = source

    # endregion --- Properties

    # region --- Methods

    def authenticate(self) \
            -> None:
        """
        Authenticates the user using the concrete strategy.
        """
        try:
            self._log_info_before_authentication()
            self._authenticate()
            self._log_info_after_authentication()
            return

        except Exception as err:
            self._log_error_after_authentication_attempt(err)
            raise

    def fetch(self, **kwargs: Any) \
            -> Any:
        """
        Fetches data from the source using the concrete strategy.
        """
        try:
            self._log_info_before_fetching_data()
            data = self._fetch(**kwargs)
            self._log_info_after_fetching_data()
            return data

        except Exception as err:
            self._log_error_after_fetching_attempt(err)
            raise

    # endregion --- Methods

    # region --- Abstract Methods

    @abstractmethod
    def _authenticate(self) \
            -> None:
        """
        Actual authentication logic, to be implemented by subclasses.
        """

    @abstractmethod
    def _fetch(self, **kwargs: Any) \
            -> None:
        """
        Actual fetching logic, to be implemented by subclasses.
        """

    # endregion --- Abstract Methods

    # region --- Protected Methods

    def _log_info_before_authentication(self):
        msg = (f"Logging in at "
               f"{self.source}...")
        self._log(msg, 'info')

    def _log_info_after_authentication(self):
        msg = (f"Successfully logged in at "
               f"{self.source}...")
        self._log(msg, 'info')

    def _log_error_after_authentication_attempt(self, err):
        msg = (f"Could not log in at "
               f"{self.source}! Error: {err}")
        self._log(msg, 'error')

    def _log_info_before_fetching_data(self):
        msg = (f"Fetching data from "
               f"{self.source}...")
        self._log(msg, 'info')

    def _log_info_after_fetching_data(self):
        msg = (f"Data successfully fetched from "
               f"{self.source}...")
        self._log(msg, 'info')

    def _log_error_after_fetching_attempt(self, err):
        msg = (f"Could not fetch data from "
               f"{self.source}! Error: {err}")
        self._log(msg, 'error')

    # endregion  --- ProtectedMethods
