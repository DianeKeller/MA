"""
test_data_check_decorator_requires_property.py
"""
import pytest

from src.decorators.data_check_decorators import requires_property


class TestClassWithProperty:
    def __init__(self, attr=None):
        self.attr = attr
        self.attr_1 = attr
        self.attr_2 = attr
        self.logged_message = None

    def log(self, msg, level):
        self.logged_message = f"{level.upper()}: {msg}"

    @requires_property("attr")
    def use_attr(self):
        return f"Using {self.attr}"

    @requires_property("attr_1", "attr_2")
    def use_multiple_attrs(self):
        return f"Using {self.attr_1}, {self.attr_2}"


def test_requires_property_set_attr():
    obj = TestClassWithProperty(attr="value")
    assert obj.use_attr() == "Using value"


def test_requires_property_multiple_attrs():
    obj = TestClassWithProperty(attr="value")
    assert obj.use_multiple_attrs() == "Using value, value"


def test_requires_property_missing_attr():
    obj = TestClassWithProperty(attr=None)
    with pytest.raises(ValueError, match="Attr is not set. Cannot proceed."):
        obj.use_attr()
