"""
test_item_series.py
"""

import pandas as pd
import pandas.testing as pdt
import pytest

from src.data_structures.item_series import ItemSeries


@pytest.fixture
def item_series():
    """Fixture to create an ItemSeries instance before each test."""
    return ItemSeries(elements=pd.Series([1, 2, 3]), name="TestSeries")


def test_initialization(item_series):
    assert item_series.name == "TestSeries"
    assert item_series.elements.equals(pd.Series([1, 2, 3]))
    assert item_series.n_elements == 3


def test_add_element(item_series):
    item_series.add_element(4)
    assert item_series.elements.equals(pd.Series(
        [1, 2, 3, 4]))
    assert item_series.n_elements == 4


def test_remove_element(item_series):
    item_series.remove_element(2)
    assert item_series.elements.equals(pd.Series([1, 3]))
    assert item_series.n_elements == 2


def test_get_element_by_id(item_series):
    assert item_series.get_element_by_id(1) == 2


def test_distinct_objects(item_series):
    item_series = ItemSeries(elements=pd.Series([1, 2, 2, 3, 3, 3]),
                             name="TestSeries")
    expected_series = pd.Series([1, 2, 3]).drop_duplicates().reset_index(
        drop=True)
    result_series = item_series.distinct_objects.reset_index(drop=True)
    pdt.assert_series_equal(result_series, expected_series)


def test_distinct_elements(item_series):
    item_series = ItemSeries(elements=pd.Series([1, 2, 2, 3, 3, 3]),
                             name="TestSeries")
    expected_list = [1, 2, 3]
    result_list = item_series.distinct_elements
    assert result_list == expected_list


def test_sorted_elements(item_series):
    item_series = ItemSeries(elements=pd.Series(["b", "a", "c"]),
                             name="TestSeries")
    expected_series = pd.Series(["a", "b", "c"]).sort_values().reset_index(
        drop=True)
    result_series = item_series.sorted_elements.reset_index(drop=True)
    pdt.assert_series_equal(result_series, expected_series)


def test_to_strings(item_series):
    assert item_series.to_strings().equals(
        pd.Series(["1", "2", "3"]).astype(str)
    )


def test_str_method_lt_5(item_series):
    expected_str = (
        "ItemSeries 'TestSeries': \n"
        "3 elements, 3 distinct \nPreview: [1, 2, 3]")
    assert str(item_series) == expected_str


def test_str_method_gt_5(item_series):
    item_series.add_element(4)
    item_series.add_element(5)
    item_series.add_element(6)
    expected_str = (
        "ItemSeries 'TestSeries': \n"
        "6 elements, 6 distinct \nPreview: [1, 2, 3, 4, 5, ...]")
    assert str(item_series) == expected_str


def test_str_method_eq_5(item_series):
    item_series.add_element(4)
    item_series.add_element(5)
    expected_str = (
        "ItemSeries 'TestSeries': \n"
        "5 elements, 5 distinct \nPreview: [1, 2, 3, 4, 5]")
    assert str(item_series) == expected_str
