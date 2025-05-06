"""
test_print_utils.py
"""

import pytest

from src.utils.print_utils import restrict_length


@pytest.mark.parametrize("input_list, max_items, expected", [
    ([1, 2, 3, 4, 5], 3, [1, 2, 3]),
    ([], 3, []),
    ([1], 5, [1]),
])
def test_restrict_list_length(input_list, max_items, expected):
    assert restrict_length(input_list, max_items) == expected


@pytest.mark.parametrize("input_dict, max_items, expected", [
    ({"a": 1, "b": 2, "c": 3}, 2, {"a": 1, "b": 2}),
    ({}, 2, {}),
    ({"a": 1}, 5, {"a": 1}),
])
def test_restrict_dict_length(input_dict, max_items, expected):
    assert restrict_length(input_dict, max_items) == expected


@pytest.mark.parametrize("input_str, max_length, expected", [
    ("hello-world", 5, "hello\n-\nworld"),
    ("hello_world", 5, "hello\n_\nworld"),
    ("hello world", 5, "hello \nworld"),
    ("hello world", 7, "hello \nworld"),
    ("hello-world", 10, "hello-\nworld"),
    ("", 5, ""),
    (
            'Text_raw_lower_free_sentence words tokenized by '
            'NoPunctuationStrategy',
            20,
            'Text_raw_lower_free_\nsentence words \ntokenized '
            'by \nNoPunctuationStrateg\ny'
    ),
    (
            'Text_raw_lower_free_sentence words tokenized by '
            'NoPunctuationStrategy',
            40,
            'Text_raw_lower_free_sentence words \ntokenized by '
            'NoPunctuationStrategy'
    ),
    (
            'Text_raw_lower_free_sentence words tokenized by '
            'NoPunctuationStrategy',
            80,
            'Text_raw_lower_free_sentence words tokenized by '
            'NoPunctuationStrategy'
    )
])
def test_restrict_string_length(input_str, max_length, expected):
    assert restrict_length(input_str, max_length) == expected
