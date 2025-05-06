"""
test_data_check_decorator_info_output_empty.py
"""

from src.data_structures.my_data_frame import MyDataFrame
from src.decorators.data_check_decorators import info_output_empty


class TestClassWithEmptyOutput:
    def __init__(self):
        self.logged_message = None

    def log(self, msg, level):
        self.logged_message = f"{level.upper()}: {msg}"

    @info_output_empty(
        "Output is empty",
        on_empty=lambda self, return_value, *args: setattr(
            self,
            'logged_message',
            'Empty output handled'
        )
    )
    def produce_output(self, data):
        return data


def test_info_output_empty_valid_output():
    obj = TestClassWithEmptyOutput()
    assert obj.produce_output("valid data") == "valid data"


def test_info_output_empty_empty_str_output():
    obj = TestClassWithEmptyOutput()
    result = obj.produce_output("")
    assert result == ""
    assert obj.logged_message == "Empty output handled"


def test_info_output_empty_empty_list_output():
    obj = TestClassWithEmptyOutput()
    result = obj.produce_output([])
    assert result == []
    assert obj.logged_message == "Empty output handled"


def test_info_output_empty_empty_my_df_output():
    obj = TestClassWithEmptyOutput()
    my_df = MyDataFrame()
    result = obj.produce_output(my_df)
    assert result == my_df
    assert obj.logged_message == "Empty output handled"
