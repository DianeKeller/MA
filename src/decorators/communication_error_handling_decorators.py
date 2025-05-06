"""
error_handling_decorators.py
----------------------------
Version 1.0, updated on 2024-12-17

"""

import json
import sys
import traceback
from functools import wraps
from ssl import SSLError
from time import sleep
from typing import Callable, Dict, Any, Tuple

import requests
from httpcore import ReadTimeout
from requests.exceptions import ConnectionError
from urllib3.exceptions import ProtocolError, NewConnectionError

from logger import Logger
from src.decorators.error_handling_decorators import handle_error
from src.utils.e_mail import EMail
from src.utils.time_utils import current_date_time

MINUTE = 60


def handle_query_error(
        logger: Logger,
        err: Exception,
        msg: str,
        waiting_time: int
) -> None:
    """
    Parameters
    ----------
    logger : object
        The logger object used for logging.

    err : Exception
        The error that occurred.

    msg : str
        The error message to be logged and raised.

    waiting_time : int
        The number of seconds to wait before the program can be resumed.

    """
    err_type = get_error_type_as_string(err)
    err_traceback = get_traceback(err)

    # Compose detailed message from provided basic message
    detailed_msg = (f"{current_date_time()} - {err_type} - {msg} - "
                    f"Waiting {waiting_time} seconds before retrying."
                    f"Traceback: {err_traceback}")
    logger.info(detailed_msg)

    EMail().send(err_type, detailed_msg)
    sleep(waiting_time)
    EMail().send(
        "Continuing...",
        f"Resuming after {err_type}."
    )


def handle_key_error(
        logger: Logger,
        response: Dict[str, Any],
        err: Exception
) -> None:
    """
    Handles key errors when handling query errors.

    Handles different kinds of key errors that can be reported in an API's
    response to a query.

    Parameters
    ----------
    logger : object
        The logger object used for logging.

    response : Dict[str, Any]
        The query response reporting the key error.

    err : Exception
        The key error that occurred.

    """

    if response.get('error', '').startswith('Rate'):
        msg = "Waiting for rate limit to expire."
        handle_query_error(logger, err, msg, 63 * MINUTE)
        return

    if response.get('error', '') == 'Service Unavailable':
        msg = "Service unavailable"
        handle_query_error(logger, err, msg, 5 * MINUTE)
        return

    msg = "Unexpected KeyError"
    handle_query_error(logger, err, msg, 1 * MINUTE)


def get_error_type_as_string(err: Exception) \
        -> str:
    """
    Gets the error type from the exception formatting it as a string.
    """
    return type(err).__name__


def get_traceback(err: Exception) \
        -> str:
    """
    Gets the traceback from the exception formatting it as a string.
    """

    return ''.join(
        traceback.format_exception(
            type(err), value=err, tb=err.__traceback__
        )
    )


def analyze_connection_error(
        logger: Logger,
        err: Exception
) -> None:
    """
    Inspects the nested exception structure.

    Parameters
    ----------
    logger : object
        The logger object used for logging.

    err : Exception
        The connection error that occurred.

    """

    if isinstance(err.args[0], ProtocolError):
        nested_exception = err.args[0]

        if isinstance(nested_exception.args[1], ConnectionResetError):
            msg = "Caught ConnectionResetError within ProtocolError."
            handle_query_error(logger, err, msg, 5 * MINUTE)
            return

        msg = "Caught ProtocolError."
        handle_query_error(logger, err, msg, 5 * MINUTE)
        return

    if isinstance(err.args[0], NewConnectionError):
        msg = "Caught NewConnectionError."
        handle_query_error(logger, err, msg, 5 * MINUTE)
        return

    if isinstance(err.args[0], SSLError):
        msg = "Caught SSLError."
        handle_query_error(logger, err, msg, 5 * MINUTE)
        return

    msg = "Caught a general ConnectionError."
    handle_query_error(logger, err, msg, 5 * MINUTE)


def raise_unknown_exception(logger, err) \
        -> None:
    """
    Re-raises an exception with a custom error message and traceback.

    This method is called when an unexpected exception occurs. It logs the
    error message and raises a new exception with the original traceback.

    Parameters
    ----------
    logger

    err : Exception
        The original exception that was caught.

    """
    err_type, _, err_traceback = sys.exc_info()
    msg = "Unexpected error occurred"
    handle_error(logger, err, msg, err_type, err_traceback)

    new_exception = err_type(msg)  # type: ignore
    raise new_exception.with_traceback(err_traceback) from err


