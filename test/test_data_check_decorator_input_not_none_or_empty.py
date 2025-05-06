"""
test_data_check_decorator_input_not_none_or_empty.py
"""
import pytest

from src.data_structures.my_data_frame import MyDataFrame
from src.decorators.data_check_decorators import input_not_none_or_empty


class TestClass:
    def __init__(self):
        self.logged_message = None

    def log(self, msg, level):
        self.logged_message = f"{level.upper()}: {msg}"

    @input_not_none_or_empty("Input data")
    def process_data(self, data):
        return f"Processed {data}"


def test_input_not_none_or_empty_valid_input():
    obj = TestClass()
    assert obj.process_data("test data") == "Processed test data"


def test_input_not_none_or_empty_empty_str_input():
    obj = TestClass()
    with pytest.raises(ValueError, match="Input data not found or empty!"):
        obj.process_data("")


def test_input_not_none_or_empty_empty_list_input():
    obj = TestClass()
    with pytest.raises(ValueError, match="Input data not found or empty!"):
        obj.process_data([])


def test_input_not_none_or_empty_empty_my_df_input():
    obj = TestClass()
    my_df = MyDataFrame()  # Assume this is empty or has no data
    with pytest.raises(ValueError, match="Input data not found or empty!"):
        obj.process_data(my_df)


def test_input_not_none_or_empty_none_input():
    obj = TestClass()
    with pytest.raises(ValueError, match="Input data not found or empty!"):
        obj.process_data(None)
