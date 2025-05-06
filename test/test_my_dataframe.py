"""
test_my_dataframe.py
"""

import pandas as pd
import pytest

from src.data_sources.mad_tsc_workflow import MadTscWorkflow
from src.data_structures.my_dataframe_factory import MyDataFrameFactory


def new_dataframe():
    return MyDataFrameFactory.create()


def test_new_empty_dataframe():
    my_df = new_dataframe()
    assert isinstance(my_df.df, pd.DataFrame)
    assert my_df.n_cols == 0
    assert my_df.n_rows == 0


@pytest.mark.parametrize("cols, n_cols", [
    (
            ['col1', 'col2', 'col3'],
            3
    ),
    (
            [1, 2, 3, 4],
            4
    )
])
def test_new_empty_dataframe_with_columns(
        cols: list[str | int],
        n_cols: int
):
    my_df = MyDataFrameFactory.create(None, col_names=cols)
    assert isinstance(my_df.df, pd.DataFrame)
    assert my_df.n_cols == n_cols
    assert my_df.n_rows == 0


def test_create_dataframe_from_dict():
    data = {
        'name': ['nnn'],
        'url': ['nnn_url']
    }
    my_df = MyDataFrameFactory.create(data)
    assert isinstance(my_df.df, pd.DataFrame)

    assert my_df.do_with_field(
        'get_field_value',
        row_identifier=0,
        col_identifier='name'
    ) == 'nnn'

    assert my_df.do_with_field(
        'get_field_value',
        row_identifier=0,
        col_identifier='url'
    ) == 'nnn_url'

    assert my_df.df.columns.tolist() == ['name', 'url']
    assert my_df.col_names == ['name', 'url']


def test_create_dataframe_from_data_list_and_columns_list():
    data_list = ['nnn', 'lll']
    columns_list = ['name']
    my_df = MyDataFrameFactory.create(data_list, columns_list)

    # check whether the dataframe was created as expected
    expected_df = pd.DataFrame({'name': ['nnn', 'lll']})
    pd.testing.assert_frame_equal(my_df.df, expected_df)


@pytest.mark.parametrize("data, data_to_check, expected_result", [
    (
            {'name': ['nnn', 'lll']},
            {'name': [1]},
            False
    ),
    (
            {'name': ['nnn', 'lll']},
            {'name': ['kkk']},
            True
    ),
    (
            {'name': ['nnn', 'lll']},
            {'name': [1, 'ppp']},
            True
    ),
    (
            {'name': ['nnn', 'lll']},
            {'name': []},
            True
    ),
    (
            {'name': ['nnn', 'lll']},
            {'info': ['Hello', 'world']},
            False
    ),
])
def test_check_data_types_dict(data, data_to_check, expected_result):
    data = {'name': ['nnn', 'lll']}
    my_df = MyDataFrameFactory.create(data)

    assert my_df.do_with_row(
        '_check_data_types', data=data_to_check
    ) == expected_result


def test_find_single_value_cols():
    data = {
        'n_elements': [5110, 5110, 5110, 5110, 5110, 5110, 5110, 5110],
        # Same value across all datasets
        'min_length': [19, 26, 22, 24, 23, 24, 22, 22],
        'max_length': [563, 415, 776, 762, 790, 786, 604, 571],
        'mean_length': [209.39, 192.42, 209.88, 205.06, 198.45, 212.45, 200.30,
                        202.90],
        'median_length': [201, 188, 203, 197, 191, 204, 194, 196],
        'std_dev_length': [85.47, 72.13, 84.13, 81.82, 78.92, 86.28, 79.41,
                           79.46]
    }
    index = ['mad_tsc_de', 'mad_tsc_en', 'mad_tsc_es', 'mad_tsc_fr',
             'mad_tsc_it', 'mad_tsc_nl', 'mad_tsc_pt', 'mad_tsc_ro']
    my_df = MyDataFrameFactory.create(pd.DataFrame(data, index=index))

    assert list(my_df.single_value_cols.keys()) == ['n_elements']


def test_drop_single_value_cols():
    data = {
        'n_elements': [5110, 5110, 5110, 5110, 5110, 5110, 5110, 5110],
        # Same value across all datasets
        'min_length': [19, 26, 22, 24, 23, 24, 22, 22],
        'max_length': [563, 415, 776, 762, 790, 786, 604, 571],
        'mean_length': [209.39, 192.42, 209.88, 205.06, 198.45, 212.45, 200.30,
                        202.90],
        'median_length': [201, 188, 203, 197, 191, 204, 194, 196],
        'std_dev_length': [85.47, 72.13, 84.13, 81.82, 78.92, 86.28, 79.41,
                           79.46]
    }
    index = ['mad_tsc_de', 'mad_tsc_en', 'mad_tsc_es', 'mad_tsc_fr',
             'mad_tsc_it', 'mad_tsc_nl', 'mad_tsc_pt', 'mad_tsc_ro']
    my_df = MyDataFrameFactory.create(pd.DataFrame(data, index=index))
    assert 'n_elements' in my_df.col_names
    my_df.drop_single_value_cols()

    assert 'n_elements' not in my_df.col_names


def test_rows_and_cols_of_dataframe():
    data = {
        'mad_tsc_de': [1, 2, 3],
        'mad_tsc_en': [2, 3, 4],
        'mad_tsc_es': [6, 8, 2],
        'mad_tsc_fr': [2, 5, 6],
        'mad_tsc_it': [7, 9, 10],
        'mad_tsc_nl': [3, 4, 8],
        'mad_tsc_pt': [4, 6, 8],
        'mad_tsc_ro': [3, 8, 9]
    }

    # Create a DataFrame
    df_lengths = pd.DataFrame(data)
    my_df = MyDataFrameFactory.create(df_lengths)
    assert my_df.n_cols == 8
    assert my_df.n_rows == 3


def test_combine_subsets():
    mad_wf = MadTscWorkflow()
    mad_wf.load_subsets()
    suite = mad_wf.suite
    combined_subset = suite.combine_subsets(suite.subset_names[:2])

    assert combined_subset.name == 'mad_tsc_de_en'
    assert combined_subset.n_cols == 17
    assert combined_subset.n_rows == 5110
