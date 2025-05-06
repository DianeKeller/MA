"""
test_join_dataframes.py
"""

import pandas as pd
from pandas import DataFrame

from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.utils.data_comparison_utils import are_equal


def test_join_dataframes_different_cols():
    # Example DataFrames
    df1 = pd.DataFrame({
        'A': ['A0', 'A1', 'A2'],
        'B': ['B0', 'B1', 'B2']
    }, index=['K0', 'K1', 'K2'])

    df2 = pd.DataFrame({
        'C': ['C0', 'C1', 'C2'],
        'D': ['D0', 'D1', 'D2']
    }, index=['K0', 'K1', 'K2'])

    # Joining on the index
    df_joined = df1.join(df2)
    print(df_joined)


def test_join_dataframes_equal_colum_names():
    # Example DataFrames
    df1 = pd.DataFrame({
        'A': ['A0', 'A1', 'A2'],
        'B': ['B0', 'B1', 'B2']
    }, index=['K0', 'K1', 'K2'])

    df2 = pd.DataFrame({
        'A': ['C0', 'C1', 'C2'],
        'B': ['D0', 'D1', 'D2']
    }, index=['K0', 'K1', 'K2'])

    # Joining on the index
    df_joined = df1.join(df2, lsuffix='_df1', rsuffix='_df2')
    print(df_joined)


def test_join_dataframes_equal_colum_names_but_different_n_cols():
    # Example DataFrames
    df1 = pd.DataFrame({
        'A': ['A0', 'A1', 'A2'],
        'B': ['B0', 'B1', 'B2']
    }, index=['K0', 'K1', 'K2'])

    df2 = pd.DataFrame({
        'A': ['C0', 'C1', 'C2'],
        'B': ['D0', 'D1', 'D2'],
        'C': ['E0', 'E1', 'E2']
    }, index=['K0', 'K1', 'K2'])

    # Joining on the index
    df_joined = df1.join(df2, lsuffix='_df1', rsuffix='_df2')
    print(df_joined)


def test_join_dataframes_equal_colum_names_and_values():
    # Example DataFrames
    df1 = pd.DataFrame({
        'A': ['A0', 'A1', 'A2'],
        'B': ['B0', 'B1', 'B2']
    }, index=['K0', 'K1', 'K2'])

    df2 = pd.DataFrame({
        'A': ['A0', 'A1', 'A2'],
        'B': ['D0', 'D1', 'D2']
    }, index=['K0', 'K1', 'K2'])

    # Joining on the index
    df_joined = df1.join(df2, lsuffix='_df1', rsuffix='_df2')
    print(df_joined)


def test_compare_dataframes_and_drop_identical_cols():
    df1 = pd.DataFrame({
        'A': ['A0', 'A1', 'A2'],
        'B': ['B0', 'B1', 'B2']
    }, index=['K0', 'K1', 'K2'])

    df2 = pd.DataFrame({
        'A': ['A0', 'A1', 'A2'],
        'B': ['B0', 'B1', 'D2']
    }, index=['K0', 'K1', 'K2'])

    my_df1 = MyDataFrameFactory.create(df1)
    names_identical_cols = my_df1.do_with_column('find_identical_cols',
                                                 other=df2)

    # Compare the DataFrames to create a boolean DataFrame
    # 'Identical' is a DataFrame with boolean values in each field, meaning
    # the compared field in the given position is identical or not.
    identical = df1 == df2
    assert isinstance(identical, DataFrame)
    assert type(identical) == DataFrame

    # Identify columns where all values are identical
    columns_to_drop = identical.columns[identical.all()]

    assert names_identical_cols == columns_to_drop

    # Drop these columns from df2
    df2_filtered = df2.drop(columns=columns_to_drop)
    print(df2_filtered)

    expected_df = pd.DataFrame({
        'B': ['B0', 'B1', 'D2']
    }, index=['K0', 'K1', 'K2'])

    assert are_equal(df2_filtered, expected_df)
