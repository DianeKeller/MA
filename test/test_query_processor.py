"""
test_query_processor.py
"""

import pytest
from pytest_mock import MockerFixture

from src.sentiment_analysis.retrieval.query_processor import QueryProcessor


@pytest.fixture
def payload():
    return {"inputs": "This is a test"}


@pytest.fixture
def mock_config(mocker):
    mock_config = mocker.patch(
        'src.sentiment_analysis.retrieval.query_processor.SentimentAnalysisConfig'
    )
    mock_config.return_value.get.return_value = 'fake_api_key'
    return mock_config


@pytest.fixture
def query_processor(payload, mock_config):
    return QueryProcessor(payload=payload)


def test_initialization(payload, mock_config):
    processor = QueryProcessor(payload)
    assert processor.payload == payload
    assert processor.prompt_is_invalid is False
    assert processor.api == 'fake_api_key'
    mock_config.return_value.get.assert_called_once_with('api')


def test_send_query(mocker, query_processor):
    mocker.patch(
        'src.sentiment_analysis.retrieval.query_processor.HuggingFaceStrategy.query',
        return_value=[{"generated_text": "positive"}]
    )

    response = query_processor.send_query()
    assert response["generated_text"] == "positive"
    query_processor.HF.query.assert_called_once_with(
        query_processor.api,
        query_processor.payload
    )


def test_process_query(mocker, query_processor):
    mocker.patch.object(QueryProcessor, 'send_query',
                        return_value={"generated_text": "positive"})
    result = query_processor.process_query()
    assert result == "positive"


def test_process_query_with_invalid_sentiment(mocker, query_processor):
    mocker.patch.object(QueryProcessor, 'send_query', return_value={
        "generated_text": "This is not a sentiment"})
    result = query_processor.process_query()
    assert result == ""
    assert query_processor.failed_answers == ["This is not a sentiment"]


def test_failed_answers_handling(query_processor):
    # Clear any pre-existing failed answers
    query_processor.failed_answers.clear()

    # Add failed answers for testing
    query_processor.failed_answers.extend(
        ["failed response 1", "failed response 2"])

    failed_answers = query_processor.get_failed_answers()
    assert failed_answers == ["failed response 1", "failed response 2"]

    flushed_answers = query_processor.flush_failed_answers()
    assert flushed_answers == ["failed response 1", "failed response 2"]
    assert query_processor.failed_answers == []


def test_remove_input_data_from_response(query_processor):
    response = {"generated_text": "This is a test positive"}
    result = query_processor._remove_input_data_from_response(response)
    assert result == " positive"


def test_extract_sentiment_from_answer(mocker: MockerFixture, query_processor):
    # Mock the set_word_tokenizer method
    mock_set_word_tokenizer = mocker.patch.object(query_processor,
                                                  'set_word_tokenizer')

    # Mock the word_tokenizer property using mocker.PropertyMock
    mock_word_tokenizer = mocker.patch.object(type(query_processor),
                                              'word_tokenizer',
                                              new_callable=mocker.PropertyMock)
    mock_word_tokenizer.return_value.tokenize.return_value = ["positive"]

    # Execute the method under test
    sentiment = query_processor._extract_sentiment_from_answer("positive")

    # Verify the result
    assert sentiment == "positive"

    # Ensure set_word_tokenizer was called once
    mock_set_word_tokenizer.assert_called_once_with('NoPunctuation')

    # If it should be called twice, use:
    # assert mock_set_word_tokenizer.call_count == 2
    # Or:
    # mock_set_word_tokenizer.assert_has_calls(
    #   [mocker.call('NoPunctuation'), mocker.call('NoPunctuation')]
    # )


def test_get_input_data_from_payload(query_processor):
    result = query_processor._get_input_data_from_payload(
        query_processor.payload)
    assert result == "This is a test"


def test_get_generated_text(query_processor):
    data = {"generated_text": "This is a generated text"}
    result = query_processor._get_generated_text(data)
    assert result == "This is a generated text"
