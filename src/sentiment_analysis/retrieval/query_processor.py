"""
query_processor.py
------------------
Version 1.0, updated on 2024-12-15

"""

from typing import Dict, Any, List, no_type_check, cast

from logger import Logger
from src.authentication.hugging_face_strategy import HuggingFaceStrategy
from src.decorators.data_check_decorators import (
    requires_property,
    output_not_none,
    parameters_not_empty
)
from src.decorators.communication_error_handling_decorators import (
    query_error_handling
)
from src.decorators.type_check_decorators import enforce_input_types
from src.logging_mixin import LoggingMixin
from src.nlp.tokenization.tokenization_mixin import TokenizationMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.utils.data_utils import is_none_or_empty


class QueryProcessor(LoggingMixin, TokenizationMixin):
    """
    QueryProcessor class.

    This class is responsible for processing queries sent to a Hugging Face
    LLM API. It manages query payloads, handles API responses, extracts
    relevant results, and tracks failed queries for further analysis.

    Features:
    ---------
    - Validates and sends query payloads to the LLM API.
    - Processes API responses to extract sentiment predictions.
    - Implements error-handling mechanisms for API interactions.
    - Provides utilities for managing failed queries.
    - Includes configurable tokenization for response processing.

    Attributes
    ----------
    HF : HuggingFaceStrategy
        An instance of the HuggingFaceStrategy class for interacting with the
        LLM API

    failed_answers : List[Any]
        A class-level attribute to track failed answers across instances

    api : str
        The API endpoint to which queries are sent.

    payload : Dict[str, str]
        The query payload containing input data for the LLM.

    prompt_is_invalid : bool
        Tracks the validity of the prompt.


    Inherited Attributes
    --------------------
    DEFAULT_SENTENCE_STRATEGY : str
        The name of the default sentence strategy.

    DEFAULT_WORD_STRATEGY : str
        The name of the default word strategy.

    sentence_tokenizer : SentenceTokenizer
        The sentence tokenizer.

    word_tokenizer : WordTokenizer
        The word tokenizer.


    Methods
    -------
    process_query() -> str:
        Processes the query by sending it to the LLM API and handling the
        response.

    send_query() -> Dict[str, Any]:
        Sends the query with the payload to the LLM's API.


    Inherited Methods
    -----------------
    set_sentence_tokenizer(tokenization_strategy_name: str = '') -> None:
        Sets the sentence tokenizer using the specified strategy.

    set_word_tokenizer(tokenization_strategy_name: str = '') -> None:
        Sets the word tokenizer using the specified strategy.

    """
    HF = HuggingFaceStrategy()

    # Sentiment polarity values
    POSITIVE: str = "positive"
    NEGATIVE: str = "negative"
    NEUTRAL: str = "neutral"
    POSSIBLE_RESULTS = [NEGATIVE, POSITIVE, NEUTRAL]

    # Class variable to store the failed answers across all instances of the
    # class
    failed_answers: List[Any] = []

    @parameters_not_empty()
    @enforce_input_types
    def __init__(
            self,
            payload: Dict[str, str]
    ):
        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.payload: Dict[str, str] = payload
        self.prompt_is_invalid = False

        self.config = SentimentAnalysisConfig()

        api = self.config.get('api')
        if not api:
            raise CriticalException(
                self.logger, "No API given. Cannot send queries!"
            )

        self.api = api

    # region --- Properties

    # endregion --- Properties

    # region --- Public Methods

    def process_query(self) \
            -> str:
        """
        Processes the query by sending it to the LLM API.

        Extracts the predicted sentiment from the response.

        Returns
        -------
        str
            The predicted sentiment or an empty string if no valid sentiment
            is found.

        """

        response = self.send_query()

        return self._process_response(response)

    @requires_property('api', 'payload')
    @query_error_handling
    @no_type_check
    def send_query(self) \
            -> Dict[str, Any]:
        """
        Sends the query with the payload to the LLM's API.

        Sends the query with the payload defined in this class to the LLM's
        API.

        Returns
        -------
        Dict[str, Any]
            The response returned by the API.

        Raises
        ------
        Exception
            Unexpected exception of unknown type that could not be caught by
            the error handling decorator function.

        Notes
        -----
        - The query_error_handling decorator of this method catches various
          exceptions regarding the connection and the kind of response
          received.

          - ConnectionError
            If there is a problem with the connection to the API,
            the program waits 5 minutes before retrying to send the query.

          - KeyError
            This exception is raised when the Hugging Face rate limit is
            reached. In this case, the program needs to wait 1 hour for the
            rate limit to expire.

        - The query originally returns a List[Dict[str, Any]]. This is
          checked by the query_error_handling decorator, that in turn
          only returns the first element of the response list (response[0]) as
          the return value of this method. This change of data type may not be
          recognized by static type checkers, which may make them complain
          about the return type.

        """

        response = self.HF.query(self.api, self.payload)
        return cast(dict[str, Any], response)

    @classmethod
    def get_failed_answers(cls) \
            -> List[Any]:
        """
        Returns the list of failed answers.

        Returns
        -------
        List[Any]
            The list of failed answers that could not be processed correctly.

        """

        return cls.failed_answers

    @classmethod
    def flush_failed_answers(cls) \
            -> List[Any]:
        """
        Returns the list of failed answers and resets the list.

        Returns the list of failed answers and resets the list to an empty
        list.

        Returns
        -------
        List[Any]
            The list of failed answers before it is reset.

        """

        failed_answers = cls.failed_answers
        cls.failed_answers = []
        return failed_answers

    # endregion --- Public Methods

    # region --- Protected Methods

    def _process_response(self, response: Dict[str, str]) \
            -> str:
        """
        Extracts the predicted sentiment from the response provided by the LLM.

        The method performs the following steps:

        - Remove the input string from the output data.
        - Split the remaining string at punctuation marks.
        - Choose only the first element, which is the requested sentiment.
        - Remove leading and trailing whitespace

        Parameters
        ----------
        response : Dict[str, str]
            The response from the LLM.

        Returns
        -------
        str
           The predicted sentiment. An empty string if the result could
           not be matched with one of the expected results.

        """

        answer = self._remove_input_data_from_response(response)

        predicted_sentiment = self._extract_sentiment_from_answer(answer)

        if not predicted_sentiment:
            self.failed_answers.append(answer)

        return predicted_sentiment

    def _extract_sentiment_from_answer(self, answer: str) \
            -> str:
        """
        Extracts the sentiment from the answer.

        Splits the answer into words and returns the first word if this
        equals one of the sentiment polarities.

        Parameters
        ----------
        answer : str
            The answer returned from the API, minus the payload text of the
            query.

        Returns
        -------
        str
            The extracted sentiment. An empty string if the first word is not
            one of the expected sentiment polarities.

        """

        self.set_word_tokenizer('NoPunctuation')
        words = self.word_tokenizer.tokenize(answer)

        if is_none_or_empty(words):
            return ''

        predicted_sentiment = words[0]

        if predicted_sentiment not in ['negative', 'positive', 'neutral']:
            return ''

        return predicted_sentiment

    def _remove_input_data_from_response(self, response) \
            -> Any:
        """
        Removes the input data from the response text.

        Parameters
        ----------
        response : Dict[str, Any]
            The raw API response containing the generated text.

        Returns
        -------
        Any
            The response text with input data removed.

        """

        generated_text = self._get_generated_text(response)
        input_data = self._get_input_data_from_payload(self.payload)

        answer = generated_text.replace(input_data, "")
        return answer

    @output_not_none('input data')
    def _get_input_data_from_payload(self, payload: Dict[str, str]) \
            -> str:
        """
        Retrieves the input data from the query payload.

        Parameters
        ----------
        payload : Dict[str, str]
            The query payload.

        Returns
        -------
        str
            The input data string extracted from the payload.

        """

        return payload.get('inputs')

    @output_not_none('generated text')
    def _get_generated_text(self, data) \
            -> str:
        """
        Retrieves the generated text from the API response.

        Parameters
        ----------
        data : Dict[str, Any]
           The raw API response.

        Returns
        -------
        str
           The generated text contained in the response.

        """

        return data.get('generated_text')

    # endregion --- Protected Methods
