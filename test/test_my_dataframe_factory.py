"""
test_my_dataframe_factory.py
"""

import pandas as pd

from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory


def test_dictionary():
    data = {'name': ['nnn', 'lll'], 'nr': [30, 24]}
    my_df = MyDataFrameFactory.create(data)
    print(my_df.df)

    # Construct the expected DataFrame
    expected_df = pd.DataFrame({'name': ['nnn', 'lll'],
                                'nr': [30, 24]})

    # Check whether my_df is a MyDataFrame object
    assert isinstance(my_df, MyDataFrame)

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_none():
    my_df = MyDataFrameFactory.create(col_names=['name', 'nr'])
    print(my_df.df)

    # Construct the expected DataFrame
    expected_df = pd.DataFrame(pd.DataFrame(columns=['name', 'nr']))

    # Check whether my_df is a MyDataFrame object
    assert isinstance(my_df, MyDataFrame)

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_simple_list_representing_column():
    data = ['nnn', 'lll']
    columns = ['name']
    my_df = MyDataFrameFactory.create(
        data=data,
        col_names=columns
    )
    print(my_df.df)

    # Construct the expected DataFrame
    expected_df = pd.DataFrame({'name': ['nnn', 'lll']})

    # Check whether my_df is a MyDataFrame object
    assert isinstance(my_df, MyDataFrame)

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_simple_list_representing_first_of_several_columns():
    data = ['nnn', 'lll']
    columns = ['name', 'nr', 'info']
    my_df = MyDataFrameFactory.create(
        data=data,
        col_names=columns
    )
    print(my_df.df)

    # Construct the expected DataFrame
    expected_df = pd.DataFrame(
        {'name': ['nnn', 'lll'], 'nr': [None, None], 'info': [None, None]})

    # Check whether my_df is a MyDataFrame object
    assert isinstance(my_df, MyDataFrame)

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_simple_list_representing_column_without_col_name():
    data = ['nnn', 'lll']
    my_df = MyDataFrameFactory.create(
        data=data
    )
    print(my_df.df)

    # Construct the expected DataFrame
    expected_df = pd.DataFrame({'Column_0': ['nnn', 'lll']})

    # Check whether my_df is a MyDataFrame object
    assert isinstance(my_df, MyDataFrame)

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_simple_list_representing_row():
    data = ['nnn', 13]
    columns = ['name', 'nr']
    my_df = MyDataFrameFactory.create(
        data=data,
        col_names=columns
    )
    print(my_df.df)

    # Construct the expected DataFrame
    expected_df = pd.DataFrame({'name': ['nnn'], 'nr': [13]})

    # Check whether my_df is a MyDataFrame object
    assert isinstance(my_df, MyDataFrame)

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_simple_list_representing_row_without_col_names():
    data = ['nnn', 13]
    my_df = MyDataFrameFactory.create(
        data=data
    )
    print(my_df.df)

    # Construct the expected DataFrame
    expected_df = pd.DataFrame([['nnn', 13]])

    # Check whether my_df is a MyDataFrame object
    assert isinstance(my_df, MyDataFrame)

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_simple_list_representing_column_w_equal_numbers_of_columns_and_rows():
    data = ['nnn', 'lll']
    columns = ['name', 'nr']
    my_df = MyDataFrameFactory.create(
        data=data,
        col_names=columns
    )
    print(my_df.df)

    # Construct the expected DataFrame
    expected_df = pd.DataFrame({'name': ['nnn', 'lll'], 'nr': [None, None]})

    # Check whether my_df is a MyDataFrame object
    assert isinstance(my_df, MyDataFrame)

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_list_of_lists():
    data = [['nnn', 30], ['lll', 24]]
    my_df = MyDataFrameFactory.create(
        data=data,
        col_names=['name', 'nr']
    )
    print(my_df.df)

    # Construct the expected DataFrame
    expected_df = pd.DataFrame({'name': ['nnn', 'lll'],
                                'nr': [30, 24]})

    # Check whether my_df is a MyDataFrame object
    assert isinstance(my_df, MyDataFrame)

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)
