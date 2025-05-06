"""
custom_exceptions.py
--------------------
Version 1.0, updated on 2024-12-13

This module provides custom exceptions that may be raised in the sentiment
retrieval process to control the process workflow.

"""

from types import TracebackType
from typing import Type, Dict

from logger import Logger


def handle_error(
        logger: Logger,
        err: Exception,
        msg: str,
        err_type: Type[BaseException] = None,
        err_traceback: TracebackType = None,
        recursive: bool = False
) -> None:
    """
    Handle the error and raise the same type of error with the given
    message.

    Parameters
    ----------
    logger : object
        The logger object used for logging.

    err : Exception
        The original error that occurred.

    msg : str
        The error message to be logged and raised.

    err_type : Type[BaseException]
        The type of error that occurred. The default is None.

    err_traceback : TracebackType
        The traceback of the error. The default is None.

    recursive : bool
        Whether recursion has occurred. If True, the function will
        raise an error to prevent infinite recursion.

    """

    if logger is None:
        logger = Logger(__name__).get_logger()

    logger.error(msg)

    if recursive:
        # Avoid further recursion by raising the error as-is
        raise err

    if err_type is None:
        err_type = type(err)  # Use the type of the original exception

    if issubclass(err_type, CriticalException):
        # Pass recursive=True to prevent nested calls
        new_exception = CriticalException(logger=logger, msg=msg, do_log=False)

    else:
        if err_type is None:
            err_type = type(err)
        if err_traceback:
            new_exception = err_type(msg).with_traceback(err_traceback)
        else:
            new_exception = err_type(msg)

    raise new_exception from err


class BatchFinishedException(Exception):
    """
    Exception to handle the switch to the next batch.
    """


class PromptInvalidException(Exception):
    """
    Exception to handle invalid prompts.

    Notes
    -----
    This custom exception is used in the QueryColumnProcessor and in the
    ServerlessBloomPromptValidationMixin class.

    """



class ChunkFinishedException(Exception):
    """
    Exception to handle the switch to the next chunk.
    """


class LanguageFinishedException(Exception):
    """
    Exception to handle the switch to the next language.
    """


class CancelledByUserException(Exception):
    """
    Exception raised when the user cancels an operation.
    """

    def __init__(self, msg="Operation cancelled by the user."):
        self.msg = msg
        super().__init__(self.msg)


class CriticalException(ValueError):
    """
    ValueError exception that cannot be caught gracefully.
    """

    def __init__(self, logger=None, msg="ValueError.", do_log=True,
                 recursive=False):
        """
        Parameters
        ----------
        logger : Logger
            A logger instance. If provided and log_message is True,
            logs the message. Defaults to None.
        msg : str
            The exception message.
        do_log : bool
            If True, logs the message using the logger. Default is True.
        recursive : bool
            Whether this is a recursive instantiation to prevent re-calling
            handle_error.

        """

        if logger and do_log:
            handle_error(
                logger,
                self,
                f"CRITICAL: {msg}",
                recursive=recursive
            )

        super().__init__(msg)
