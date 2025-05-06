"""
test_logger.py
"""

import importlib
import logging
import os
import tempfile
from logging.handlers import RotatingFileHandler

from logger import Logger
from settings import get_setting, SettingCategories, LOG_ROOT
from src.data_structures.my_dataframe_factory import MyDataFrameFactory


def test_logger_init():
    """
    Test logger initialization.

    Test whether the logger is initialized properly by checking if the name
    is correctly set.

    """

    logger_name = "test_logger"
    my_logger = Logger(logger_name).get_logger()
    assert my_logger.name == logger_name


def test_log_file():
    """
    Test whether the log file is created.

    Notes
    -----
    - The temporary directory and all its files will automatically be deleted
      when the 'with' block is exited. There is no need to delete the files and
      the directory manually.

    - The file handlers must be closed before assessing the existence of the
      log file, otherwise we get a permission error.

    """

    with tempfile.TemporaryDirectory() as temp_dir:
        log_file_name = "test.log"
        log_file_path = os.path.join(temp_dir, log_file_name)

        # Create log file in the temp directory and write message into it
        logger = Logger(__name__, log_file_path).get_logger()
        logger.info("Creating a log entry.")

        # Close file handlers
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)

        assert os.path.exists(log_file_path)


def test_rotating_file_handler_initialization():
    """
    Test whether the file handler attributes are correctly set.

    """

    logger = Logger(__name__).get_logger()
    file_handler_found = False

    for handler in logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            file_handler_found = True
            assert handler.maxBytes == get_setting(
                SettingCategories.LOG, 'SIZE')
            assert handler.backupCount == get_setting(
                SettingCategories.LOG, 'NR_BACKUPS')

    assert file_handler_found


def test_log_level():
    """
    Test whether the log level is correctly set.

    """

    logger = Logger(__name__).get_logger()
    expected_level = get_setting(SettingCategories.LOG, 'LEVEL')
    assert logger.level == expected_level


def test_log_entry():
    """
    Test whether the log file content is correctly created.

    Notes
    -----
    - The temporary directory and all its files will automatically be deleted
      when the 'with' block is exited. There is no need to delete the files and
      the directory manually.

    - The file handlers must be closed before accessing the
      log file, otherwise we get a permission error.

    - The test would fail if run together with the other test_logger test
      cases, even though it uses the context management provided by the logger
      class because writing to the log files is delayed by the other
      tests' operations. Therefore, logging needs to be shutdown and
      reloaded before the test.

    """
    # Make sure the logger will work independently of the other
    # test_logger test operations so that they do not delay the logger's
    # context management.

    logging.shutdown()
    importlib.reload(logging)

    with tempfile.TemporaryDirectory() as temp_dir:
        log_file_name = "output_test.log"
        log_file_path = os.path.join(temp_dir, log_file_name)

        # Use Logger as a context manager, ensuring that all handlers are
        # flushed and closed before the created log is accessed for reading.
        with Logger(__name__, log_file_path) as logger:
            # Create log file in the temp directory and write message into it
            test_message = "Test log message"
            logger.info(test_message)

        with open(log_file_path, 'r') as log_file:
            log_contents = log_file.read()
            assert test_message in log_contents


def test_production_logger():
    data = {'name': ['nnn', 'lll']}
    my_df = MyDataFrameFactory.create(data)

    assert os.path.exists(my_df.logger.handlers[0].baseFilename)


def test_log_settings_types():
    """
    Checks the data types of log settings so that they can be used in the
    creation of the file handler.

    """
    expected_path_type = str

    log_file_path = os.path.join(
        LOG_ROOT,
        f"name"
        f"{get_setting(SettingCategories.LOG, 'EXTENSION')}"
    )

    expected_type = int

    maxBytes = get_setting(SettingCategories.LOG, 'SIZE')
    backupCount = get_setting(SettingCategories.LOG, 'NR_BACKUPS')

    assert isinstance(log_file_path, expected_path_type)
    assert isinstance(maxBytes, expected_type)
    assert isinstance(backupCount, expected_type)
