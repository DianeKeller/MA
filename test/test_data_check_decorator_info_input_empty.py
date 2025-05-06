"""
test_data_check_decorator_info_input_empty.py
"""
from src.data_structures.my_data_frame import MyDataFrame
from src.decorators.data_check_decorators import info_input_empty


class TestClass:
    def __init__(self):
        self.logged_message = None

    def log(self, msg, level):
        self.logged_message = f"{level.upper()}: {msg}"

    def get_default_value(self) \
            -> str:
        return "default"

    @info_input_empty(
        "Processing input",
        on_empty=lambda self, input: self.get_default_value()
    )
    def process_input(self, data):
        return f"{data} processed."


def test_info_input_empty_valid_input():
    obj = TestClass()
    assert obj.process_input("valid data") == "valid data processed."


def test_info_input_empty_empty_str_input():
    obj = TestClass()
    result = obj.process_input("")
    assert result == "default processed."
    assert obj.logged_message == "INFO: Value is empty! Processing input"


def test_info_input_empty_empty_list_input():
    obj = TestClass()
    result = obj.process_input([])
    assert result == "default processed."
    assert obj.logged_message == "INFO: Value is empty! Processing input"


def test_info_input_empty_empty_my_df_input():
    obj = TestClass()
    my_df = MyDataFrame()  # Assume this is empty or has no data
    result = obj.process_input(my_df)

    # Adjust according to MyDataFrame behavior
    assert result == "default processed."
    assert obj.logged_message == "INFO: Value is empty! Processing input"
