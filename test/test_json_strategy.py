"""
test_json_strategy.py
"""

from src.serialization.serialization_factory import get_serializer
from src.utils.time_utils import current_date_time


def test_JsonStrategy():
    serializer = get_serializer(
        'json',
        "json_test_file_" + current_date_time()
    )

    assert (serializer.strategy.file.path ==
            'S:\\CODE\\PYTHON\\SentimentAnalysis\\data\\json')
