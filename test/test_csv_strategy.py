"""
test_csv_strategy.py

This test module contains test functions for the CSV serialization strategy.

The test functions use parameters provided by fixtures in the conftest.py
file to enable the tests to use a temporary directory for file operations
instead of the production csv directory located under the project's file path.

Parameters
----------
temp_dir
    Temporary directory created by the fixture in conftest.py.

mock_csv_strategy
    CsvStrategy instance configured to use the temporary directory

"""

import os

import pandas as pd
import pytest

from src.serialization.serialization_factory import get_serializer
from src.utils.time_utils import current_date_time


def test_CsvStrategy():
    file_name = "csv_test_file_" + current_date_time()

    serializer = get_serializer('csv', file_name)

    assert (serializer.strategy.file.path ==
            'S:\\CODE\\PYTHON\\SentimentAnalysis\\data\\csv')


@pytest.mark.parametrize("dictionary", [
    (
            {'col1': [1, 2], 'col2': [3, 4], 'col3': [5, 6]}
    ),
    (
            {'name': ['any_name'], 'url': ['any_url']}
    )
])
def test_simple_save_and_read_dataframe(dictionary, temp_dir):
    """
    This test serves as a reference for the unit tests below.

    It does not test any module or function but shows how the serialization
    and deserialization of a dataframe work and result in an exact copy of
    the original dataframe.

    Parameters
    ----------
    temp_dir

    """
    df = pd.DataFrame(dictionary)

    # Use index=False to prevent pandas from writing row indices into the
    # CSV file.

    full_file_path = os.path.join(temp_dir, 'test.csv')

    df.to_csv(full_file_path, index=False)
    df_loaded = pd.read_csv(full_file_path)

    print(df)
    pd.testing.assert_frame_equal(df, df_loaded)


@pytest.mark.parametrize("dictionary", [
    (
            {'col1': [1, 2], 'col2': [3, 4], 'col3': [5, 6]}
    ),
    (
            {'name': ['any_name'], 'url': ['any_url']}
    )
])
def test_save_and_read_dataframe_with_separator(dictionary, mock_csv_strategy,
                                                temp_dir):
    """
    This test also serves as a reference for the unit tests below.

    It is slightly more complex than the simple test before, adding the
    indication of the separator which should be used in the CSV file,
    just to see how the serialization and deserialization of a dataframe work
    in this case and result in an exact copy of the original dataframe.

    Parameters
    ----------
    mock_csv_strategy
    temp_dir

    """

    # df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4], 'col3': [5, 6]})
    df = pd.DataFrame(dictionary)

    # Use index=False to prevent pandas from writing row indices into the
    # CSV file.

    full_file_path = os.path.join(temp_dir, 'test.csv')

    df.to_csv(full_file_path, sep=mock_csv_strategy.separator, index=False)
    df_loaded = pd.read_csv(full_file_path, sep=mock_csv_strategy.separator)

    pd.testing.assert_frame_equal(df, df_loaded)


def test_save_dataframe(mock_csv_strategy, temp_dir):
    """
    Test the save method of the CsvStrategy class.

    The original DataFrame is compared to the output of the pd.read_csv method.

    Parameters
    ----------
    mock_csv_strategy
    temp_dir

    Notes
    -----
    If the original dataframe is saved setting a certain separator,
    the separator must also be provided when loading the data from the CSV.

    """

    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4], 'col3': [5, 6]})
    mock_csv_strategy.save(df)

    # Verify file creation
    expected_file_path = os.path.join(temp_dir, "test.csv")
    assert os.path.exists(expected_file_path)

    # Verify content
    loaded_df = pd.read_csv(expected_file_path,
                            sep=mock_csv_strategy.separator)
    pd.testing.assert_frame_equal(df, loaded_df)


def test_load_dataframe(mock_csv_strategy, temp_dir):
    """
    Test the load method only of the CsvStrategy class.

    The original DataFrame is saved to the file using the pandas method
    "to_csv".

    Parameters
    ----------
    mock_csv_strategy
    temp_dir

    Notes
    -----
    If a certain separator is set in the loading operation as it is done in
    the load method of the CsvStrategy class, the separator must have been
    previously provided when the data was saved to the CSV file in order to
    get equal dataframes.

    """
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    file_path = os.path.join(temp_dir, "test.csv")
    df.to_csv(file_path, sep=mock_csv_strategy.separator, index=False)
    loaded_df = mock_csv_strategy.load()
    print(type(loaded_df))
    pd.testing.assert_frame_equal(df, loaded_df)


def test_save_n_load_dataframe(mock_csv_strategy, temp_dir):
    """
    Test the combined save and load methods of the CsvStrategy class.

    Parameters
    ----------
    mock_csv_strategy
    temp_dir

    """
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4], 'col3': [5, 6]})
    mock_csv_strategy.save(df)

    # Verify file creation
    expected_file_path = os.path.join(temp_dir, "test.csv")
    assert os.path.exists(expected_file_path)

    # Verify content
    loaded_df = mock_csv_strategy.load()
    print(type(loaded_df))
    pd.testing.assert_frame_equal(df, loaded_df)


def test_delete_file(mock_csv_strategy, temp_dir):
    """
    Test the delete method of the CsvStrategy class.

    Parameters
    ----------
    mock_csv_strategy
    temp_dir

    """

    file_path = os.path.join(temp_dir, "test.csv")
    open(file_path, 'a').close()  # Create an empty file
    mock_csv_strategy.delete()
    assert not os.path.exists(file_path)
