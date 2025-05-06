"""
hugging_face_strategy.py
------------------------
Version 1.0, updated on 2024-12-15

"""

import os
from typing import Dict, Any, List

import datasets
import requests
from datasets import DatasetDict
from huggingface_hub import login

from src.authentication.authentication_strategy import AuthenticationStrategy
from src.decorators.data_check_decorators import requires_property
from src.decorators.communication_error_handling_decorators import \
    communication_error_handling


class HuggingFaceStrategy(AuthenticationStrategy):
    """
    This class provides authentication and data fetching methods for
    HuggingFace.

    It is a concrete implementation of the AuthenticationStrategy
    interface.

    Methods
    -------
    authenticate()
        Login to HuggingFace.

    fetch(**kwargs: Any)
        Fetch data from HuggingFace.

    """

    def __init__(self):
        super().__init__()
        self.__access_token = os.getenv('HUGGING_FACE_AUTH_TOKEN')

    # region --- Public Methods

    @communication_error_handling
    def query(self, api, payload) \
            -> List[Dict[str, Any]]:
        """
        Sends a query to a Hugging Face and returns the response JSON.

        Sends a query to a Hugging Face inference API and returns the
        response JSON data.

        Returns
        -------
        List[Dict[str, Any]]

        """
        headers = {"Authorization": f"Bearer {self.__access_token}"}

        response = requests.post(
            api, headers=headers, json=payload, timeout=60
        )

        return response.json()

    # endregion --- Public Methods

    # region --- Protected Methods

    @requires_property('__access_token')
    def _authenticate(self) \
            -> None:
        """
        Login to HuggingFaceStrategy.

        Uses local environment variable 'HUGGING_FACE_AUTH_TOKEN' to
        authenticate the user for login to HuggingFaceStrategy.

        Raises
        ------
        CriticalException
            If the environment variable is not set or not found or is invalid.

        """

        login(token=self.__access_token)

    def _fetch(self, **kwargs: Any) \
            -> DatasetDict:
        data = datasets.load_dataset(self.source)
        return data

    # endregion --- Protected Methods
