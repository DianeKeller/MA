"""
test_string_search_utils.py
"""

import re

import pytest

from src.utils.string_search_utils import _search, \
    find_all_matches


def test_search():
    text = "This is a test. This, indeed, is another test!"
    pattern = re.compile(r'\btest\b')
    matches_and_positions, matches = _search(text, pattern)
    assert len(matches_and_positions) == 2
    assert len(matches) == 2
    assert matches == ['test', 'test']


@pytest.mark.parametrize('regex, n, expected',
                         [(r'\btest\b', 0, False),
                          (r'e', 4, 'e'),
                          (r'\btext\b', 1, 'text'),
                          (r'est', 2, 'est'),
                          (r'\bSample\b', 0, False)
                          ])
def test_find_all_matches(regex, n, expected):
    text = "Test text with some tests."
    pattern = re.compile(regex)
    results, matches = find_all_matches(text, pattern, verbose=False)
    assert len(results) == n
    assert len(matches) == n
    assert expected is False or matches[0]
