"""
test_fixtures.py
"""

import os

from settings import SettingCategories, get_setting


def test_temp_dir(temp_dir):
    assert os.path.exists(temp_dir)


def test_mock_csv_file(mock_csv_file, temp_dir):
    assert mock_csv_file.file_name == 'test'
    assert mock_csv_file.path == temp_dir
    assert mock_csv_file.full_path == os.path.join(temp_dir, "test.csv")
    assert mock_csv_file.extension == '.csv'


def test_mock_csv_strategy(mock_csv_strategy, temp_dir):
    assert mock_csv_strategy.file.file_name == 'test'
    assert mock_csv_strategy.file.full_path == os.path.join(temp_dir,
                                                            "test.csv")
    assert mock_csv_strategy.file.extension == '.csv'
    assert mock_csv_strategy.separator == get_setting(SettingCategories.CSV,
                                                      'SEPARATOR')
