"""
test_my_regex.py
"""

import re

import pytest

from src.nlp.tokenization import word_tokenization_regex


@pytest.mark.parametrize("text, expected_matches", [
    (
            "This is a - very short but nice - little text.  "
            "It contains but 2 sentences.",
            [
                "This", "is", "a", "very", "short", "but", "nice",
                "little", "text", "It", "contains", "but", "2",
                "sentences"
            ]
    ),
    (
            "This is my little text. "
            "It contains three little sentence examples. "
            "They are pretty stupid, but still useful.",
            [
                "This", "is", "my", "little", "text", "It",
                "contains", "three", "little", "sentence", "examples",
                "They", "are", "pretty", "stupid", "but",
                "still", "useful"
            ]
    )
])
def test_regex_penn_treebank_wo_punctuation(text, expected_matches):
    """
    Tests the regex for Penn Treebank tokenization designed not to
    include punctuation marks and the like.

    The regex is used to split the text into words.

    """
    regex = word_tokenization_regex.regex_penn_treebank_wo_punctuation()
    assert regex is not None
    assert isinstance(regex, re.Pattern)
    assert re.search(regex, text)

    matches_and_positions = [
        {"pos": match.span(), "match": match.group().strip()}
        for match in re.finditer(regex, text)
    ]
    matches = [match["match"] for match in matches_and_positions]

    assert matches == expected_matches