def query_error_handling(operation: Callable) \
        -> Callable:
    """
    Handles errors that occur when a query is sent to an API.

    Catches the errors, logs them and retries to execute the operation after
    some waiting time.

    Parameters
    ----------
    operation : Callable
        The function to be decorated, which sends a query to an API.

    Returns
    -------
    Callable
        A wrapped function that handles exceptions and retries the query.

    """

    @wraps(operation)
    def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) \
            -> Dict[str, Any]:

        max_retries = 5
        retry_delay = 60  # Initial deley in seconds

        for attempt in range(1, max_retries + 1):
            try:
                response = operation(self, *args, **kwargs)
                return response[0]

            except ConnectionError as err:
                analyze_connection_error(self.logger, err)
                retry_delay *= 2  # Exponential backoff

            except ProtocolError as err:
                msg = (
                    f"ProtocolError - Attempt {attempt} of {max_retries}. "
                    f"Retrying in {retry_delay} seconds."
                )
                handle_query_error(self.logger, err, msg, retry_delay)
                retry_delay *= 2  # Exponential backoff

            except ReadTimeout as err:
                msg = (
                    f"ReadTimeOutError - Attempt {attempt} of {max_retries}. "
                    f"Retrying in {retry_delay} seconds."
                )
                handle_query_error(self.logger, err, msg, retry_delay)
                retry_delay *= 2  # Exponential backoff

            except json.JSONDecodeError as err:
                msg = (
                    f"JSONDecodeError - Attempt {attempt} of {max_retries}. "
                    f"Retrying in {retry_delay} seconds."
                )
                handle_query_error(self.logger, err, msg, retry_delay)
                retry_delay *= 2  # Exponential backoff

            except SSLError as err:
                msg = (
                    f"SSLError - Attempt {attempt} of {max_retries}. "
                    f"Retrying in {retry_delay} seconds."
                )
                handle_query_error(self.logger, err, msg, retry_delay)
                retry_delay *= 2  # exponential backoff

            except Exception as err:  # pylint: disable=broad-except
                err_type, _, err_traceback = sys.exc_info()

                msg = f"FATAL: Unexpected error during communication: {err}"
                detailed_msg = (
                    f"{current_date_time()} - {err_type} - {msg} - "
                    f"{err_traceback}")
                EMail().send(str(err_type), detailed_msg)

                raise_unknown_exception(self.logger, err)

        raise requests.exceptions.ReadTimeout("Maximum retries reached.")

    return wrapper


def communication_error_handling(operation):
    """
    Handles communication-related errors with automatic retries and backoff.

    Handles communication-related errors that occur when sending requests
    to external APIs.

    The decorator wraps the given operation and handles specific
    communication-related errors, logging appropriate messages and retrying
    the operation with exponential backoff.

    """

    @wraps(operation)
    def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):

        max_retries = 5
        retry_delay = 60  # Initial deley in seconds

        for attempt in range(1, max_retries + 1):

            err_msg = (
                f"Attempt {attempt} of {max_retries}. Retrying in "
                f"{retry_delay} seconds."
            )

            try:
                return operation(self, *args, **kwargs)

            except ReadTimeout as err:
                msg = f"ReadTimeOutError - {err_msg}"
                handle_query_error(self.logger, err, msg, retry_delay)

            except requests.ConnectionError as err:
                msg = (
                    f"Connection error while communicating with the API. - "
                    f"{err_msg}")
                handle_query_error(self.logger, err, msg, retry_delay)

            except requests.Timeout as err:
                msg = f"The request to the API timed out. - {err_msg}"
                handle_query_error(self.logger, err, msg, retry_delay)

            except requests.RequestException as err:
                msg = f"Unexpected request-related error: - {err_msg}"
                handle_query_error(self.logger, err, msg, retry_delay)

            except Exception as err:  # pylint: disable=broad-except
                err_type, _, err_traceback = sys.exc_info()

                msg = f"FATAL: Unexpected error during communication: {err}"
                detailed_msg = (
                    f"{current_date_time()} - {err_type} - {msg} - "
                    f"{err_traceback}")
                EMail().send(str(err_type), detailed_msg)

                handle_error(self.logger, err, msg, err_type, err_traceback)

            # Exponential backoff
            retry_delay *= 2

        raise requests.exceptions.ReadTimeout("Maximum retries reached.")

    return wrapper
