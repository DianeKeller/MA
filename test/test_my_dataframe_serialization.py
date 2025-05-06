"""
test_my_dataframe_serialization.py
"""

import os

import pandas as pd

from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.utils.time_utils import current_date_time


def test_save_csv(mock_csv_strategy, temp_dir):
    my_df = MyDataFrameFactory.create({
        'name': ['nnn'],
        'url': ['nnn_url']
    }, name="dataframe_test_file_" + current_date_time())

    # Make the my_df serializer use the path defined in the mock strategy
    my_df.serializer.file.path = mock_csv_strategy.file.path
    my_df.serializer.file.extension = mock_csv_strategy.file.extension

    my_df.save()
    # Verify file creation
    expected_file_path = os.path.join(temp_dir, my_df.file_name + '.csv')
    assert os.path.exists(expected_file_path)

    # Verify content
    loaded_df = my_df.serializer.load()
    print(type(loaded_df))
    pd.testing.assert_frame_equal(my_df.df, loaded_df)


def test_save_default(mock_pkl_strategy, temp_dir):
    my_df = MyDataFrameFactory.create({
        'name': ['nnn'],
        'url': ['nnn_url']
    }, name="dataframe_test_file_" + current_date_time())

    # Make the my_df serializer use the path defined in the mock strategy
    my_df.serializer.file.path = mock_pkl_strategy.file.path

    my_df.save()
    # Verify file creation
    expected_file_path = os.path.join(temp_dir, my_df.file_name + '.pkl')
    assert os.path.exists(expected_file_path)

    # Verify content
    loaded_df = my_df.serializer.load()
    print(type(loaded_df))
    pd.testing.assert_frame_equal(my_df.df, loaded_df)


def test_load(mock_csv_strategy, temp_dir):
    my_df = MyDataFrameFactory.create({
        'name': ['nnn'],
        'url': ['nnn_url']
    }, name="dataframe_test_file_" + current_date_time())

    # Make the my_df serializer use the path defined in the mock strategy
    my_df.serializer.file.path = mock_csv_strategy.file.path
    my_df.serializer.file.extension = mock_csv_strategy.file.extension
    my_df.save()

    output = my_df.serializer.load()
    assert output.equals(my_df.df)
