"""
test_serialization_strategies.py
"""

import os
from typing import Dict

import pytest

from conftest import CANNOT_INSTANTIATE_ABSTRACT_CLASS, MISSING_IMPLEMENTATION
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.serialization import serialization_strategy as SAVING_STRATEGY
from src.serialization.serialization_factory import get_serializer
from src.utils.time_utils import current_date_time


def test_abstract_class():
    with pytest.raises(TypeError) as err:
        SAVING_STRATEGY.SerializationStrategy()
    assert (str(err.value) ==
            CANNOT_INSTANTIATE_ABSTRACT_CLASS
            + "SerializationStrategy"
            + MISSING_IMPLEMENTATION
            + "s '_add', '_load', '_save'")


@pytest.mark.parametrize("serializer, data", [
    (
            get_serializer(
                'json',
                "json_test_file_" + current_date_time()
            ),
            {
                'name': ['any_name'],
                'url': ['any_url']
            }
    ),
    (
            get_serializer(
                'csv',
                "csv_test_file_" + current_date_time()
            ),
            MyDataFrameFactory.create({
                'name': ['any_name'],
                'url': ['any_url']
            }).df
    ),
    (
            get_serializer(
                'pkl',
                "pkl_test_file_" + current_date_time()
            ),
            MyDataFrameFactory.create({
                'name': ['any_name'],
                'url': ['any_url']
            }).df
    ),
    (
            get_serializer(
                'json',
                "json_test_file_" + current_date_time()
            ),
            ['ccc', 'aaaa', 'fff', 'aaa', 'd', 'bb']
    ),
    (
            get_serializer(
                'txt',
                "txt_test_file_" + current_date_time()
            ),
            'The idea is good. But that U.S.A. poster-print costs $12.40...'
    )

])
def test_file_creation_strategies(serializer, data):
    """
    Test the file creation done by the serialization strategies.
    """
    print(data)

    file = serializer
    file.save(data)
    output = file.load()
    if isinstance(data, Dict) \
            or isinstance(data, str) \
            or isinstance(data, list):
        assert output == data
    else:
        assert output.equals(data)

    absolute_path = os.path.join(
        file.strategy.file.path,
        file.strategy.file.file_name + file.strategy.file.extension
    )

    assert os.path.exists(absolute_path)
    file.delete()
    assert not os.path.exists(absolute_path)

    with pytest.raises(Exception) as err:
        file.delete()

    # Assert the error message
    assert str(err.value.args[0]) == (f"File not found for deletion: "
                                      f"{absolute_path}")
