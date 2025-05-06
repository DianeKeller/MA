"""
test_data_frame_field_operations.py
"""

import pytest

from src.data_structures.my_dataframe_factory import MyDataFrameFactory


def test_set_field_value():
    my_df = MyDataFrameFactory.create(
        ['nnn', 'lll'], ['name']
    )

    my_df.df.set_index(my_df.df.columns[0], inplace=True)

    my_df.do_with_column(
        'add_column',
        data=['nnn_url', 'lll_url'],
        col_name='url'
    )
    my_df.do_with_field(
        'set_field_value',
        row_identifier='nnn',
        col_identifier='url',
        value='n_url'
    )
    my_df.do_with_field(
        'set_field_value',
        row_identifier='lll',
        col_identifier='url',
        value='l_url'
    )

    assert my_df.do_with_field(
        'get_field_value',
        row_identifier='nnn',
        col_identifier='url'
    ) == 'n_url'

    assert my_df.do_with_field(
        'get_field_value',
        row_identifier='lll',
        col_identifier='url'
    ) == 'l_url'


def test_set_field_value_no_row_index():
    my_df = MyDataFrameFactory.create(
        ['nnn', 'lll'], ['name']
    )
    my_df.do_with_column(
        'add_column',
        data=['nnn_url', 'lll_url'],
        col_name='url'
    )
    with pytest.raises(KeyError) as err:
        my_df.do_with_field(
            'set_field_value',
            row_identifier='nnn',
            col_identifier='url',
            value='n_url'
        )

        # Assert the error message
        assert str(err.value.args[0]).startswith(
            "The specified row or column (nnn, url) does not exist in the "
            "DataFrame. Row IDs: [0, 1], Column IDs: ['name', 'url']"
        )


@pytest.mark.parametrize("row_identifier, col_identifier, expected", [
    (0, 0, 'nnn'),
    (2, 1, 'kkk_url'),
    (0, 'name', 'nnn'),
    (2, 'url', 'kkk_url'),
    (-1, 0, 'kkk'),
    (-2, 0, 'lll'),
    (1, -1, 'lll_url'),
    (0, -2, 'nnn')

])
def test_get_field_value(my_df, row_identifier, col_identifier, expected):
    assert my_df.do_with_field(
        'get_field_value',
        row_identifier=row_identifier,
        col_identifier=col_identifier
    ) == expected


@pytest.mark.parametrize("row_identifier, col_identifier", [
    (0, '1'),
    ('0', 0),
    (0, 'nr'),
    ('name', 'url')
])
def test_get_field_value_invalid_identifier(
        my_df, row_identifier,
        col_identifier
):
    with pytest.raises(KeyError) as err:
        my_df.do_with_field(
            'get_field_value',
            row_identifier=row_identifier,
            col_identifier=col_identifier
        )

    # Assert the error message
    assert str(err.value.args[0]) == (
        f"The specified row or column ({row_identifier}, {col_identifier}) "
        f"does not exist in the DataFrame."
    )


@pytest.mark.parametrize("row_identifier, col_identifier", [
    (5, 'name'),
    (1, 7),
    (3, 10)
])
def test_get_field_value_out_of_bounds(
        my_df,
        row_identifier,
        col_identifier
):
    with pytest.raises(IndexError) as err:
        my_df.do_with_field(
            'get_field_value',
            row_identifier=row_identifier,
            col_identifier=col_identifier
        )

    # Assert the error message
    assert str(err.value.args[0]) == (
        f"Row or column index ({row_identifier}, {col_identifier}) is out of "
        f"bounds."
    )


@pytest.mark.parametrize("row_identifier, col_identifier", [
    (0.5, 0),  # Using float, which is unsupported
    (0, 0.5),  # Another example with float where it's not supported
])
def test_get_field_value_invalid_type(
        my_df, row_identifier,
        col_identifier
):
    with pytest.raises(KeyError) as err:
        my_df.do_with_field(
            'get_field_value',
            row_identifier=row_identifier,
            col_identifier=col_identifier
        )

        # Assert the error message
    assert str(err.value.args[0]) == (
        f"The specified row or column ({row_identifier}, {col_identifier}) "
        f"does not exist in the DataFrame."

    )
