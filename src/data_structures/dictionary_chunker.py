"""
dictionary_chunker.py
-------------------------------
Version 1.0, updated on 2024-12-12

"""

from typing import Dict, Any, Tuple

from src.logging_mixin import LoggingMixin
from src.checkpoint_mixin import CheckpointMixin


class DictionaryChunker(LoggingMixin, CheckpointMixin):
    """
    DictionaryChunker class.

    This class splits a large dictionary into smaller chunks returned one by
    one. It keeps track of the generated and returned chunks by creating a
    checkpoint each time a chunk is returned and restarts where it left off
    if the program is interrupted and restarted.

    Attributes
    ----------
    chunk_size : int
        The number of items in each chunk. Defaults to 10.

    current_chunk : int
        The current chunk number, which keeps track of the progress.

    dic : Dict[str, Any]
        The dictionary to be chunked.

    iterator : Iterator
        An iterator over the dictionary items, used to yield chunks.

    name : str
        The name used for checkpointing. Defaults to 'chunk'.

    Methods
    -------
    get_next_chunk(self) -> Tuple[Dict[str, Any], int]:
        Gets the next chunk.

    Notes
    -----
    - If the program is interrupted, the chunker resumes from the last
      returned chunk based on the checkpoint saved previously.

    - If the dictionary is exhausted, further calls to 'get_next_chunk'
      will return empty chunks.

    """

    def __init__(
            self,
            dic: Dict[str, Any],
            chunk_size=10,
            name='chunk'
    ):
        """
        Constructor.

        Initializes the DictionaryChunker with the provided parameters.

        Parameters
        ----------
        dic : Dict[str, Any]
            The dictionary to be chunked.

        chunk_size : int, optional
            The number of items per chunk. Default is 10.

        name : str, optional
            The name used for checkpointing. Default is 'chunk'.

        """

        CheckpointMixin.__init__(
            self,
            element_type="chunk",
            checkpoint_name=f"{name}_chunk_checkpoint"
        )

        self.name: str = name
        self.dic: Dict[str, Any] = dic
        self.chunk_size: int = chunk_size

        self.current_chunk: int = self._get_start_nr()
        self.iterator = iter(dic.items())

        # Skip items in the iterator to reach the current chunk
        for _ in range(self.current_chunk - 1):
            try:
                next(self.iterator)
            except StopIteration:
                break

    # region --- Public Methods

    def get_next_chunk(self) \
            -> Tuple[Dict[str, Any], int]:
        """
        Gets the next chunk.

        Uses the CheckpointMixin to determine the next chunk to load and to
        set new checkpoints.

        Returns
        -------
        Tuple[Dict[str, Any], int]
            The next chunk and its number.

        """

        msg = f"Chunk starts with query n° {self.current_chunk}"
        self._log(msg, 'info')

        chunk = {}
        start = self.current_chunk
        end = self.current_chunk + self.chunk_size

        # If the program is interrupted before the current chunk has been
        # processed, the chunker will restart with the chunk that was left
        # unfinished.
        self._set_checkpoint(self.current_chunk, self.name)

        for _ in range(start, end):
            try:
                key, value = next(self.iterator)
                chunk[key] = value
                self.current_chunk += 1
            except StopIteration:
                break

        # Return the next chunk and its number.
        # For this, the incremented current_chunk number needs to be reset
        # to the previous state.
        return chunk, self.current_chunk - 1

    # endregion --- Public Methods
