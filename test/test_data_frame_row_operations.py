"""
test_data_frame_row_operations.py
"""

import pandas as pd
import pytest
from pandas import DataFrame

from src.data_structures.my_dataframe_factory import MyDataFrameFactory


def test_get_row_df_by_name():
    # Prepare a dataframe with row names, first defining columns with column
    # names, then transposing the dataframe so that the column names become
    # row names.

    # 1. Create a dataframe with two columns and two rows.

    dict1 = {
        'name': ['nnn'],
        'url': ['nnn_url']
    }
    dict2 = {
        'name': ['lll'],
        'url': ['lll_url']
    }
    my_df = MyDataFrameFactory.create(dict1)

    my_df.do_with_row('add_rows', data=dict2)

    '''
    Now, my_df.df looks like this:

    __________________________________
        name            url            
    0   nnn           nnn_url
    1   lll           lll_url
    ==================================
    '''

    my_df.df = my_df.df.T

    '''
    The transposed dataframe looks like this:
    __________________________________
            0           1
    name    nnn       lll
    url     nnn_url   lll_url
    ==================================
    '''

    # Check whether the result matches the expected result

    expected_df_1 = pd.DataFrame({'name': ['nnn', 'lll']}).T

    row_1 = my_df.do_with_row('get_row_df_by_name', row_name='name')

    pd.testing.assert_frame_equal(row_1, expected_df_1)

    expected_df_2 = pd.DataFrame({'url': ['nnn_url', 'lll_url']}).T

    row_2 = my_df.do_with_row('get_row_df_by_name', row_name='url')
    pd.testing.assert_frame_equal(row_2, expected_df_2)


def test_get_row_df_by_index():
    my_df = MyDataFrameFactory.create(['nnn', 'lll'], ['name'])

    expected_df_1 = pd.DataFrame({'name': ['nnn']})
    expected_df_2 = pd.DataFrame({'name': ['lll']}, index=[1])

    row_1 = my_df.do_with_row('get_row_df_by_index', row_index=0)
    row_2 = my_df.do_with_row('get_row_df_by_index', row_index=1)

    pd.testing.assert_frame_equal(row_1, expected_df_1)
    pd.testing.assert_frame_equal(row_2, expected_df_2)


def test_row_index_usage():
    """
    This is the example from the row_index getter docstring. It does not
    assert anything but allows for running the code whilst monitoring the
    data in debugging mode.

    """
    # Create MyDataFrame object with some columns and rows:

    my_df = MyDataFrameFactory.create({
        'name': ['a', 'b'],
        'nr': [7, 9],
        'info': ['Hello', 'World!']
    })

    # Set one of the columns as the row index:

    my_df.row_index = 'name'

    # Get the row index and print it:

    index = my_df.row_index
    print(index)
    # The print output should look like this:
    # Index(['a', 'b'], dtype='object', name='name')

    # Use the index to access a specific row:
    row_df = my_df.do_with_row('get_row_df_by_name', row_name='b')

    # or
    row_series = my_df.do_with_row('get_row_series_by_name', row_name='b')


def test_get_row_series_by_name():
    # Prepare a dataframe with row names, first defining columns with column
    # names, then transposing the dataframe so that the column names become
    # row names.

    # Create a dataframe with two columns and two rows.

    dict1 = {
        'name': ['nnn'],
        'url': ['nnn_url']
    }
    dict2 = {
        'name': ['lll'],
        'url': ['lll_url']
    }
    my_df = MyDataFrameFactory.create(dict1)

    my_df.do_with_row('add_rows', data=dict2)

    '''
    Now, my_df.df looks like this:

    __________________________________
        name            url            
    0   nnn           nnn_url
    1   lll           lll_url
    ==================================
    '''
    # Transpose the dataframe
    my_df.df = my_df.df.T

    '''
    The transposed dataframe looks like this:
    __________________________________
            0           1
    name    nnn       lll
    url     nnn_url   lll_url
    ==================================
    '''

    # Check whether the result matches the expected result
    # Expected series matching the transposed structure
    # Note: The 'name' attribute of the series should match the row label in
    # the transposed DataFrame
    expected_series_1 = pd.Series(['nnn', 'lll'], index=[0, 1],
                                  name='name')
    expected_series_2 = pd.Series(['nnn_url', 'lll_url'], index=[0, 1],
                                  name='url')

    row_1 = my_df.do_with_row(
        'get_row_series_by_name',
        row_name='name'
    )
    row_2 = my_df.do_with_row(
        'get_row_series_by_name',
        row_name='url'
    )

    pd.testing.assert_series_equal(row_1, expected_series_1)
    pd.testing.assert_series_equal(row_2, expected_series_2)


def test_get_row_series_by_index():
    my_df = MyDataFrameFactory.create(['nnn', 'lll'], ['name'])

    expected_series_1 = pd.Series(['nnn'], index=['name'], name=0)
    expected_series_2 = pd.Series(['lll'], index=['name'], name=1)

    row_1 = my_df.do_with_row('get_row_series_by_index', row_index=0)
    row_2 = my_df.do_with_row('get_row_series_by_index', row_index=1)

    pd.testing.assert_series_equal(row_1, expected_series_1)
    pd.testing.assert_series_equal(row_2, expected_series_2)


