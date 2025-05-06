"""
test_check_attribute_chain.py
"""

import pytest

from logger import Logger
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException)
from src.decorators.attribute_chain_decorators import _check_attribute_chain


class C:
    def __init__(self):
        self.c = 1


class B:
    def __init__(self):
        self.b = C()


class MockLogger(Logger):
    def __init__(self):
        super().__init__("mock")
        self.messages = []

    def error(self, message):
        self.messages.append(message)


class TestObject:
    def __init__(self):
        self.a = B()


def test_check_attribute_chain_valid():
    obj = TestObject()
    assert _check_attribute_chain(
        obj,
        'a.b.c',
        'Attribute chain is not valid'
    ) is True


def test_check_attribute_chain_invalid(monkeypatch):
    # Create a mock logger
    mock_logger = MockLogger()

    # Patch the Logger class used in handle_error
    monkeypatch.setattr(
        "src.decorators.attribute_chain_decorators.Logger.get_logger",
        lambda *args, **kwargs: mock_logger)

    monkeypatch.setattr(
        "src.sentiment_analysis.retrieval.custom_exceptions.Logger"
        ".get_logger",
        lambda *args, **kwargs: mock_logger
    )

    obj = TestObject()

    # Test exception handling
    with pytest.raises(CriticalException) as excinfo:
        _check_attribute_chain(
            obj,
            'a.b.x',
            'Attribute chain is not valid.'
        )

    assert ("Attribute chain is not valid. Attribute 'x' "
            "of chain 'a.b.x' is missing or None.") in str(excinfo.value)

    # Verify that the logger captured the expected error message
    assert mock_logger.messages == [
        "CRITICAL: Attribute chain is not valid. Attribute 'x' of chain "
        "'a.b.x' is "
        "missing or None."
    ]