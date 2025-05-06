"""
prompts.py
-----------------
Version 1.0, updated on 2025-01-30

"""

from __future__ import annotations

from typing import List

from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.utils.print_utils import print_in_box
from type_aliases import PromptsDictType


class Prompts:
    """
    Prompts class.

    Manages and displays prompts for sentiment analysis.

    This class encapsulates a MyDataFrame object containing prompts,
    allowing for easy creation, storage, and display of the data.

    Attributes
    ----------
    data : MyDataFrame
        A MyDataFrame object holding prompts, created from the
        provided dictionary.


    Methods
    -------
    print() -> None:
        Prints a summary of the prompts and the full DataFrame.


    """

    def __init__(
            self,
            data_dict: PromptsDictType,
            name: str = ''
    ):
        """
        Constructor.

        Initializes the Prompts instance with a dictionary of prompts.

        Parameters
        ----------
        data_dict : PromptsDictType
            A dictionary containing prompts, where each key is
            a prompt number and each value is a dictionary with
            positions as keys and variants of text that can be inserted into
            a query at the given position.

        name : str
            Name identifier for the MyDataFrame. Default is an empty string.

        """

        self.data: MyDataFrame = MyDataFrameFactory.create(
            data_dict, name=name
        )

    def print(self) \
            -> None:
        """
        Prints a summary of the prompts and the full DataFrame.

        This method displays a summary box of the DataFrame's name
        and descriptive statistics, such as counts and distributions,
        along with the DataFrame's full content for a detailed view.

        """

        print_in_box(self.data.name, self.data.df.describe())
        print_in_box(self.data.name, self.data.df)

    @staticmethod
    def merge(prompts_list: List[Prompts]) \
            -> Prompts:
        lst: List[MyDataFrame] = [prompts.data for prompts in prompts_list]
        my_df = lst.pop(0)
        my_df = my_df.do_with_row('join', my_df_lst=lst)

        prompts = Prompts({})
        prompts.data = my_df

        return prompts

# region --- Properties

# endregion --- Properties

# region --- Public Methods

# endregion --- Public Methods

# region --- Protected Methods

# endregion --- Protected Methods