@pytest.mark.parametrize("new_data", [
    (['kkk', 'rrr']),
    ({'name': ['kkk', 'rrr']}),
    (DataFrame({'name': ['kkk', 'rrr']})),
    ('kkk', 'rrr')
])
def test_add_rows(new_data):
    # Initial data setup
    initial_data = {'name': ['nnn', 'lll']}
    my_df = MyDataFrameFactory.create(initial_data)

    my_df.do_with_row('add_rows', data=new_data)

    expected_df = pd.DataFrame({
        'name': ['nnn', 'lll', 'kkk', 'rrr']
    })

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df.reset_index(drop=True), expected_df)


@pytest.mark.parametrize("invalid_data", [
    ([74]),
    ({'age': [74]}),
    (DataFrame({'age': [74]})),
    (74,)
])
def test_add_invalid_data(invalid_data):
    # Initial data setup
    initial_data = {'name': ['nnn', 'lll']}
    my_df = MyDataFrameFactory.create(initial_data)

    # Try to add the new colum
    with pytest.raises(ValueError) as err:
        my_df.do_with_row('add_rows', data=invalid_data)

    # Assert the error message
    assert str(err.value.args[0]) == (
        "CRITICAL: The data contains columns that do not match the "
        "dataframe's columns. Cannot add the rows."
    )


@pytest.mark.parametrize("invalid_data", [
    ([1]),
    ({'name': [1]}),
    (DataFrame({'name': [1]})),
    (1,)
])
def test_add_row_with_wrong_data_type(invalid_data):
    # Initial data setup
    initial_data = {'name': ['nnn', 'lll']}
    my_df = MyDataFrameFactory.create(initial_data)

    # Try to add the new colum
    with pytest.raises(ValueError) as err:
        my_df.do_with_row('add_rows', data=invalid_data)

    # Assert the error message
    assert str(err.value.args[0]) == (
        "CRITICAL: The data contains columns that do not match the "
        "dataframe's columns. Cannot add the rows."
    )


@pytest.mark.parametrize("new_data", [
    ([['kkk', 7], ['ppp', 8], ['zzz', 8]]),
    ({
        'name': ['kkk', 'ppp', 'zzz'],
        'nr': [7, 8, 8]
    }),
    (
            DataFrame({
                'name': ['kkk', 'ppp', 'zzz'],
                'nr': [7, 8, 8]
            })
    ),
    (('kkk', 7), ('ppp', 8), ('zzz', 8))
])
def test_add_rows_to_several_columns(new_data):
    # Initial data setup
    initial_data = {
        'name': ['nnn', 'lll'],
        'nr': [100, 45]
    }
    my_df = MyDataFrameFactory.create(initial_data)

    my_df.do_with_row('add_rows', data=new_data)

    expected_df = pd.DataFrame({
        'name': ['nnn', 'lll', 'kkk', 'ppp', 'zzz'],
        'nr': [100, 45, 7, 8, 8],
    })

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df.reset_index(drop=True), expected_df)


@pytest.mark.parametrize("invalid_data", [
    ([['kkk', 'xyz', 18], ['ppp', 'opq', 17]]),
    ({
        'name': ['kkk', 'ppp'],
        'info': ['xyz', 'opq'],
        'nr': [18, 17]
    }),
    (
            DataFrame({
                'name': ['kkk', 'ppp'],
                'info': ['xyz', 'opq'],
                'nr': [18, 17]
            })
    ),
    (('kkk', 'xyz', 18), ('ppp', 'opq', 17))
])
def test_add_rows_with_too_many_columns(invalid_data):
    # Initial data setup
    initial_data = {'name': ['nnn', 'lll']}
    my_df = MyDataFrameFactory.create(initial_data)

    # Try to add the new colum
    with pytest.raises(ValueError) as err:
        my_df.do_with_row('add_rows', data=invalid_data)

    # Assert the error message
    assert str(err.value.args[0]) == (
        "CRITICAL: The data contains columns that do not match the "
        "dataframe's columns. Cannot add the rows."
    )


def test_row_index():
    data = {
        'name': ['nnn', 'lll'],
        'nr': [7, 9]
    }

    my_df = MyDataFrameFactory.create(data,
                                      col_names=['name', 'nr', 'address'])
    my_df.row_index = 'name'

    expected_index = pd.Index(['nnn', 'lll'], name='name')

    pd.testing.assert_index_equal(my_df.row_index, expected_index)


def test_manually_add_row_to_a_dataframe():
    """
    This test serves as a reference for the unit tests below.

    It does not test any module or function but shows how a row can
    successfully be added to a dataframe.

    """

    df = DataFrame({'name': ['nnn', 'lll']})
    # Adding a row using a dictionary for new row data
    row_data = {'name': ['kkk']}
    df = pd.concat([df, DataFrame(row_data)], ignore_index=True)
    expected_df = pd.DataFrame({
        'name': ['nnn', 'lll', 'kkk']
    })

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(df.reset_index(drop=True), expected_df)
