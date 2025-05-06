"""
logger.py
---------
Version 1.0, updated on 2024-12-06

"""

import logging
import os
from logging.handlers import RotatingFileHandler

from settings import LOG_ROOT, get_setting, SettingCategories


class Logger:
    """
    This class provides logging for the entire application.

    This class provides a logger that can be used throughout the application.
    The logger prints log messages to the console and simultaneously stores
    them in log files for future reference.

    Additionally, the logger can be used as a context manager to ensure all
    handlers are properly flushed and closed before any log files are accessed
    for reading.

    Parameters
    ----------
    name : str
        The name of the logger. The name provided should make clear
        from which module the message comes from. Use '__name__' to pass
        the name of any module from which you call the logger.

    log_file_path : str | None
            The path where the log file should be stored, including the
            actual file name. If not provided, the path defaults to the
            LOG_ROOT defined in the settings file, the actual file name being
            taken from the name provided, adding the log file extension.

    Methods
    -------
    get_logger() -> logging.Logger:
        Returns the configured logger for logging messages.

    Examples
    --------

    .. code-block:: python

        - Simple logging:
          >>> from logger import Logger

          >>> logger = Logger(__name__, "/path/to/logfile.log").get_logger()
          >>> logger.info("This is an informational message")

        - As a context manager for outomatically flushing and closing the
          handlers after the logging has finished, i.e. when the 'while' block is
          exited:
          >>> from logger import Logger

          >>> with Logger(__name__, "app.log") as logger:
          ...     logger.info("This is an informational message")
          ...

    Notes
    -----
    - Constant logging parameters such as the log level, the maximum size
      of the log files, and the maximum number of log files of one kind to
      keep are stored in the settings for easy change.

    - Utilizing a RotatingFileHandler, the logger restricts the size of each
      log file and the total number of backup files retained, thereby
      conserving disk space by automatically overwriting the oldest files once
      these limits are reached.

    """

    def __init__(self, name: str, log_file_path: str | None = None) \
            -> None:
        """
        Configures and initializes the logger.

        """

        if log_file_path is None:
            log_file_path = os.path.join(
                LOG_ROOT,
                f"{name}"
                f"{get_setting(SettingCategories.LOG, 'EXTENSION')}"
            )

        self.logger = logging.getLogger(name)

        # Set default log level
        self.logger.setLevel(get_setting(
            SettingCategories.LOG,
            'LEVEL'
        ))

        # File handler for writing logs to a file
        # Getting the maxBytes and backupCount values from the settings

        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=int(get_setting(
                SettingCategories.LOG, 'SIZE')
            ),
            backupCount=int(get_setting(
                SettingCategories.LOG,
                'NR_BACKUPS'
            ))
        )
        file_handler.setLevel(logging.INFO)

        # Console handler for writing logs to the console
        # Debug messages are only output to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(get_setting(
            SettingCategories.LOG,
            'LEVEL'
        ))

        # Log message format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger if they do not already exist
        if not any(isinstance(handler, RotatingFileHandler)
                   for handler in self.logger.handlers):
            self.logger.addHandler(file_handler)

        # Isinstance does not work here for the StreamHandler type because
        # RotatingFileHandler is a subtype of Streamhandler. Therefore,
        # the handlers' __class__ variable is used for the check:
        if not any(handler.__class__ == logging.StreamHandler
                   for handler in self.logger.handlers):
            self.logger.addHandler(console_handler)

    def get_logger(self) \
            -> logging.Logger:
        """
        Returns the configured logger.

        This method provides access to the logger configured in the
        constructor, allowing it to be used for logging messages in the
        application.

        Returns
        -------
        logging.Logger
            The configured logger.

        Examples
        --------

        .. code-block:: python

            >>> from logger import Logger

            >>> logger = Logger(__name__).get_logger()
            >>> logger.debug("This is a debug message")
            >>> logger.error("This is an error message")

        """

        return self.logger

    def __enter__(self):
        """
        This method is automatically called if the logger is used as a
        context manager.

        To use the logger as a context manager, you need to use a 'with'
        block, the __enter__ method being executed when entering the block.

        Returns
        -------
        logging.Logger
            The configured logger.

        Examples
        --------

        .. code-block:: python

            >>> from logger import Logger

            >>> with Logger(__name__, "app.log") as logger:
            ...     logger.info("This is an informational message")
            ...

        """

        return self.get_logger()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        This method is automatically called when exiting the 'with' block.

        It ensures all handlers are properly flushed and closed.

        """

        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
