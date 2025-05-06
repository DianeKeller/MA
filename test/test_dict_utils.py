"""
test_dict_utils.py
"""

from collections import OrderedDict

import pytest

from src.data_structures.my_ordered_dict import MyOrderedDict
from src.utils.dict_utils import (
    get_n_items_from_bottom,
    get_n_items_from_top,
    filter_dict_by_value, dict_to_string,
    convert_keys_to_consecutive_str_numbers, merge_dicts,
    exclude_list_elements_from_dict, unique, value_is_in_dict,
    dict_is_in_list_of_dicts
)


def test_empty_dict():
    """Test that an empty dictionary returns an empty string."""
    assert dict_to_string({}) == ""


def test_simple_dict():
    """Test conversion of a simple dictionary."""
    result = dict_to_string({'apple': 1, 'banana': 2, 'cherry': 3})
    expected = '\t apple: 1\t banana: 2\t cherry: 3\t \n'
    assert result == expected


def test_mixed_types_dict():
    """Test a dictionary with mixed key and value types."""
    result = dict_to_string({1: 'a', 2: 'b', '3': 3})
    # Note: The order of items in the string depends on the dictionary order,
    # which is insertion order for Python 3.7+
    expected = '\t 1: a\t 2: b\t 3: 3\t \n'
    assert result == expected


def test_long_dict():
    """Test a dictionary that results in a string longer than 80 characters."""
    long_dict = {f"item_{i}": i for i in range(1, 21)}
    result = dict_to_string(long_dict)
    assert len(result) > 80, "The result should be longer than 80 characters."
    assert '\n' in result, ("The result should contain newline characters to "
                            "avoid exceeding line length.")
    assert result.endswith('\n')


def test_special_characters():
    """Test dictionary keys/values that include special characters."""
    special_dict = {
        'new\nline': 'value1',
        'key2': 'tab\tcharacter',
        'key3': 'normal'
    }
    result = dict_to_string(special_dict)
    # This test assumes that special characters are not handled specially and
    # appear as-is.
    expected = ('\t new\nline: value1\t key2: tab\tcharacter\t key3: '
                'normal\t \n')
    assert result == expected


def test_get_n_items_from_top(a_dict):
    extracted_dict = get_n_items_from_top(a_dict, 3)
    extracted_ordered_dict = MyOrderedDict(OrderedDict(extracted_dict))
    assert extracted_ordered_dict.first_value == '1bcd'
    assert extracted_ordered_dict.second_value == '3fgh'
    assert extracted_ordered_dict.last_value == '11def'


def test_get_n_items_from_top_of_empty_dict(an_empty_dict):
    extracted_dict = get_n_items_from_top(an_empty_dict, 3)
    assert extracted_dict == {}


def test_get_0_items_from_top(a_dict):
    extracted_dict = get_n_items_from_top(a_dict, 0)
    assert extracted_dict == {}


def test_get_more_items_from_top_than_exist(a_dict):
    extracted_dict = get_n_items_from_top(a_dict, 20)
    assert len(extracted_dict) == 6


def test_get_n_items_from_top_with_negative_int(a_dict):
    with pytest.raises(ValueError) as err:
        get_n_items_from_top(a_dict, -3)

    # Assert the error message
    assert str(err.value.args[0]) == (
        "CRITICAL: The number of items in a dictionary cannot be negative."
    )


def test_get_n_items_from_top_with_float(a_dict):
    with pytest.raises(TypeError) as err:
        get_n_items_from_top(a_dict, 3.7)

    # Assert the error message
    assert str(err.value.args[0]) == (
        "slice indices must be integers or None or have an __index__ method"
    )


@pytest.mark.parametrize("n_elements", [
    (),
    None,
    "zwei"
])
def test_get_n_items_from_top_with_invalid_input_type(n_elements, a_dict):
    with pytest.raises(TypeError) as err:
        get_n_items_from_top(a_dict, n_elements)

    # Assert the error message
    assert str(err.value.args[0]).startswith(
        "'<' not supported between instances of "
    )


def test_get_n_items_from_bottom(a_dict):
    extracted_dict = get_n_items_from_bottom(a_dict, 3)
    extracted_ordered_dict = MyOrderedDict(OrderedDict(extracted_dict))
    assert extracted_ordered_dict.first_value == '11def'
    assert extracted_ordered_dict.second_value == '11def'
    assert extracted_ordered_dict.last_value == '2abc'
    assert extracted_ordered_dict.first_key == 'd'
    assert extracted_ordered_dict.last_key == 'a'
    assert extracted_ordered_dict.second_key == 'c'


def test_get_n_items_from_bottom_of_empty_dict(an_empty_dict):
    extracted_dict = get_n_items_from_bottom(an_empty_dict, 3)
    assert not extracted_dict


def test_get_0_items_from_bottom(a_dict):
    extracted_dict = get_n_items_from_bottom(a_dict, 0)
    assert not extracted_dict


def test_get_more_items_from_bottom_than_exist(a_dict):
    extracted_dict = get_n_items_from_bottom(a_dict, 20)
    assert len(extracted_dict) == 6


