"""
test_data_frame_factory.py
"""

import pytest
from pandas import DataFrame
from pandas._testing import assert_frame_equal

from src.data_structures.data_frame_factory import DataFrameFactory
from src.utils.data_comparison_utils import are_equal


@pytest.mark.parametrize("col_names, expected_keys", [
    (None, ['A', 'B', 'C']),
    ([None, None, None], ['A', 'B', 'C']),
    (['', '', ''], ['A', 'B', 'C']),
    ([1, 2, 3], ['A', 'B', 'C']),
    (['A', 'C', 'B'], ['A', 'C', 'B']),
    (['A', 'C', 'D'], ['A', 'B', 'C']),
    (['A', 'C'], ['A', 'B', 'C']),
    (['B', 'E', 'F'], ['A', 'B', 'C']),
    (['D', 'E', 'F'], ['A', 'B', 'C']),
    (['A', 'B', 'C', 'D'], ['A', 'B', 'C', 'D']),
    (['A', 'C', 'B', 'D'], ['A', 'C', 'B', 'D']),
])
def test_ordered_dict_reorder_columns_with_at_least_one_known_column(
        an_ordered_dict_with_multiple_columns, col_names, expected_keys
):
    o_dict = an_ordered_dict_with_multiple_columns
    df = DataFrameFactory().create(o_dict, col_names=col_names)
    expected_data = {
        key: o_dict.get(key, [None] * len(next(iter(o_dict.values())))) for key
        in expected_keys}
    df_expected = DataFrame(expected_data, columns=expected_keys)

    assert are_equal(df, df_expected)
    assert_frame_equal(df, df_expected)
