"""
test_dict_list_result.py
"""

import pytest

from constants import MAX_ITEMS
from src.nlp.results.dict_list_result import DictListResult


def test_matches_dictionaries_initialization():
    """
    Test for matching dictionaries initialization and assertion of instance
    attributes.

    Checks if a class instance initializes with a specific dictionary and
    has an attribute that matches the input dictionary.

    """
    matches_dictionaries = [{'a': [1, 2, 3]}, {'b': [4, 5, 6]}]
    my_instance = DictListResult(matches_dictionaries)
    assert my_instance.matches_dictionaries == matches_dictionaries


# Sample data for testing
sample_matches = [
    {"key1": ["value1", "value2"], "key2": ["value3"]},
    {"key3": ["value4"], "key4": ["value5", "value6"]}
]


@pytest.fixture
def dict_list_result():
    """
    Fixture to create a DictListResult instance for testing.
    """
    return DictListResult(matches_dictionaries=sample_matches)


def test_initialization():
    """
    Test that the object is initialized with the correct data.
    """
    result = DictListResult(matches_dictionaries=sample_matches)
    assert result.matches_dictionaries == sample_matches


def test_matches_dictionaries_getter(dict_list_result):
    """
    Test the getter of matches_dictionaries.
    """
    assert dict_list_result.matches_dictionaries == sample_matches


def test_matches_dictionaries_setter(dict_list_result):
    """
    Test the setter of matches_dictionaries.
    """
    new_matches = [{"key5": ["value7"]}]
    dict_list_result.matches_dictionaries = new_matches
    assert dict_list_result.matches_dictionaries == new_matches


def test_matches_dictionaries_empty(dict_list_result):
    """
    Test getting matches_dictionaries when they are set to an empty list.
    """
    dict_list_result.matches_dictionaries = []

    with pytest.raises(AttributeError) as err:
        dict_list_result.print()

    assert err.value.args[0] == "No dictionaries given!"


def test_print_less_than_double_max_items(capfd, dict_list_result):
    """
    Test the print method when the list size is less than double MAX_ITEMS.
    """
    dict_list_result.print()
    out, _ = capfd.readouterr()
    assert "key1" in out
    assert "key2" in out


def test_print_more_than_double_max_items(capfd):
    """
    Test the print method when the list size is more than double MAX_ITEMS.
    """
    large_matches = sample_matches * (
            2 * MAX_ITEMS + 1)  # Ensure the list is large enough
    result = DictListResult(matches_dictionaries=large_matches)
    result.print(MAX_ITEMS)
    out, _ = capfd.readouterr()
    assert "..." in out


def test_restrict_print_length(capfd):
    """Test the restrict_print_length method directly."""
    large_matches = sample_matches * (
            2 * MAX_ITEMS + 1)  # Ensure the list is large enough
    result = DictListResult(matches_dictionaries=large_matches)
    result.restrict_print_length(MAX_ITEMS)
    out, _ = capfd.readouterr()
    assert "..." in out
    # Check for presence of content from the start of the list
    assert "key1" in out
