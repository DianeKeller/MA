"""
test_statistics_factory.py
"""

import pytest

from src.data_structures.item_list import ItemList
from src.stats.statistics_factory import get_analyzer
from src.stats.statistics_strategy import StatisticsStrategy


@pytest.fixture()
def mock_item_list():
    return ItemList(elements=["a", "b", "c"], name="TestList")


@pytest.mark.parametrize("category, expected_class_name", [
    (
            "frequency", "FrequencyStrategy"
    ),
    (
            "LENGTH", "LengthStrategy"
    )
])
def test_get_statistics_strategy(
        mock_item_list,
        category,
        expected_class_name
):
    analyzer = get_analyzer(category, mock_item_list)

    assert isinstance(analyzer.strategy, StatisticsStrategy)
    assert analyzer.strategy.__class__.__name__ == expected_class_name
    assert analyzer.strategy.items == mock_item_list
    print(analyzer.strategy.to_string())


@pytest.mark.parametrize("category, expected_class_name", [
    (
            "abc", ""
    ),
])
def test_get_statistics_strategy_invalid_category(
        mock_item_list,
        category,
        expected_class_name
):
    with pytest.raises(ImportError) as err:
        get_analyzer(category, mock_item_list)
    assert "not found" in str(err.value)
