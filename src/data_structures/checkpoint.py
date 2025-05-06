"""
checkpoint.py
-------------
Version 1.0, updated on 2025-05-01

"""

from src.serialization.data_serialization_mixin import DataSerializationMixin


class Checkpoint(DataSerializationMixin):
    """
    Checkpoint class.

    This class represents a checkpoint, encapsulating data and its associated
    name. It also provides methods for serialization and deserialization of
    the checkpoint data through the 'DataSerializationMixin'.

    Attributes
    ----------
    data : str
        The textual content of the checkpoint.

    name : str
        The name associated with the checkpoint data, typically used as the
        file name when saving or loading data.

    file_name : str
        The name of the file derived from 'name', used for saving or loading
        the checkpoint data.

    file_type : str
        The file type used for serialization, defaulting to 'txt'.

    """

    def __init__(
            self,
            data: str = '',
            name: str = ''
    ) -> None:
        """
        Constructor.

        Initializes a new instance of the Checkpoint class with the provided
        parameters.

        Parameters
        ----------
        data : str
            The data to be stored in the checkpoint. Defaults to an empty
            string.

        name : str
            The name associated with the checkpoint data. Defaults to an empty
            string.

        """

        # Set the file type and file name for saving and loading the
        # previously processed data.
        self._data = data
        self._name = name

        self.file_name = self.name
        self.file_type = 'txt'

    @property
    def name(self) \
            -> str:
        """
        Gets the name of the data.
        """
        return self._name

    @name.setter
    def name(self, name: str) \
            -> None:
        """
        Sets the name of the data.
        """
        self._name = name

    @property
    def data(self) \
            -> str:
        """
        Gets the data.
        """
        return self._data

    @data.setter
    def data(self, data: str) \
            -> None:
        """
        Sets the data.
        """
        self._data = data
