"""
test_word_tokenization.py
"""

from src.nlp.tokenization.tokenization_mixin import TokenizationMixin


class WordTokenizationTest(TokenizationMixin):
    def __init__(self):
        pass


def test_split_no_punctuation_strategy(some_sentences):
    tok = WordTokenizationTest()
    tok.set_word_tokenizer('NoPunctuation')

    for sentence in some_sentences:
        words = tok.word_tokenizer.tokenize(sentence)
        print(words[0])
