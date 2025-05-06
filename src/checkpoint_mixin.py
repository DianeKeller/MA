"""
checkpoint_mixin.py
-------------------
Version 1.0, updated on 2025-05-01

"""

from src.data_structures.checkpoint import Checkpoint
from src.utils.data_utils import is_none_or_empty


class CheckpointMixin:
    """
    CheckpointMixin class

    Mixin class for handling checkpoints.

    Attributes
    ----------
    checkpoint : Checkpoint
        The checkpoint.

    checkpoint_name : str
        The checkpoint_name.


    Usage
    -----
    - Add the CheckpointMixin as a superclass to a class that needs to
      handle checkpoints.

    - In the constructor of the class, initialize the CheckpointMixin with
      the required parameters.

    - Use the mixin's protected methods, e.g. _get_start_nr,
      _set_checkpoint.

    >>> from src.data_structures.my_data_frame import MyDataFrame

    >>> class BatchProcessor(CheckpointMixin):
    >>>     def __init__(self, samples: MyDataFrame):
    >>>         CheckpointMixin.__init__(
    ...            self,
    ...            element_type="batch",
    ...            checkpoint_name=f"{samples.name}_batch_checkpoint"
    ...         )
    >>>     def process_batches(self, samples: MyDataFrame):
    >>>         start_batch_nr = self._get_start_nr()
    >>>         for i in range(start_batch_nr, len(samples.df)+1):
    >>>             ...
    >>>             self._set_checkpoint(i + 1)

    """

    def __init__(self, element_type: str = '', checkpoint_name: str = '') \
            -> None:
        """
        Constructor.

        Initializes a new instance of the CheckpointMixin class with the
        provided parameters.

        Parameters
        ----------
        element_type : str
            The element type.

        checkpoint_name : str
            The checkpoint name.

        """

        self._checkpoint: Checkpoint | None = None
        self._checkpoint_name = checkpoint_name
        self.element_type = element_type

    # region --- Properties
    @property
    def checkpoint(self) \
            -> Checkpoint:
        """
        Returns the checkpoint.

        """

        if self._checkpoint is None:
            self._set_checkpoint()
        return self._checkpoint

    @checkpoint.setter
    def checkpoint(self, checkpoint: Checkpoint) \
            -> None:
        """
        Sets the checkpoint.

        """

        self._checkpoint = checkpoint

    @property
    def checkpoint_name(self) \
            -> str:
        """
        Returns the checkpoint_name.

        """

        return self._checkpoint_name

    @checkpoint_name.setter
    def checkpoint_name(self, checkpoint_name: str) \
            -> None:
        """
        Sets the checkpoint_name.

        """

        self._checkpoint_name = checkpoint_name

    # endregion --- Properties
    # region --- Public Methods
    # endregion --- Public Methods

    # region --- Protected Methods

    def _set_checkpoint(self, el_nr: int = 1, name: str = '') \
            -> None:
        """
        Sets and saves a checkpoint with the given element number.

        If the checkpoint property is not set yet, the given name is used to
        create it.

        Parameters
        ----------
        name : str
            Name of the checkpoint (equals a part of its file name).
            Defaults to an empty string. If needed to create a new
            checkpoint object, the empty string is replaced by a default name.

        el_nr: int
            The number of the element to set the checkpoint for. Defaults to 1.

        """

        if not self._checkpoint_exists():

            if not name:
                name = self._create_default_checkpoint_name()

            self.checkpoint = Checkpoint(name=name)
            if self.checkpoint.can_load():
                self.checkpoint.load()
            else:
                self.checkpoint.data = str(el_nr)
                self.checkpoint.save()

        if el_nr > int(self.checkpoint.data):
            self.checkpoint.data = str(el_nr)
            self.checkpoint.save()

    def _create_default_checkpoint_name(self) \
            -> str:
        """
        Creates a default checkpoint name.

        Returns an existing checkpoint name or a default checkpoint name
        newly created from the element type.

        Returns
        -------
        str
            The existing or newly created checkpoint name.

        """

        return self._checkpoint_name or f'{self.element_type}_checkpoint'

    def _checkpoint_exists(self) \
            -> bool:
        """
        Checks whether the checkpoint property is set.

        Returns
        -------
        bool
            True if the property is set, False otherwise

        """

        return self._checkpoint is not None

    def _checkpoint_has_name(self) \
            -> bool:
        """
        Checks whether the checkpoint's name is set.

        Returns
        -------
        bool
            True if the name is set, False otherwise or if the checkpoint
            does not exist or has no name.

        """

        if (
                not self._checkpoint_exists() or
                is_none_or_empty(self._checkpoint.name)
        ):
            return False

        return True

    def _get_start_nr(self) \
            -> int:
        """
        Gets the number of the element to start with.

        Retrieves the start element number from the elements' checkpoint or
        sets the start number to 1 and saves the newly created Checkpoint
        with this number.

        Returns
        -------
        int
            The start number.

        """

        if self.checkpoint.can_load():
            self.checkpoint.load()
        else:
            self._set_checkpoint(1)

        return int(self.checkpoint.data.strip())

    # endregion --- Protected Methods
