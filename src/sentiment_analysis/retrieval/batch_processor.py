"""
batch_processor.py
-------------------
Version 1.0, updated on 2024-12-04

"""

import numpy as np

from logger import Logger
from src.checkpoint_mixin import CheckpointMixin
from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.decorators.data_check_decorators import (
    requires_property,
    parameters_not_empty
)
from src.decorators.type_check_decorators import enforce_input_types
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.chunk_processor import ChunkProcessor
from src.sentiment_analysis.retrieval.custom_exceptions import (
    BatchFinishedException,
    LanguageFinishedException
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)


class BatchProcessor(LoggingMixin, CheckpointMixin):
    """
    BatchProcessor class.

    This class manages batch-wise processing of data samples for a specified
    language. It maintains checkpoints to resume processing after interruptions
    and aggregates results from processed batches.

    Attributes
    ----------
    batch_size : int
        The size of each batch, according to the entiment analysis
        configuration.

    config : SentimentAnalysisConfig
        The sentiment analysis configuratation.

    n_possible_batches : int
        The number of possible batches. Computed property.

    results : MyDataFrame
        The batches results.

    results_file_name : str
        The name of the results file.

    samples : MyDataFrame
        The samples to process in batches.

    target_n_batches: int
        The number of batches to process, according to the sentiment analysis
        configuration.

    target_n_samples : int
        The number of samples to process. Computed property


    Methods
    -------
    process_batch(batch_nr: int) -> None:
        Processes the givwn batch of the data.

    process_batches():
        Processes all batches for the given language.

    """

    @parameters_not_empty()
    @enforce_input_types
    def __init__(
            self,
            language: str,
            samples: MyDataFrame
    ):
        """
        Initializes the BatchProcessor with the specified parameters.

        Parameters
        ----------
        language : str
           Language code.

        samples : MyDataFrame
            The MyDataFrame with the samples to process in batches.

        """

        CheckpointMixin.__init__(
            self,
            element_type="batch",
            checkpoint_name=f"{samples.name}_batch_checkpoint"
        )

        self._results: MyDataFrame | None = None
        self._samples: MyDataFrame | None = None
        self._target_n_samples: int = 0
        self._n_possible_batches: int = 0
        self._results_file_name = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.language = language
        self.samples = samples

        # Configs used in this class
        self.config = SentimentAnalysisConfig()
        self.batch_size = self.config.get('batch_size')
        self.target_n_batches = self.config.get('n_batches')

    # region --- Properties
    @property
    def samples(self) \
            -> MyDataFrame:
        """
        Gets the samples to process in batches.
        """

        if self._samples is None:
            return MyDataFrameFactory.create()

        return self._samples

    @samples.setter
    def samples(self, samples: MyDataFrame) \
            -> None:
        """
        Sets the samples to process in batches.
        """

        self._samples = samples
        # Reset computed properties to enforce reload the next time they are
        # needed
        self._n_possible_batches = 0
        self._target_n_samples = 0

    @property
    def results(self) \
            -> MyDataFrame:
        """
        Gets the batches results.

        Returns a filled MyDataFrame instance after the batches have been
        processed. Empty or partially filled until then.

        """

        if self._results is None:
            return MyDataFrameFactory.create()

        return self._results

    @results.setter
    def results(self, results: MyDataFrame) \
            -> None:
        """
        Sets a MyDataFrame instance to store the batches results in.
        """

        self._results = results

    @property
    def n_possible_batches(self) \
            -> int:
        """
        Gets the number of possible batches.

        Gets the number of possible batches given the number of samples and
        the size of the batches.

        """

        if self._n_possible_batches == 0:
            self._compute_n_possible_batches()
        return self._n_possible_batches

    @n_possible_batches.setter
    def n_possible_batches(self, n_batches: int) \
            -> None:
        """
        Sets the number of possible batches.
        """

        self._n_possible_batches = n_batches

    @property
    def target_n_samples(self) \
            -> int:
        """
        Gets the number of samples to process.
        """

        if self._target_n_samples == 0:
            self._set_target_n_samples()

        return self._target_n_samples

    @target_n_samples.setter
    def target_n_samples(self, n_samples: int) \
            -> None:
        """
        Sets the number of samples to process.
        """

        self._target_n_samples = n_samples

    @property
    def results_file_name(self) \
            -> str:
        """
        Gets the name of the results file.
        """

        if not self._results_file_name:
            self._set_results_file_name()

        return self._results_file_name

    @results_file_name.setter
    def results_file_name(self, file_name: str) \
            -> None:
        """
        Sets the name of the results file.
        """

        self._results_file_name = file_name

    # endregion --- Properties

    # region --- Public Methods
    def process_batches(self):
        """
        Processes all batches for the given language.

        Creates a checkpoint at the end of each processed batch so that the
        program can resume after an interruption where it left off. Prevents
        infinite loops by tracking repeated batch numbers.

        Raises
        ------
        LanguageFinishedException
            If all batches for the language are processed.

        """

        start_batch_nr = self._get_start_nr()

        # Validate the checkpoint
        if start_batch_nr < 1 or start_batch_nr > self.target_n_batches:
            msg = (
                    "Invalid checkpoint: start_batch_nr = %d. "
                    "Must be between 1 and %d." % (
                        start_batch_nr,
                        self.target_n_batches
                    )
            )
            self._log(msg, "error")
            raise RuntimeError(msg)

        for batch_nr in range(start_batch_nr, 1 + self.target_n_batches):
            try:
                self.process_batch(batch_nr)

            except BatchFinishedException as err:
                if batch_nr >= self.target_n_batches:
                    msg = (
                            "All batches for language %s processed!" %
                            self.language
                    )
                    self._log(msg, 'info')
                    self._set_checkpoint(batch_nr + 1)
                    raise LanguageFinishedException(msg) from err

                # Log finished batch if nat all the batches have been processed
                msg = "Going to proceed with batch %d ..." % (
                        batch_nr + 1
                )
                self._log(msg, 'info')

            except Exception as err:
                # Log and handle unexpected errors
                msg = "Error processing batch  %d: %s" % (
                    batch_nr, str(err)
                )
                self._log(msg, 'error')
                raise

            # Since the current batch has been processed successfully,
            # the next batch number to start with is written into the
            # checkpoint file.
            self._set_checkpoint(batch_nr + 1)

    def process_batch(self, batch_nr: int) \
            -> None:
        """
        Processes the given batch of data.

        Extracts the part from the data that corresponds to the batch's number
        and size and passes the data on to the chunks processor to add and 
        execute the queries.

        Appends the results returned from the chunks processor to the results 
        file and reports any failed answers.

        Parameters
        ----------
        batch_nr : int
            The number of the batch.

        """

        batch_size = self.batch_size

        start_row = (batch_nr - 1) * batch_size
        end_row = start_row + batch_size

        # Extract batch from DataFrame
        batch_df = self.samples.df.iloc[start_row:end_row].copy()
        batch_samples = MyDataFrameFactory.create(
            batch_df, name=f"{self.samples.name}_batch_{str(batch_nr)}"
        )

        msg = f"Processing samples {start_row} - {end_row}"
        self._log(msg, 'info')

        try:
            chunk_processor = ChunkProcessor(
                self.language,
                batch_samples
            )
            batch_results = chunk_processor.process_chunks()

        except BatchFinishedException as err:
            raise BatchFinishedException(msg) from err

        self._add_to_results(batch_results, batch_nr)

    # endregion --- Public Methods

    # region --- Protected Methods

    def _add_to_results(
            self, batch_results: MyDataFrame, batch_nr: int
    ) -> None:
        """
        Adds the batch results to the existing results and saves the results.

        Adds the batch results to the existing results and saves the results
        file.

        Parameters
        ----------
        batch_results : MyDataFrame
            The batch results returned from the chunk processor.

        batch_nr : int
            The current batch number.

        """

        if batch_nr == 0:
            self.results = batch_results
            self.results.name = self.results_file_name
        else:
            self.results.do_with_row(
                "_append_rows", other=batch_results
            )

        self.results.save()

    def _set_target_n_samples(self) \
            -> None:
        """
        Computes the targeted number of samples.

        Computes the targeted number of samples from the targeted number of
        batches and the batch size and sets the corresponding property.

        """

        self.target_n_samples = self.target_n_batches * self.batch_size

    @requires_property('samples', 'batch_size')
    def _compute_n_possible_batches(self) \
            -> None:
        """
        Computes the possible number of batches and stores it as a property.
        """

        self.n_possible_batches = int(
            np.ceil(len(self.samples.df) / self.batch_size)
        )

    def _set_results_file_name(self) \
            -> None:
        """
        Sets the name of the file for the results of the processed batches.

        In this file, the sentiment predictions of all targeted batches for 
        the current language are collected.

        """

        self.results_file_name = (
            f"{self.samples.name}_{str(self.target_n_samples)}_results"
        )

    # endregion --- Protected Methods
