"""
test_attribute_chain_decorators.py
"""

import pytest

from src.decorators.attribute_chain_decorators import \
    output_attribute_chain_not_none, input_attribute_chain_not_none


class Profile:
    def __init__(self, name=None):
        self.name = name


class User:
    def __init__(self, profile=None):
        self.profile = profile


class DummyClass:
    def __init__(self):
        # Initialize the nested objects
        self.user = User(Profile("John"))

    @output_attribute_chain_not_none("Output attribute chain is not valid.",
                                     'profile.name')
    def test_method(self):
        # Return the root object from which the chain will be evaluated
        return self.user

    @input_attribute_chain_not_none("Input attribute chain is not valid",
                                    'profile.name')
    def test_input_method(self, input_data):
        return "Input is valid"


def test_output_attribute_chain_decorator():
    dummy = DummyClass()
    user = dummy.test_method()
    assert user.profile.name == 'John'


def test_output_attribute_chain_decorator_failure():
    dummy = DummyClass()
    # Invalidate an attribute in the chain to trigger the error
    dummy.user.profile.name = None
    with pytest.raises(ValueError):
        dummy.test_method()


def test_input_attribute_chain_decorator():
    dummy = DummyClass()
    # Properly initialized input object for the test
    input_data = User(Profile("John"))
    assert dummy.test_input_method(input_data) == "Input is valid"


def test_input_attribute_chain_decorator_failure():
    dummy = DummyClass()
    # Invalidate an attribute in the input data to trigger the error
    input_data = User(Profile(None))
    with pytest.raises(ValueError):
        dummy.test_input_method(input_data)
