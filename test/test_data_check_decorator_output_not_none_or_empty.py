"""
test_data_check_decorator_output_not_none_or_empty.py
"""

import pytest

from src.data_structures.my_data_frame import MyDataFrame
from src.decorators.data_check_decorators import output_not_none_or_empty


class TestClassWithOutput:
    def __init__(self):
        self.logged_message = None

    def log(self, msg, level):
        self.logged_message = f"{level.upper()}: {msg}"

    @output_not_none_or_empty("Result")
    def produce_output(self, data):
        return data


def test_output_not_none_or_empty_valid_output():
    obj = TestClassWithOutput()
    assert obj.produce_output("valid data") == "valid data"


def test_output_not_none_or_empty_empty_str_output():
    obj = TestClassWithOutput()
    with pytest.raises(ValueError, match="Result not found or empty!"):
        obj.produce_output("")


def test_output_not_none_or_empty_empty_list_output():
    obj = TestClassWithOutput()
    with pytest.raises(ValueError, match="Result not found or empty!"):
        obj.produce_output([])


def test_output_not_none_or_empty_empty_my_df_output():
    obj = TestClassWithOutput()
    my_df = MyDataFrame()
    with pytest.raises(ValueError, match="Result not found or empty!"):
        obj.produce_output(my_df)


def test_output_not_none_or_empty_none_output():
    obj = TestClassWithOutput()
    with pytest.raises(ValueError, match="Result not found or empty!"):
        obj.produce_output(None)
