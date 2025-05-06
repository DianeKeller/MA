"""
test_item_list.py
"""

import pytest

from src.data_structures.item_list import \
    ItemList  # Adjust the import path as necessary


@pytest.fixture
def item_list():
    """Fixture to create an ItemList instance before each test."""
    return ItemList(elements=[1, 2, 3], name="TestList")


def test_initialization(item_list):
    assert item_list.name == "TestList"
    assert item_list.elements == [1, 2, 3]
    assert item_list.n_elements == 3


def test_add_element(item_list):
    item_list.add_element(4)
    assert item_list.elements == [1, 2, 3, 4]
    assert item_list.n_elements == 4


def test_remove_element(item_list):
    item_list.remove_element(2)
    assert item_list.elements == [1, 3]
    assert item_list.n_elements == 2


def test_get_element(item_list):
    assert item_list.get_element_by_id(1) == 2


def test_compute_distinct_elements():
    item_list = ItemList(elements=[1, 2, 2, 3, 3, 3], name="TestList")
    item_list._compute_distinct_elements()
    assert set(item_list.distinct_elements) == {1, 2, 3}
    assert item_list.n_distinct_elements == 3


def test_compute_sorted_elements():
    item_list = ItemList(elements=["b", "a", "c"], name="TestList")
    item_list._compute_sorted_elements()
    assert item_list.sorted_elements == ["a", "b", "c"]


def test_to_strings(item_list):
    assert item_list.to_strings() == ["1", "2", "3"]


def test_str_method(item_list):
    expected_str = ("ItemList 'TestList': \n3 elements, 3 distinct \nPreview: "
                    "[1, 2, 3]")
    assert str(item_list) == expected_str
