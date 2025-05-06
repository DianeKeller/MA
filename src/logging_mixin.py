"""
logging_mixin.py
----------------
Version 1.0, validated on 2024-12-04

"""

import inspect

from logger import Logger
from settings import DISALLOWED_MESSAGES


class LoggingMixin:
    """
    LoggingMixin class.

    This mixin class provides logging functionality to any class that
    inherits it.

    This mixin offers both class-level and instance-level logging methods with
    customizable logging levels. It also includes features to avoid logging
    specific messages the user wants to exclude from logging.

    Attributes
    ----------
    logger : logging.Logger
        A default logger that is used if the inheriting class does not define
        its own logger.

    Methods
    -------
    log(message: str, level: str = 'info', msg_id: str = '').
        Class method to log a message at the specified logging level. This
        method should be called from modules that do not present any class.

    _log(message: str, level: str = 'info', msg_id: str = '').
        Instance method to log a message at the specified logging level.
        This method should be called from classes that inherit from the mixin.

    """

    # Initialize a default logger to ensure a logger actually exists for
    # the methods to work in this mixin, even if none is initialized in the
    # inheriting class.

    logger = Logger("default_logger").get_logger()

    # region --- Public Methods
    @classmethod
    def log(cls, message: str, level: str = 'info', msg_id: str = ''):
        """
        Logs a message at the specified logging level.

        Public method to log messages at the specified level. This can be used
        both within class instances and statically from the class itself if
        no instance is available.

        This method is intended for direct use for logging without needing
        detailed contextual information like class or method names in the logs.

        Parameters
        ----------
        message : str
            The message to log.

        level : str
            The logging level ('debug', 'info', 'warning', 'error',
            'exception', 'critical'). Defaults to 'info'.

        msg_id : str
            Message identifier that can be used to identify the logging
            message, e.g. for use in the 'DISALLOWED_MESSAGES' list in the
            settings file. Defaults to an empty string.

        Examples
        --------

        .. code-block:: python

            >>> LoggingMixin.log("An informational message", "info")
            >>> LoggingMixin.log("An error message", "error", "err_msg_01")

        """

        # Do not log disallowed messages
        if msg_id and cls._is_disallowed(msg_id):
            return

        # Use the getattr function to dynamically get the logging method based
        # on 'level'. Default to self.logger.info if the level is not found.
        getattr(cls.logger, level, cls.logger.info)(message)

    # endregion --- Public Methods

    # region --- Protected Methods

    def _log(
            self,
            message: str,
            level: str = 'info',
            msg_id: str = ''
    ) -> None:
        """
        Utility method for logging messages with automatic inclusion of class
        and method names.

        Parameters
        ----------
        message : str
            The message to log.

        level : str
            The logging level ('debug', 'info', 'warning', 'error',
            'exception', 'critical'). Defaults to 'info'.

        msg_id : str
            Message identifier. Defaults to an empty string.

        Notes
        -----
        The foreseen levels correspond to the ones defined in the "logging"
        library used for logging. If another level name is provided,
        the logger will default to the 'info' level. This method
        uses the given level to dynamically select the appropriate logging
        method.

        Usage
        -----
        To use this method in a class, make the class inherit from
        'LoggingMixin' and initialize a 'logger' attribute to override the
        default logger initialized in the 'LoggingMixin' class.

        Examples
        --------

        Here is how to use the '_log' method within a class that inherits from
        "LoggingMixin":

        .. code-block:: python

            >>> from logger import Logger
            >>> from src.logging_mixin import LoggingMixin

            >>> class MyClass(LoggingMixin):
            ...     def __init__(self):
            ...         # Override the default logger of the 'LoggingMixin'
            ...         # class.
            ...         self.logger = Logger(
            ...             self.__class__.__name__
            ...         ).get_logger()
            ...
            ...     def some_method(self):
            ...         self._log("This is an info message.", "info")
            ...
            ...     def some_other_method(self):
            ...         try:
            ...            # do something
            ...         except Exception as err:
            ...            self._log(f"An error occurred: {err}.", "error")

        """

        # Do not log disallowed messages
        if self._is_disallowed(msg_id):
            return

        # Fetch the caller method's name
        method_name = self._get_caller_name()

        # Construct the full log message with class and method context
        full_message = f"{self.__class__.__name__}.{method_name}: {message}"

        # Explicitly log the constructed full message
        log_func = getattr(self.logger, level, self.logger.info)
        log_func(full_message)

    @staticmethod
    def _get_caller_name() \
            -> str:
        """
        Returns the name of the caller method for use in logging.

        Inspects the call stack to determine the name of the method that
        called the _log method.

        Returns
        -------
        str
            The name of the caller method.
        """

        # [2] gets the caller of the method that called _log
        return inspect.stack()[2].function

    @staticmethod
    def _is_disallowed(msg_id: str) \
            -> bool:
        """
        Returns whether the given message is disallowed.

        Looks up the message in the DISALLOWED_MESSAGES dictionary in the
        settings file.

        Parameters
        ----------
        msg_id : str
            Message identifier. Can be an empty string.

        Returns
        -------
        bool
            True if the message is disallowed, False otherwise.

        """

        return msg_id in DISALLOWED_MESSAGES

    # endregion --- Protected Methods
