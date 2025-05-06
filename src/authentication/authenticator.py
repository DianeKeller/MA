"""
authenticator.py
----------------
Version 1.0, updated on 2024-11-10

"""
from typing import Any

from logger import Logger

from src.authentication.authentication_strategy import AuthenticationStrategy
from src.authentication.local_strategy import LocalStrategy
from src.logging_mixin import LoggingMixin


class Authenticator(LoggingMixin):
    """
    This class serves as the context in a strategy pattern, which allows you to
    dynamically choose an authentication strategy at runtime.

    The class works with any of the authentication strategies that implement
    the AuthenticationStrategy interface. It gives access to authentication
    methods such as authenticating the user and fetching data from an
    external or local source.

    """

    def __init__(self, my_strategy: AuthenticationStrategy | None = None) \
            -> None:
        """
        Constructor.

        Sets the authentication strategy which is supposed to be used for
        accessing data. If no strategy is specified when the
        serializer is called, a default authentication strategy is used.

        Parameters
        ----------
        my_strategy : AuthenticationStrategy | None
            The authentication strategy to be used. Default value: None.

        """

        # Override the default logger of the 'LoggingMixin' class.
        self.logger: Logger = Logger(self.__class__.__name__).get_logger()

        self._strategy = my_strategy or self.default_strategy()
        self.__source = self.strategy.source

    # region --- Properties

    @property
    def strategy(self) -> AuthenticationStrategy:
        """
        Gets the current authentication strategy.

        Returns
        -------
        AuthenticationStrategy
            The authentication strategy currently in use.

        """

        return self._strategy

    @strategy.setter
    def strategy(self, strategy: AuthenticationStrategy) \
            -> None:
        """
        Sets the authentication strategy to be used.

        The strategy can be changed at runtime.

        Parameters
        ----------
        strategy : AuthenticationStrategy
            The authentication strategy to be used for fetching data.

        """

        self._strategy = strategy

    @property
    def source(self) \
            -> str:
        """
        Gets the source path.

        Returns
        -------
        source : str
            the source path of the data in string format.

        Notes
        -----
        As the source might not have been provided at the moment of
        the initialization of the strategy, it might have defaulted to an
        empty string. Therefore, this method might return an empty string.

        """

        return self.__source

    # endregion --- Properties

    # region --- Public Methods
    def authenticate(self) -> None:
        """
        Delegate authentication to the strategy.
        """
        self._strategy.authenticate()

    def fetch(self, **kwargs: Any) \
            -> Any:
        """
        Delegate fetching to the strategy.
        """

        return self._strategy.fetch(**kwargs)

    # endregion --- Public Methods

    # region --- Static Methods

    @staticmethod
    def default_strategy() \
            -> AuthenticationStrategy:
        """
        Returns the default authentication strategy.

        As default, the local strategy is used. Data will be fetched from a
        local source.

        Returns
        -------
        AuthenticationStrategy
            The default authentication strategy.

        Notes
        -----
        This method is used instead of a class constant to ensure lazy
        instantiation. This approach avoids the overhead of creating a default
        strategy object until it is actually needed.

        """

        return LocalStrategy("")

    # endregion --- StaticMethods

    # region --- Protected Methods

    # endregion --- Protected Methods
