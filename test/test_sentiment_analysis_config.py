"""
test_sentiment_analysis_config.py
"""

from src.sentiment_analysis.sentiment_analysis_config import \
    SentimentAnalysisConfig


def test_initialization_1():
    SentimentAnalysisConfig.reset_instance()

    SentimentAnalysisConfig(
        batch_size=200,
        n_batches=1,
        chunk_size=15,
        version='01'
    )
    assert SentimentAnalysisConfig.get('version') == '01'
    assert SentimentAnalysisConfig.get('batch_size') == 200

    SentimentAnalysisConfig.reset_instance()


def test_initialization():
    SentimentAnalysisConfig.reset_instance()

    SentimentAnalysisConfig(api='https://api.example.com', batch_size=400)

    assert SentimentAnalysisConfig.get('batch_size') == 400
    assert SentimentAnalysisConfig.get('api') == 'https://api.example.com'

    SentimentAnalysisConfig.reset_instance()


def test_singleton():
    SentimentAnalysisConfig.reset_instance()
    config1 = SentimentAnalysisConfig()
    config2 = SentimentAnalysisConfig()
    assert config1 is config2  # Both should be the same instance

    SentimentAnalysisConfig.reset_instance()


def test_reinitialization():
    SentimentAnalysisConfig.reset_instance()
    SentimentAnalysisConfig(api='https://api.example.com', batch_size=200)
    SentimentAnalysisConfig(api='https://api.changed.com', batch_size=300)
    assert SentimentAnalysisConfig.get('api') == 'https://api.example.com'
    assert SentimentAnalysisConfig.get('batch_size') == 200

    SentimentAnalysisConfig.reset_instance()


def test_set_and_get():
    SentimentAnalysisConfig.set('test_key', 'test_value')
    assert SentimentAnalysisConfig.get('test_key') == 'test_value'

    SentimentAnalysisConfig.reset_instance()


def test_remove():
    SentimentAnalysisConfig.set('test_key', 'test_value')
    SentimentAnalysisConfig.remove('test_key')
    assert SentimentAnalysisConfig.get('test_key') is None

    SentimentAnalysisConfig.reset_instance()


def test_update():
    SentimentAnalysisConfig.update(
        api='https://newapi.example.com',
        batch_size=300
    )
    assert SentimentAnalysisConfig.get('api') == 'https://newapi.example.com'
    assert SentimentAnalysisConfig.get('batch_size') == 300

    SentimentAnalysisConfig.reset_instance()
