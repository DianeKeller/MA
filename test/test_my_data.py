"""
test_my_data.py
"""

import pytest

from src.data_structures.my_data import MyData
from src.data_structures.my_dataframe_factory import MyDataFrameFactory


def test_my_data(a_mydataframe):
    my_data = MyData(data=a_mydataframe, name="Test Data")
    assert my_data.name == "Test Data"
    assert my_data.data == a_mydataframe
    assert len(my_data.data.df) == 1
    assert my_data.n_cols == 6
    assert my_data.n_rows == 1


# Test adding a text length column
def test_add_text_length_column():
    my_df = MyDataFrameFactory.create(
        {"text": ["This is a test.", "Another test."]},
        name="Test Data"
    )
    my_data = MyData(data=my_df, name="Test Data")

    my_data.add_text_length_column()
    assert "length" in my_data.data.df.columns
    assert my_data.data.df["length"].tolist() == [15, 13]


@pytest.mark.parametrize('strategy, expected_n_sentences', [
    ('', [2, 1, 1, 1, 1, 2, 1]),
    ('Nltk', [2, 1, 1, 1, 1, 2, 1]),
    ('RegexWithColons', [2, 1, 2, 1, 1, 1, 2])
])
def test_add_sentence_count_column(strategy, expected_n_sentences,
                                   a_text_collection_df, ):
    my_data = MyData(data=a_text_collection_df, name="Test Data")

    my_data.add_sentence_count_column(strategy)
    assert "n_sentences" in my_data.data.df.columns
    assert my_data.data.df["n_sentences"].tolist() == expected_n_sentences


# Test adding a word count column
@pytest.mark.parametrize('strategy, expected_n_words', [
    ('', [3, 3]),
    ('NoPunctuation', [3, 3]),
])
def test_add_word_count_column(
        strategy, expected_n_words, a_text_collection_with_two_columns_df
):
    my_data = MyData(
        data=a_text_collection_with_two_columns_df, name="Test Data"
    )

    my_data.add_word_count_column(strategy)
    assert "n_words" in my_data.data.df.columns
    assert my_data.data.df["n_words"].tolist() == expected_n_words


def test_filter():
    dic = {
        "category": ["news", "not-news"],
        "text": ["This is news.", "This is not."]
    }
    my_df = MyDataFrameFactory.create(dic, name="Test Data")
    my_data = MyData(data=my_df, name="Test Data")

    filtered_data = my_data.filter_rows_by_col_value("category", "news")
    assert len(filtered_data.df) == 1
    assert filtered_data.df["text"].tolist() == ["This is news."]