def test_get_n_items_from_bottom_with_negative_int(a_dict):
    with pytest.raises(ValueError) as err:
        get_n_items_from_bottom(a_dict, -3)

    # Assert the error message
    assert str(err.value.args[0]) == (
        "CRITICAL: The number of items in a dictionary cannot be negative."
    )


def test_get_n_items_from_bottom_with_float(a_dict):
    with pytest.raises(ValueError) as err:
        get_n_items_from_bottom(a_dict, 3.7)

    # Assert the error message
    assert str(err.value.args[0]).endswith(
        "Stop argument for islice() must be None or an integer: 0 <= x <= "
        "sys.maxsize."
    )


@pytest.mark.parametrize("n_elements", [
    (),
    None,
    "zwei"
])
def test_get_n_items_from_bottom_with_invalid_input_type(n_elements, a_dict):
    with pytest.raises(TypeError) as err:
        get_n_items_from_bottom(a_dict, n_elements)

    # Assert the error message
    assert str(err.value.args[0]).startswith(
        "'<' not supported between instances of "
    )


@pytest.mark.parametrize("filter_value, expected", [
    (3, {'c': 3}),
    (3.0, {'c': 3}),
    (2, {'b': 2.5, 'c': 3}),
    (2.5, {'b': 2.5, 'c': 3}),
    (2.7, {'b': 2.5, 'c': 3}),
    (2.8, {'b': 2.5, 'c': 3}),
    (3.5, {'c': 3}),
    (0, {'a': 1}),
    (0.0, {'a': 1}),
    (-4, {'a': 1}),
    (-4.0, {'a': 1}),
    (100, {'e': 5.0, 'f': 5.5, 'g': 5.7}),
    (100.0, {'e': 5.0, 'f': 5.5, 'g': 5.7}),
])
def test_filter_dict_by_value(a_num_dict, filter_value, expected):
    assert filter_dict_by_value(filter_value, a_num_dict) == expected


def test_convert_keys_to_consecutive_str_numbers():
    data = {
        'a': 1,
        'b': 2,
        'c': 3
    }

    expected_data = {
        '1': 1,
        '2': 2,
        '3': 3
    }

    converted_data = convert_keys_to_consecutive_str_numbers(data)

    assert converted_data == expected_data


def test_merge_dicts():
    dict1 = {'a': ['apple', 'avocado'], 'b': ['banana']}
    dict2 = {'a': ['apricot'], 'c': ['cherry']}

    result = merge_dicts(dict1, dict2)
    expected_result = {
        'a': ['apple', 'avocado', 'apricot'],
        'b': ['banana'],
        'c': ['cherry']
    }

    assert result == expected_result

    print(result)


def test_exclude_list_elements_from_dict():
    dict1 = {'a': ['apple', 'avocado'], 'b': ['banana']}
    dict2 = {'a': ['apple'], 'c': ['cherry'], 'b': ['blueberry', 'banana']}

    result = exclude_list_elements_from_dict(dict1, dict2)
    expected_result = {
        'a': ['avocado'],
        'b': [],
    }

    assert result == expected_result


def test_unique_1():
    data = {
        '1': 'a',
        '2': 'a',
        '3': 'b',
        '4': 'c',
        '5': 'b',
        '6': 'a'
    }

    x = unique(data)

    expected = {
        '1': 'a',
        '3': 'b',
        '4': 'c',
    }

    assert x == expected


def test_unique_2():
    data = {
        '1': {
            'a': 'abc',
            'b': 'bcd',
            'c': 'cde'
        },
        '2': {
            'a': 'efg',
            'b': 'bcd',
            'c': 'cde'
        },
        '3': {
            'a': 'abc',
            'b': 'bcd',
            'c': 'cde'
        }
    }

    x = unique(data)

    expected = {
        '1': {
            'a': 'abc',
            'b': 'bcd',
            'c': 'cde'
        },
        '2': {
            'a': 'efg',
            'b': 'bcd',
            'c': 'cde'
        }
    }

    assert x == expected


def test_is_in_dict_1():
    data = {
        '1': {
            'a': 'abc',
            'b': 'bcd',
            'c': 'cde'
        },
        '2': {
            'a': 'efg',
            'b': 'bcd',
            'c': 'cde'
        },
        '3': {
            'a': 'abc',
            'b': 'bcd',
            'c': 'cde'
        }
    }

    item = {
        'a': 'abc',
        'b': 'bcd',
        'c': 'cde'
    }

    assert value_is_in_dict(item, data)


def test_is_in_dict_2():
    data = {
        '1': 'a',
        '2': 'a',
        '3': 'b',
        '4': 'c',
        '5': 'b',
        '6': 'a'
    }

    item = 'b'

    assert value_is_in_dict(item, data)


def test_is_in_list():
    dict_list = [
        {'a': 1, 'b': 2},
        {'a': 3, 'b': 4},
        {'a': 5, 'b': 6}
    ]

    item = {'a': 3, 'b': 4}

    assert dict_is_in_list_of_dicts(item, dict_list)
