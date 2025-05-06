"""
no_authentication_strategy.py
-----------------------------
Version 1.0, updated on 2024-12-17

"""
from typing import Any

from src.authentication.authentication_strategy import AuthenticationStrategy


class NoAuthenticationStrategy(AuthenticationStrategy):
    """
    NoAuthenticationStrategy class.

    This class is a concrete implementation of the AuthenticationStrategy
    interface. It is used for fetching data from an external source when no
    authentication is required.

    """

    def __init__(
            self,
            source: str = ""
    ) -> None:
        """
        Constructor.

        Initializes the NoAuthenticationStrategy class with the source path.

        Parameters
        ----------
        source : str
            The path of the source from where the data is to be fetched.
            Defaults to an empty string.


        """
        super().__init__(source)

    def _authenticate(self) -> None:
        """
        No authentication needed for this strategy.
        """

        print("No authentication required.")

    def _fetch(self, **kwargs: Any) \
            -> Any:
        """
        Fetch data without authentication.
        """

        print(f"Fetching data from {self.source} without authentication.")

        raise NotImplementedError
