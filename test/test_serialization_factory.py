"""
test_serialization_factory.py
"""

import os

from src.serialization.csv_strategy import CsvStrategy
from src.serialization.json_strategy import JsonStrategy
from src.serialization.pkl_strategy import PklStrategy
from src.serialization.serialization_factory import _get_serialization_strategy
from src.serialization.serialization_strategy import SerializationStrategy
from src.serialization.txt_strategy import TxtStrategy


def test_get_csv_serialization_strategy(mock_csv_file, mock_csv_strategy):
    """
    Tests the serialization factory for a csv strategy.

    This test function checks if the strategy returned is an instance of the
    SerializationStrategy and CsvStrategy classes, and if the file path of the
    strategy matches the file path of the mock CSV strategy.

    Parameters
    ----------
    mock_csv_file
    mock_csv_strategy

    """
    strategy = _get_serialization_strategy('csv', os.path.join(
        mock_csv_file.path,
        mock_csv_file.file_name
    ))

    assert isinstance(strategy, SerializationStrategy)
    assert isinstance(strategy, CsvStrategy)
    assert strategy.file.full_path == mock_csv_strategy.file.full_path


def test_get_txt_serialization_strategy(mock_txt_file, mock_txt_strategy):
    """
    Tests the serialization factory for a txt strategy.

    This test function checks if the strategy returned is an instance of the
    SerializationStrategy and TxtStrategy classes, and if the file path of the
    strategy matches the file path of the mock TXT strategy.

    Parameters
    ----------
    mock_txt_file
    mock_txt_strategy

    """
    strategy = _get_serialization_strategy('txt', os.path.join(
        mock_txt_file.path,
        mock_txt_file.file_name
    ))

    assert isinstance(strategy, SerializationStrategy)
    assert isinstance(strategy, TxtStrategy)
    assert strategy.file.full_path == mock_txt_strategy.file.full_path


def test_get_json_serialization_strategy(mock_json_file, mock_json_strategy):
    """
    Tests the serialization factory for a json strategy.

    This test function checks if the strategy returned is an instance of the
    SerializationStrategy and JsonStrategy classes, and if the file path
    of the strategy matches the file path of the mock JSON strategy.

    Parameters
    ----------
    mock_json_file
    mock_json_strategy

    """
    strategy = _get_serialization_strategy('json', os.path.join(
        mock_json_file.path,
        mock_json_file.file_name
    ))

    assert isinstance(strategy, SerializationStrategy)
    assert isinstance(strategy, JsonStrategy)
    assert strategy.file.full_path == mock_json_strategy.file.full_path


def test_get_pkl_serialization_strategy(mock_pkl_file, mock_pkl_strategy):
    """

    Parameters
    ----------
    mock_pkl_file
    mock_pkl_strategy

    """
    strategy = _get_serialization_strategy('pkl', os.path.join(
        mock_pkl_file.path,
        mock_pkl_file.file_name
    ))

    assert isinstance(strategy, SerializationStrategy)
    assert isinstance(strategy, PklStrategy)
    assert strategy.file.full_path == mock_pkl_strategy.file.full_path
