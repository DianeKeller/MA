"""
test_stat_frequency_strategy.py
"""

from src.data_structures.item_list import ItemList
from src.stats.statistics_factory import get_analyzer


def test_char_frequencies():
    chars = ItemList(['T', 'h', 'i', 's', ' ', 'i', 's', ' ', 'm',
                      'y', ' ', 'l', 'i', 't', 't', 'l', 'e', ' ', 't', 'e',
                      'x', 't', '.'], "characters")
    expected_freqs = {'t': 4, 'h': 1, 'i': 3, 's': 2, ' ': 4, 'T': 1, 'm': 1,
                      'y': 1, 'l': 2, 'e': 2, 'x': 1, '.': 1}

    stats = get_analyzer("frequency", chars)
    freqs = stats.strategy

    assert freqs.items_and_values.my_dict == expected_freqs
    assert freqs.highest_value_ids == [4, 13]
    assert freqs.lowest_value_ids == [0, 1, 8, 9, 20, 22]
    assert freqs.ids_near_means == {0: 1, 1: 1, 3: 2, 8: 1, 9: 1,
                                    11: 2,
                                    16: 2, 20: 1, 22: 1}
    assert freqs.ids_near_median == {3: 2, 11: 2, 16: 2, 0: 1, 1: 1, 8: 1,
                                     9: 1, 20: 1, 22: 1}
