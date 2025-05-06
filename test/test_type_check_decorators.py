"""
test_type_check_decorators.py
"""

from collections import OrderedDict

import pytest
from pandas import DataFrame

from src.data_structures.my_data_frame import MyDataFrame
from src.decorators.type_check_decorators import enforce_input_types, \
    enforce_output_types
from src.utils.data_comparison_utils import are_equal


class TestClass:
    @enforce_input_types
    def method_with_input_types(self, a: int, b: str) -> str:
        return f"{a}, {b}"

    @enforce_output_types
    def method_with_output_types(self, a, b) -> int:
        return a + b

    @enforce_input_types
    def method_with_complex_input_types(
            self, a: MyDataFrame,
            b: OrderedDict
    ) -> DataFrame:
        return a.df

    @enforce_output_types
    def method_with_complex_output_type(
            self, a: MyDataFrame,
            b: OrderedDict
    ) -> DataFrame:
        return a.df

    @enforce_output_types
    def method_with_complex_wrong_output_type(
            self, a: MyDataFrame,
            b: OrderedDict
    ) -> DataFrame:
        return a

    @enforce_input_types
    @enforce_output_types
    def method_with_input_and_output_types(
            self, a: MyDataFrame,
            b: OrderedDict
    ) -> DataFrame:
        return a.df


def test_enforce_input_types_correct_types():
    obj = TestClass()
    # This should pass without any exception
    assert obj.method_with_input_types(1, 'test') == "1, test"


def test_enforce_input_types_incorrect_types():
    obj = TestClass()
    # This should raise TypeError because 'a' expects an int, not a string
    with pytest.raises(TypeError):
        obj.method_with_input_types('a string', 'test')


def test_enforce_output_types_correct_types():
    obj = TestClass()
    # This should pass as the output is an int
    assert obj.method_with_output_types(1, 2) == 3


def test_enforce_output_types_incorrect_types():
    obj = TestClass()
    # This should raise TypeError because the output is expected to be int,
    # not str
    with pytest.raises(TypeError):
        obj.method_with_output_types('1', '2')


def test_enforce_complex_input_types_correct_types(
        a_mydataframe, an_ordered_dict
):
    obj = TestClass()
    assert are_equal(obj.method_with_complex_input_types(
        a_mydataframe, an_ordered_dict
    ), a_mydataframe.df)


def test_enforce_complex_output_type_correct_type(
        a_mydataframe, an_ordered_dict
):
    obj = TestClass()
    assert are_equal(obj.method_with_complex_output_type(
        a_mydataframe, an_ordered_dict
    ), a_mydataframe.df)


def test_enforce_input_and_output_types_correct_types(
        a_mydataframe, an_ordered_dict
):
    obj = TestClass()
    assert are_equal(obj.method_with_input_and_output_types(
        a_mydataframe, an_ordered_dict
    ), a_mydataframe.df)


def test_enforce_complex_input_types_incorrect_types(
        a_mydataframe, an_ordered_dict
):
    obj = TestClass()
    with pytest.raises(TypeError):
        obj.method_with_complex_input_types(
            an_ordered_dict, a_mydataframe
        )


def test_enforce_complex_output_type_incorrect_type(
        a_mydataframe, an_ordered_dict
):
    obj = TestClass()
    with pytest.raises(TypeError):
        obj.method_with_complex_wrong_output_type(
            a_mydataframe, an_ordered_dict
        )


def test_enforce_input_and_output_types_incorrect_input_types(
        a_mydataframe, a_dict
):
    obj = TestClass()
    with pytest.raises(TypeError):
        obj.method_with_input_and_output_types(
            a_mydataframe, a_dict
        )


def test_enforce_input_and_output_types_incorrect_output_types(
        a_mydataframe, an_ordered_dict
):
    obj = TestClass()
    with pytest.raises(TypeError):
        obj.method_with_input_and_output_types(
            a_mydataframe.df, an_ordered_dict
        )
