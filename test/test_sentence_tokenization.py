"""
test_sentence_tokenization.py
"""

from src.nlp.tokenization.tokenization_mixin import TokenizationMixin


class SentenceTokenizationTest(TokenizationMixin):
    def __init__(self):
        pass


def test_nltk_strategy(some_sentences):
    tok = SentenceTokenizationTest()
    tok.set_sentence_tokenizer('Nltk')

    for sentence in some_sentences:
        sentences = tok.sentence_tokenizer.tokenize(sentence)
        for s in sentences:
            print(s)
