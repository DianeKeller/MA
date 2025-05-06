"""
file_loader.py
--------------
Version 1.0, updated on 2024-12-04

"""

import os
from typing import List

import settings
from logger import Logger
from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.logging_mixin import LoggingMixin
from src.serialization.directory import Directory
from src.utils.data_utils import is_none_or_empty


class FileLoader(LoggingMixin):
    """
    FileLoader class.
    
    """

    def __init__(
            self,
            language: str = 'en',
            sub_dir: str = ''
    ):
        """
        Initializes the ChunkLoader with the specified parameters.

        Parameters
        ----------
        language : str
           Language code (default is 'en').

        sub_dir : str
            Name of the subdirectory in which are stored the files to be
            loaded. Defaults to an empty string.

        """

        self._current_dir = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.language: str = language
        self.sub_dir: str = sub_dir
        self.files: List[MyDataFrame] = []

        self._set_dir()
        self._load_files()

    @property
    def current_dir(self) \
            -> Directory:
        if not self._current_dir:
            self._set_dir()

        return self._current_dir

    @current_dir.setter
    def current_dir(self, path_name: str) \
            -> None:
        self._current_dir = Directory(path_name)

    # region --- Properties

    # endregion --- Properties

    # region --- Public Methods

    # endregion --- Public Methods

    # region --- Protected Methods

    def _set_dir(self) \
            -> None:
        """
        Sets the subdirectory from which the file(s) are to be loaded.

        """

        if is_none_or_empty(self.sub_dir):

            self.current_dir = os.path.join(settings.DATA_ROOT, 'csv')

        else:

            current_dir = os.path.join(settings.DATA_ROOT, 'csv', self.sub_dir)

            if not os.path.exists(current_dir):
                msg = "Invalid path: %s" % current_dir
                self._log(msg, 'error')
                raise FileNotFoundError(msg)

            self.current_dir = current_dir

    def _load_files(self) \
            -> None:
        """
        Loads the files and sets the data property.

        Loads the files from the main CSV data directory or from the
        subdirectory of the CSV data directory, if the 'sub_dir' property is
        set with a non-empty string.

        Returns
        -------

        """

        file_names = self._get_file_names_by_language(self.language)

        for file_name in file_names:
            data = MyDataFrameFactory.create(name=file_name)
            data.file_type = 'csv'
            data.sub_dir = self.sub_dir
            data.load()
            self.files.append(data)

    def _get_file_names_by_language(self, language: str) \
            -> List[str]:
        """
        Get all file names in directory that correspond to the given language.

        Parameters
        ----------
        language : str
            Language code, e.g. 'en'

        Returns
        -------
        List[str]
            List of file names.

        """

        return self.current_dir.get_file_names_by_string(f'_{language}_')

    # endregion --- Protected Methods
