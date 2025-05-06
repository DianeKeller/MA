"""
txt_strategy.py
---------------
Version 1.0, updated on 2025-05-01

"""

from settings import SettingCategories
from src.serialization.file import File
from src.serialization.serialization_strategy import SerializationStrategy


class TxtStrategy(SerializationStrategy):
    """
    This class is a concrete implementation of the SerializationStrategy
    interface for handling TXT (text) files.

    Attributes
    ----------
    DATA_STRUCTURE : str
        The data structure type this strategy can serialize and
        deserialize.

    FILE_TYPE : str
        The file type this strategy uses to serialize and deserialize data.
        This string is used in log messages.

    file : File | None
       Inherited from the SerializationStrategy interface. Represents
       the text file to be serialized or deserialized.


    Methods
    -------
    _add(data: str) -> None:
        Saves data to an existing file.

    _load() -> str:
        Deserializes and loads data from a TXT file as a string. If
        the file does not exist, returns None.

    _save(data: str) -> None:
        Serializes and saves a string to a TXT file.



    Notes
    -----
    The path where the text file is saved or loaded from is determined by
    settings specific to the TXT strategy.

    """

    DATA_STRUCTURE = "text"
    FILE_TYPE = "TXT"

    def __init__(
            self,
            file: File | None = None
    ) -> None:
        """
        Initializes a new instance of the TxtStrategy class.

        Sets the file path to use, retrieving it from the application settings.

        Parameters
        ----------
        file : File | None
            Custom 'File' object used for saving or loading data or removing a
            file from the file system. The 'File' object holds
            attributes detailing the name and extension of the file which
            is concerned by the intended file operations. If not provided,
            operations will require a file to be set later.

        """

        super().__init__(file)

        if self.file is not None:
            self.set_file_path(SettingCategories.TXT)

    def _save(self, data: str) \
            -> None:
        """
        Attempts to save the given data string to a TXT (text) file.

        Parameters
        ----------
        data : str
            The string to be serialized and saved to a TXT file.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        with open(
            self.file.full_path,
            'w',
            encoding="utf-8"
        ) as file:
            char_count = file.write(data)

            msg = "Saved %s characters to %s" % (
                char_count, self.file.full_path
            )
            self._log(msg, 'info')


    def _add(self, data: str) \
            -> None:
        """
        Attempts to add the given string to an existing TXT file.

        Parameters
        ----------
        data : str
            The string to be serialized and saved to a TXT file.

        """

        raise NotImplementedError

    def _load(self) \
            -> str:
        """
        Attempts to load data from a TXT (text) file into string variable.

        Returns
        -------
        str
            The loaded text if the file exists; otherwise, None.

        """

        # Ensure that Mypy recognizes that self.file is not None
        assert self.file is not None

        with open(
            self.file.full_path,
            'r',
            encoding='utf_8'
        ) as file:
            data = file.read()

        return data
