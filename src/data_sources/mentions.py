"""
mentions.py
-----------
Version 1.0, updated on 2024-09-03

"""

from src.data_structures.str_series import StrSeries


class Mentions:
    """
    Mentions class.

    Handles operations related to mentions within the dataset.

    Attributes
    ----------
    data : StrSeries
        A series containing the mentions data.

    Methods
    -------
    frequency_diagram(min_freq: int = 2, max_n: int = 30) -> None:
        Displays a frequency diagram of mentions.

    """

    def __init__(self, mentions_series: StrSeries):
        """
        Initializes the Mentions class with a series of mentions.

        Parameters
        ----------
        mentions_series : StrSeries
            A string series containing mention data.

        """
        self.data = mentions_series

    # region --- Properties

    # endregion --- Properties

    # region --- Public Methods

    def frequency_diagram(self, min_freq: int = 2, max_n: int = 30) -> None:
        """
        Displays a frequency diagram of mentions.

        Parameters
        ----------
        min_freq : int, optional
            The minimum frequency to display, by default 2.

        max_n : int, optional
            The maximum number of mentions to display, by default 30.

        """

        self.data.frequencies_diagram(
            x_label="Mention",
            min_freq=min_freq,
            max_n=max_n
        )

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
