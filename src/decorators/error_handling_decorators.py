"""
error_handling_decorators.py
----------------------------
Version 1.0, updated on 2024-12-15

"""

import sys
from functools import wraps
from typing import Dict, Any, Tuple

import pandas as pd

from src.sentiment_analysis.retrieval.custom_exceptions import handle_error


def save_error_handling(operation):
    """
    Handles errors that occur when saving data.

    The decorator wraps the given operation and handles specific file-related
    errors, logging appropriate messages.
    """

    @wraps(operation)
    def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        try:
            return operation(self, *args, **kwargs)

        except FileNotFoundError as err:
            msg = "Directory not found for %s!" % self.file.full_path
            handle_error(self.logger, err, msg)

        except PermissionError as err:
            msg = "Permission denied for writing to %s!" % self.file.full_path
            handle_error(self.logger, err, msg)

        except IsADirectoryError as err:
            msg = "No file, but a directory: %s" % self.file.full_path
            handle_error(self.logger, err, msg)

        except Exception as err:  # pylint: disable=broad-except

            err_type, _, err_traceback = sys.exc_info()

            msg = "Data could not be saved: %s" % (err,)
            handle_error(self.logger, err, msg, err_type, err_traceback)

        # Explicitly return None to make clear that the function does not
        # return anything in case of an error.
        return None

    return wrapper


def load_error_handling(operation):
    """
        Handles errors that occur when files are attempted to be loaded.

        Catches all file loading errors and logs them.

    """

    @wraps(operation)
    def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):

        try:
            return operation(self, *args, **kwargs)

        except FileNotFoundError as err:
            msg = "File not found: %s!" % self.file.full_path
            handle_error(self.logger, err, msg)

        except PermissionError as err:
            msg = "Permission denied for %s!" % self.file.full_path
            handle_error(self.logger, err, msg)

        except IsADirectoryError as err:
            msg = "No file, but a directory: %s" % self.file.full_path
            handle_error(self.logger, err, msg)

        except pd.errors.EmptyDataError as err:
            msg = "File is empty: %s" % self.file.full_path
            handle_error(self.logger, err, msg)

        except pd.errors.ParserError as err:
            msg = "Could not parse %s! No CSV format?" % self.file.full_path
            handle_error(self.logger, err, msg)

        except UnicodeDecodeError as err:
            msg = ("Could not decode %s! Wrong Unicode format?"
                   % self.file.full_path)
            handle_error(self.logger, err, msg)

        except Exception as err:  # pylint: disable=broad-except
            err_type, _, err_traceback = sys.exc_info()

            msg = ("Unexpected error loading file %s: %s!"
                   % (self.file.full_path, err))
            handle_error(self.logger, err, msg, err_type, err_traceback)

        # Explicitly return None to make clear that the function does not
        # return anything in case of an error.
        return None

    return wrapper


def delete_error_handling(operation):
    """
    Handles errors that occur when files are attempted to be deleted.

    Catches all file deletion errors and logs them.

    """

    @wraps(operation)
    def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):

        try:
            return operation(self, *args, **kwargs)

        except FileNotFoundError as err:
            msg = "File not found for deletion: %s" % self.file.full_path
            handle_error(self.logger, err, msg)

        except PermissionError as err:
            msg = ("Permission denied: Unable to delete file %s."
                   % self.file.full_path)
            handle_error(self.logger, err, msg)

        except IsADirectoryError as err:
            msg = ("Expected a file but found a directory: %s."
                   % self.file.full_path)
            handle_error(self.logger, err, msg)

        except OSError as err:
            msg = ("Error deleting file %s: %s"
                   % (self.file.full_path, err.strerror))
            handle_error(self.logger, err, msg)

        except Exception as err:  # pylint: disable=broad-except
            err_type, _, err_traceback = sys.exc_info()

            msg = ("Unexpected error occurred while attempting to delete file "
                   "%s: %s" % (self.file.full_path, err))
            handle_error(self.logger, err, msg, err_type, err_traceback)

        # Explicitly return None to make clear that the function does not
        # return anything in case of an error.
        return None

    return wrapper
