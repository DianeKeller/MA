"""
language_processor.py
---------------------
Version 1.0, updated on 2024-12-17

"""

from src.data_structures.my_data_frame import MyDataFrame
from src.decorators.data_check_decorators import parameters_not_empty
from src.decorators.type_check_decorators import enforce_input_types
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.batch_processor import BatchProcessor
from src.sentiment_analysis.retrieval.custom_exceptions import (
    LanguageFinishedException
)


class LanguageProcessor(LoggingMixin):
    """
    LanguageProcessor class.

    This class processes a given dataset of samples for a given language in
    batches.

    Attributes
    ----------
    language : str
        The language of the samples to be processed.

    samples : MyDataFrame
        A MyDataFrame object containing a pandas DataFrame with the samples
        to be processed

    Methods
    -------
    process_language()
        Processes the samples for the language in batches.

    """

    @parameters_not_empty()
    @enforce_input_types
    def __init__(
            self,
            language: str,
            samples: MyDataFrame
    ):
        """
        Constructor.

        Initializes a LanguageProcessor instance with the given parameters.

        Parameters
        ----------
        language : str
            The language of the samples to be processed.

        samples : MyDataFrame
            A MyDataFrame object containing a pandas DataFrame with the
            samples to be processed

        Raises
        ------
        CriticalException
            If the 'language' is empty or not a string, or if 'samples' is
            empty.

        TypeError
            If 'samples' is not an instance of 'MyDataFrame'.

        """

        self.language: str = language
        self.samples: MyDataFrame = samples

    def process_language(self) \
            -> None:
        """
        Processes the samples for the language in batches.

        This method uses the BatchProcessor class to process the
        samples in batches. If all samples have already been processed
        for the language, it logs an informational message and moves on
        to the next language.

        Raises
        ------
        LanguageFinishedException
            If processing for the current language is already complete.

        Notes
        -----
        The LanguageFinishedException is not re-raised but caught
        gracefully, logging an info message.

        """

        try:
            batch_processor = BatchProcessor(
                self.language,
                self.samples
            )
            batch_processor.process_batches()

            msg = ("Processing complete for %s without "
                   "having raised a LanguageFinishedException!" %
                   self.language)
            self._log(msg, 'warning')

        except LanguageFinishedException:
            msg = "Going to proceed with other languages if any ..."
            self._log(msg, 'info')
            return

        except Exception as err:
            self._log(f"An error occurred during batch processing: {str(err)}",
                      'error')
            raise  # Re-raise the exception after logging.
