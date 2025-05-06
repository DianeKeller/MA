"""
test_data_utils.py
"""

from collections import OrderedDict

import pytest
from pandas import DataFrame

from src.data_structures.my_data_frame import MyDataFrame
from src.utils.data_utils import is_none_or_empty


@pytest.mark.parametrize("data, expected", [
    (None, True),
    ([], True),
    ([False], False),
    ({}, True),
    ({1}, False),
    ("", True),
    (" \n", True),
    ("Hello", False),
    (b'', True),
    (set(), True),
    (set(""), True),
    ((), True),
    (("", ""), False),
    ((None, None), False),
    ({None}, False),
    (range(0), True),
    (0, True),
    (0.0, True)
])
def test_is_none_or_empty(data, expected):
    assert is_none_or_empty(data) is expected


@pytest.mark.parametrize("string, expected", [
    ("  ", True),
    ("", True),
    (None, True),
    ("test", False),
    ("test ", False),
    (" test", False),
    ("\n", True),
    ("\t", True),
    ("test\n", False),
    ("test\t", False),
    ("test\n\t", False)
])
def test_string_is_empty(string, expected):
    assert is_none_or_empty(string) is expected


def test_is_none_or_empty_with_dataframe(a_dataframe, an_empty_dataframe):
    assert isinstance(a_dataframe, DataFrame)
    assert isinstance(an_empty_dataframe, DataFrame)

    assert is_none_or_empty(a_dataframe) is False
    assert is_none_or_empty(an_empty_dataframe) is True


def test_is_none_or_empty_with_mydataframe(
        a_mydataframe,
        an_empty_mydataframe,
        a_mydataframe_with_empty_data
):
    assert isinstance(a_mydataframe, MyDataFrame)
    assert isinstance(an_empty_mydataframe, MyDataFrame)
    assert isinstance(a_mydataframe_with_empty_data, MyDataFrame)

    assert is_none_or_empty(a_mydataframe) is False
    assert is_none_or_empty(an_empty_mydataframe) is True
    assert is_none_or_empty(a_mydataframe_with_empty_data.df) is True
    assert is_none_or_empty(a_mydataframe_with_empty_data) is True


def test_is_none_or_empty_with_ordered_dict(
        an_ordered_dict, an_empty_ordered_dict):
    assert isinstance(an_ordered_dict, OrderedDict)
    assert isinstance(an_empty_ordered_dict, OrderedDict)

    assert is_none_or_empty(an_ordered_dict) is False
    assert is_none_or_empty(an_empty_ordered_dict) is True
