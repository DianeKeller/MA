"""
test_list_utils.py
"""
import pytest

from src.utils.list_utils import (
    are_all_elements_included,
    list_to_string, permute_elements,
    permute_and_join, to_dict_with_str_keys
)


def test_all_elements_included_with_all_elements_found():
    partial_list = [1, 2, 3]
    complete_list = [1, 2, 3, 4, 5]
    assert are_all_elements_included(partial_list, complete_list) is True


def test_all_elements_included_with_some_elements_missing():
    partial_list = [1, 6]
    complete_list = [1, 2, 3, 4, 5]
    assert are_all_elements_included(partial_list, complete_list) is False


def test_all_elements_included_with_empty_partial_list():
    partial_list = []
    complete_list = [1, 2, 3, 4, 5]
    assert are_all_elements_included(partial_list, complete_list) is True


def test_all_elements_included_with_both_lists_empty():
    partial_list = []
    complete_list = []
    assert are_all_elements_included(partial_list, complete_list) is True


def test_all_elements_included_with_identical_lists():
    partial_list = [1, 2, 3]
    complete_list = [1, 2, 3]
    assert are_all_elements_included(partial_list, complete_list) is True


def test_list_to_string_with_list():
    input_list = ['apple', 'banana', 'pear']
    expected_output = '\t apple\t banana\t pear\t \n'
    assert list_to_string(input_list) == expected_output


def test_list_to_string_with_set():
    input_set = {'apple', 'banana', 'pear'}
    # Since sets are unordered, the element output can vary in order.
    # Therefore, it is only verified here if each expected element is in the
    # output string
    output = list_to_string(input_set)
    for item in input_set:
        assert f'\t {item}\t ' in output
    # Check if the output ends with a newline
    assert output.endswith('\n')


def test_list_to_string_with_empty_list_or_set():
    assert list_to_string([]) == ''
    assert list_to_string(set()) == ''


def test_list_to_string_with_line_split():
    # Creating a list that would force a line split
    long_list = ['word' + str(i) for i in range(20)]  # 20 words
    output = list_to_string(long_list)

    # Check if there are at least two lines
    assert output.count('\n') >= 1


def test_list_to_string_with_non_string_elements():
    input_list = [1, 2.5, True]
    expected_output = '\t 1\t 2.5\t True\t \n'
    assert list_to_string(input_list) == expected_output


def test_permute_elements():
    lst = [1, 2, 3]
    expected_result = [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2),
                       (3, 2, 1)]
    assert permute_elements(lst) == expected_result


def test_permute_several_lists():
    lst_1 = [1, 2, 3]
    lst_2 = ["a", "b", "c"]

    result = permute_and_join(lst_1, lst_2)

    expected_result = [(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2),
                       (3, 2, 1), ('a', 'b', 'c'), ('a', 'c', 'b'),
                       ('b', 'a', 'c'), ('b', 'c', 'a'), ('c', 'a', 'b'),
                       ('c', 'b', 'a')]
    assert result == expected_result


@pytest.mark.parametrize("lst, expected", [
    (
            ["a", "b", "c"],
            {"1": "a", "2": "b", "3": "c"}
    ),
    (
            [{"a": "A"}, {"b": "B"}, {"c": "C"}],
            {"1": {"a": "A"}, "2": {"b": "B"}, "3": {"c": "C"}}
    ),
])
def test_to_dict_with_str_keys(lst, expected):
    result = to_dict_with_str_keys(lst, 1)

    assert result == expected
