"""
test_file.py
"""

from src.serialization.serialization_factory import get_serializer
from src.utils.time_utils import current_date_time


def test_csv_file():
    file_name = "csv_test_file_" + current_date_time()
    serializer = get_serializer('csv', file_name)
    assert serializer.strategy.file.extension == '.csv'


def test_json_file():
    file_name = "json_test_file_" + current_date_time()
    serializer = get_serializer('json', file_name)

    assert serializer.strategy.file.extension == '.json'
