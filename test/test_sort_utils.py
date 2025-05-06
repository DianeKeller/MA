"""
test_sort_utils.py
"""

import pytest

from src.utils.list_sort_utils import sort_list


@pytest.mark.parametrize("unsorted_lst, expected_sorted_lst", [
    (
            [3, 1, 0, 2, 1, -1],
            [-1, 0, 1, 1, 2, 3]
    ),
    (
            {3, 1, 0, 2, 1, -1},
            [-1, 0, 1, 2, 3]
    ),
    (
            (3, 1, 0, 2, 1, -1),
            [-1, 0, 1, 1, 2, 3]
    ),
    (
            [3, 1.2, 0, 2.8, 1.20, -1.01, -1],
            [-1.01, -1, 0, 1.2, 1.2, 2.8, 3]
    ),
    (
            {3, 1.2, 0, 2.8, 1.20, -1.01, -1},
            [-1.01, -1, 0, 1.2, 2.8, 3]
    ),
    (
            (3, 1.2, 0, 2.8, 1.20, -1.01, -1),
            [-1.01, -1, 0, 1.2, 1.2, 2.8, 3]
    ),
    (
            ["banana", "apple", " ", "", "-1", "0", "apple", "pear", "10",
             "2", "fig", "1"],
            ["", " ", "-1", "0", "1", "10", "2", "apple", "apple", "banana",
             "fig", "pear"]
    ),
    (
            {"banana", "apple", " ", "", "-1", "0", "apple", "pear", "10",
             "2", "fig", "1"},
            ["", " ", "-1", "0", "1", "10", "2", "apple", "banana",
             "fig", "pear"]
    ),
    (
            ("banana", "apple", " ", "", "-1", "0", "apple", "pear", "10",
             "2", "fig", "1"),
            ["", " ", "-1", "0", "1", "10", "2", "apple", "apple", "banana",
             "fig", "pear"]
    ),
    (
            [],
            []
    ),
    (
            ["banana", "apple", " ", "", "-1", "0", "Apple", "Pear", "10",
             "2", "fig", "1"],
            ["", " ", "-1", "0", "1", "10", "2", "Apple", "Pear", "apple",
             "banana", "fig"]
    ),
    (
            {"banana", "apple", " ", "", "-1", "0", "Apple", "Pear", "10",
             "2", "fig", "1"},
            ["", " ", "-1", "0", "1", "10", "2", "Apple", "Pear", "apple",
             "banana", "fig"]
    ),
    (
            ("banana", "apple", " ", "", "-1", "0", "Apple", "Pear", "10",
             "2", "fig", "1"),
            ["", " ", "-1", "0", "1", "10", "2", "Apple", "Pear", "apple",
             "banana", "fig"]
    ),
])
def test_sort_list(unsorted_lst, expected_sorted_lst):
    """
    Test sort_list() with lists [], sets {} and tuples () of strings or
    numbers.

    Parameters
    ----------
    unsorted_lst
    expected_sorted_lst

    """
    result = sort_list(unsorted_lst)

    assert result == expected_sorted_lst
    assert isinstance(result, list)


def test_sort_list_with_mixed_types():
    unsorted_lst = ["1", "apple", 3]

    with pytest.raises(TypeError) as err:
        sort_list(unsorted_lst)

    # Assert the error message
    assert str(err.value.args[0]) == (
        "Input cannot mix strings and numbers"
    )
