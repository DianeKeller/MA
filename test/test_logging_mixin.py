"""
test_logging_mixin.py
"""

from unittest.mock import MagicMock, patch

import pytest

from logger import Logger
from src.logging_mixin import LoggingMixin  # Corrected import path

# Mock settings.DISALLOWED_MESSAGES
DISALLOWED_MESSAGES = [
    "disallowed_msg_id"
]


@pytest.fixture
def logging_mixin_instance():
    """
    Fixture to create an instance of a class inheriting from LoggingMixin.
    """

    class TestClass(LoggingMixin):
        def __init__(self):
            # Override the default logger of the 'LoggingMixin' class.
            self.logger = Logger(self.__class__.__name__).get_logger()

        def test_method(self):
            self._log("A test message", "info")

    return TestClass()


def test_log_method_calls_correct_logger_method(logging_mixin_instance):
    """
    Test that the correct logging method is called based on the level.
    """
    with patch.object(LoggingMixin.logger, 'info') as mock_info:
        LoggingMixin.log("Info message", "info")
        mock_info.assert_called_once_with("Info message")

    with patch.object(LoggingMixin.logger, 'error') as mock_error:
        LoggingMixin.log("Error message", "error")
        mock_error.assert_called_once_with("Error message")

    with patch.object(LoggingMixin.logger, 'warning') as mock_warning:
        LoggingMixin.log("Warning message", "warning")
        mock_warning.assert_called_once_with("Warning message")


def test_log_method_does_not_log_disallowed_message(logging_mixin_instance):
    """
    Test that a message with a disallowed msg_id is not logged.
    """
    with patch.object(LoggingMixin, '_is_disallowed',
                      return_value=True) as mock_is_disallowed:
        # Patch the logger to mock the 'info' logging method
        with patch.object(LoggingMixin.logger, 'info') as mock_info:
            # Attempt to log a message with a disallowed msg_id
            LoggingMixin.log("Should not log", "info",
                             msg_id="disallowed_msg_id")

            # Assert that the logging method was not called
            mock_info.assert_not_called()

            # Assert that _is_disallowed was called with the correct msg_id
            mock_is_disallowed.assert_called_once_with("disallowed_msg_id")


def test_log_method_logs_allowed_message(logging_mixin_instance):
    """
    Test that a message with an allowed msg_id is logged.
    """
    with patch.object(LoggingMixin.logger, 'info') as mock_info:
        LoggingMixin.log(
            "Should log",
            "info",
            msg_id="allowed_msg_id"
        )
        mock_info.assert_called_once_with("Should log")


def test_instance_log_method_includes_caller_name(logging_mixin_instance):
    """
    Test that the _log method includes the correct caller method name.
    """
    with patch.object(
            logging_mixin_instance.logger, 'info'
    ) as mock_info:
        logging_mixin_instance.test_method()
        mock_info.assert_called_once_with(
            "TestClass.test_method: A test message"
        )


def test_instance_log_method_does_not_log_disallowed_message(
        logging_mixin_instance
):
    """
    Test that the _log method does not log disallowed messages.
    """
    # Patch the DISALLOWED_MESSAGES in the settings module to include
    # "disallowed_msg_id"
    with patch(
            'src.logging_mixin.DISALLOWED_MESSAGES',
            {'disallowed_msg_id': 'This should not log'}
    ):
        # Patch the logger's info method to monitor if it gets called
        with patch.object(
                logging_mixin_instance.logger, 'info'
        ) as mock_info:
            # Attempt to log a message with a disallowed msg_id
            logging_mixin_instance._log(
                "This should not log",
                "info", "disallowed_msg_id"
            )

            # Ensure that the info method was not called since the message
            # is disallowed
            mock_info.assert_not_called()


def test_instance_log_method_logs_allowed_message(logging_mixin_instance):
    """
    Test that the _log method logs allowed messages.
    """
    with patch.object(
            logging_mixin_instance.logger, 'info'
    ) as mock_info:
        logging_mixin_instance._log(
            "This should log",
            "info",
            "allowed_msg_id"
        )
        mock_info.assert_called_once_with(
            "TestClass.test_instance_log_method_logs_allowed_message: "
            "This should log"
        )


def test_get_caller_name(logging_mixin_instance):
    """
    Test that _get_caller_name returns the correct caller method name.
    """
    # Patch inspect.stack directly
    with patch('inspect.stack') as mock_stack:
        # Mock the return value of inspect.stack to simulate the call stack
        mock_stack.return_value = [
            MagicMock(function='dummy_func'),
            # The _get_caller_name or _log function itself
            MagicMock(function='outer_func'),
            # The method that calls the method that calls _log
            MagicMock(function='test_method'),
            # The method that directly calls _log
        ]

        # Given the indexing, we expect _get_caller_name to return
        # 'test_method'
        caller_name = logging_mixin_instance._get_caller_name()
        assert caller_name == 'test_method'


def test_is_disallowed(logging_mixin_instance):
    """
    Test that _is_disallowed returns True for disallowed messages and False
    otherwise.
    """
    # Patch the DISALLOWED_MESSAGES in the settings module to include
    # "disallowed_msg_id"
    with patch(
            'src.logging_mixin.DISALLOWED_MESSAGES',
            {'disallowed_msg_id': 'Some disallowed message'}
    ):
        assert logging_mixin_instance._is_disallowed(
            "disallowed_msg_id"
        ) is True
        assert logging_mixin_instance._is_disallowed(
            "allowed_msg_id"
        ) is False
        assert logging_mixin_instance._is_disallowed("") is False
