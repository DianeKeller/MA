"""
my_ordered_dict_result.py
"""

from constants import INFINITY
from src.data_structures.my_ordered_dict import MyOrderedDict
from src.nlp.results.result import Result, print_mere_results
from src.utils.dict_utils import dict_to_string
from src.utils.print_utils import print_sep, print_subsep, print_wline


class MyOrderedDictResult(Result):
    def __init__(
            self,
            my_ordered_dict: MyOrderedDict
    ) -> None:

        super().__init__()

        self.__max_print_length = None
        self.__my_ordered_dict = None
        self.my_ordered_dict = my_ordered_dict

    # region --- Properties
    @property
    def my_ordered_dict(self) \
            -> MyOrderedDict:
        if not self.__my_ordered_dict:
            raise AttributeError("No MyOrderedDict given!")
        return self.__my_ordered_dict

    @my_ordered_dict.setter
    def my_ordered_dict(self, my_ordered_dict: MyOrderedDict) \
            -> None:
        self.__my_ordered_dict = my_ordered_dict

    @property
    def max_print_length(self):
        if not self.__max_print_length:
            self.max_print_length = INFINITY
        return self.__max_print_length

    @max_print_length.setter
    def max_print_length(self, length: int):
        self.__max_print_length = length

    # endregion --- Properties

    # region --- Methods

    def print(self):
        if self.my_ordered_dict.len < self.max_print_length:
            print(dict_to_string(self.my_ordered_dict.my_dict))
        else:
            self.restrict_print_length()

    def restrict_print_length(self) -> None:

        results = {}
        max_items = min(self.my_ordered_dict.len, self.max_print_length)
        for i in range(0, max_items):
            results[list(self.my_ordered_dict.my_dict.keys())[i]] = \
                list(self.my_ordered_dict.my_dict.values())[i]

        print(results)

    # endregion --- Methods


def print_results_part1(
        results: MyOrderedDictResult,
        title='Results',
        descr=None
):
    print_wline()
    print_sep()
    print(title)
    print_sep()

    if descr is not None:
        print(descr)
        print_subsep()

    print_mere_results(results)


def print_results_part2(
        results: MyOrderedDictResult,
        title='Results',
        descr=None
):
    print_sep()
    print(title)
    print_sep()

    if descr is not None:
        print(descr)
        print_subsep()

    print_mere_results(results)

    print_sep()
    print_wline()
