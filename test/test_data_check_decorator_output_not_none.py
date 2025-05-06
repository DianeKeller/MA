"""
test_data_check_decorator_output_not_none.py
"""
import pytest

from src.data_structures.my_data_frame import MyDataFrame
from src.decorators.data_check_decorators import output_not_none


class TestClassWithNoneOutput:
    def __init__(self):
        self.logged_message = None

    def log(self, msg, level):
        self.logged_message = f"{level.upper()}: {msg}"

    @output_not_none("Result")
    def produce_output(self, data):
        return data


def test_output_not_none_valid_output():
    obj = TestClassWithNoneOutput()
    assert obj.produce_output("valid data") == "valid data"


def test_output_not_none_none_output():
    obj = TestClassWithNoneOutput()
    with pytest.raises(ValueError, match="Result is None!"):
        obj.produce_output(None)


def test_output_not_none_empty_str_output():
    obj = TestClassWithNoneOutput()
    assert obj.produce_output("") == ""


def test_output_not_none_empty_list_output():
    obj = TestClassWithNoneOutput()
    assert obj.produce_output([]) == []


def test_output_not_none_empty_my_df_output():
    obj = TestClassWithNoneOutput()
    my_df = MyDataFrame()
    assert obj.produce_output(my_df) == my_df
