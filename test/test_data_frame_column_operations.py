"""
test_data_frame_column_operations.py
"""

import pandas as pd
import pytest

from src.data_structures.my_dataframe_factory import MyDataFrameFactory


def test_add_column_with_name():
    # Initial data for the DataFrame
    initial_data = {
        'name': ['nnn', 'lll'],
        'url': ['nnn_url', 'lll_url']
    }
    my_df = MyDataFrameFactory.create(initial_data)

    # Data to be added as a new column
    new_column_data = [1, 2]
    new_col_name = 'id'

    # Add the new column
    my_df.do_with_column(
        'add_column',
        data=new_column_data,
        col_name=new_col_name
    )

    # Check if the new column exists
    assert new_col_name in my_df.df.columns
    assert new_col_name in my_df.col_names

    # Check if the data in the new column is correct
    pd.testing.assert_series_equal(
        my_df.df[new_col_name],
        pd.Series(
            new_column_data,
            name=new_col_name
        ),
        check_names=False
    )


def test_add_column_without_name():
    # Initial data for the DataFrame
    initial_data = {
        'name': ['nnn', 'lll'],
        'url': ['nnn_url', 'lll_url']
    }
    my_df = MyDataFrameFactory.create(initial_data)

    # Data to be added as a new column
    new_column_data = ['info', 'info']

    # Expected column name based on the existing columns
    expected_col_name = f"Column_{len(my_df.df.columns) + 1}"

    # Add the new column without specifying a name
    my_df.do_with_column(
        'add_column',
        data=new_column_data
    )

    # Check if the new column exists with the expected name
    assert expected_col_name in my_df.df.columns

    # Check if the data in the new column is correct
    pd.testing.assert_series_equal(
        my_df.df[expected_col_name],
        pd.Series(
            new_column_data,
            name=expected_col_name
        ),
        check_names=False
    )


def test_add_column_without_values():
    # Initial data setup with value lists
    data_list = ['nnn', 'lll']
    columns_list = ['name']
    my_df = MyDataFrameFactory.create(data_list, columns_list)

    # Name of the new column to be added
    col_name = 'url'

    # Add the new column without providing values
    my_df.do_with_column(
        'add_column',
        col_name=col_name
    )

    # Construct the expected DataFrame
    expected_df = pd.DataFrame({'name': ['nnn', 'lll'],
                                'url': [None, None]})

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_add_column_with_none_values():
    # Initial data setup with a list of lists
    data_list = [['nnn'], ['lll']]
    columns_list = ['name']
    my_df = MyDataFrameFactory.create(data_list, columns_list)

    # Name of the new column to be added
    col_name = 'philosophy'

    # Explicitly specify None values for the new column
    none_values = [None, None]

    # Add the new column with None values
    my_df.do_with_column(
        'add_column',
        data=none_values,
        col_name=col_name
    )

    # Construct the expected DataFrame
    expected_df = pd.DataFrame({
        'name': ['nnn', 'lll'],
        'philosophy': [None, None]
    })

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_add_column_with_all_values():
    # Initial data setup with a list of dictionaries
    data_list = [{'name': 'nnn'}, {'name': 'lll'}]
    my_df = MyDataFrameFactory.create(data_list)

    # Name of the new column to be added
    col_name = 'url'

    # Specify values for the new column
    values = ['url_nnn', 'url_lll']

    # Add the new column with None values
    my_df.do_with_column(
        'add_column',
        data=values,
        col_name=col_name
    )

    # Construct the expected DataFrame
    expected_df = pd.DataFrame({
        'name': ['nnn', 'lll'],
        'url': ['url_nnn', 'url_lll']
    })

    # Check whether the result matches the expected result
    pd.testing.assert_frame_equal(my_df.df, expected_df)


def test_add_column_with_missing_value():
    # Initial data setup with a list of dictionaries
    data_list = [{'name': 'nnn'}, {'name': 'lll'}]
    my_df = MyDataFrameFactory.create(data_list)

    # Name of the new column to be added
    col_name = 'url'

    # Specify values for the new column
    values = ['url_nnn']

    # Try to add the new column with None values
    with pytest.raises(ValueError) as err:
        my_df.do_with_column(
            'add_column',
            data=values,
            col_name=col_name
        )

    # Assert the error message
    assert str(err.value.args[0]) == (
        "Length of values (1) does not match length of index (2)"
    )


def test_get_col_type():
    """
    Tests whether the get_col_type method returns the correct dtype of the
    requested column of the dataframe wrapped in the class MyDataframe,
    comparing the return value of the method with the dtype of the wrapped
    dataframe.

    """
    data = {'name': ['nnn', 'lll']}
    my_df = MyDataFrameFactory.create(data)

    assert (my_df.do_with_column(
        'get_col_type',
        col_name='name'
    ) == my_df.df['name'].dtype)


@pytest.mark.parametrize("col_name, expected_col_type", [
    (
            'name',
            'object'
    ),
    (
            'age',
            'int64'
    ),
    (
            'info',
            'object'
    )
])
def test_col_type_dict(col_name, expected_col_type):
    """
    Tests whether the dtype of the data used to create the
    Dataframe matches the expected column type and whether it stays the same
    when the dataframe is created.

    """
    data = {
        'name': ['nnn', 'lll'],
        'age': [3, 44],
        'info': [7, 'some_info']
    }
    my_df = MyDataFrameFactory.create(data)

    col_type = pd.Series(data[col_name]).dtype

    assert col_type == expected_col_type
    assert (my_df.do_with_column(
        'get_col_type',
        col_name=col_name
    ) == col_type)


def test_get_col_index_by_col_name():
    dict1 = {
        'name': ['nnn'],
        'url': ['nnn_url']
    }
    dict2 = {
        'name': ['lll'],
        'url': ['lll_url']
    }
    my_df = MyDataFrameFactory.create(dict1)

    my_df.do_with_column(
        'add_column',
        data=dict2
    )

    '''
    my_df.df:
    __________________________________
        name            url            
    0   nnn             nnn_url
    1   lll             lll_url
    ==================================
    '''

    assert my_df.do_with_column(
        'get_col_index_by_col_name',
        col_name='name'
    ) == 0

    assert my_df.do_with_column(
        'get_col_index_by_col_name',
        col_name='url'
    ) == 1


def test_add_column_with_additional_row_order_not_preserved(
        a_statistics_dataframe,
        another_statistics_dataframe
):
    df1 = a_statistics_dataframe
    df2 = another_statistics_dataframe

    df_combined = df1.reindex(df1.index.union(df2.index))
    df_combined = df_combined.join(df2)

    print(df_combined)


def test_add_column_with_additional_row_order_preserved(
        a_statistics_dataframe,
        another_statistics_dataframe
):
    df1 = a_statistics_dataframe
    df2 = another_statistics_dataframe

    # Combine the two DataFrames
    combined_df = pd.concat([df1, df2], axis=1)

    # Display the combined DataFrame
    print(combined_df)
