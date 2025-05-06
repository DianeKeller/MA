"""
labels.py
---------
Version 1.0, updated on 2024-12-17

"""

from typing import List, Tuple

from pandas import Series

from logger import Logger
from src.data_structures.item_collection_factories import ItemSeriesFactory
from src.data_structures.item_series import ItemSeries
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.print_utils import print_in_box


class Labels(LoggingMixin):
    def __init__(
            self,
            elements: Series | None = None,
            name: str = ""
    ):
        self._categories = None
        self._my_elements = None
        self._elements = None
        self._name = name

        self.elements = elements
        self.categories = ['negative', 'neutral', 'positive']

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

    @property
    def name(self) \
            -> str:
        return self._name

    @name.setter
    def name(self, name: str) \
            -> None:
        self._name = name

    @property
    def categories(self) \
            -> List[str]:
        return self._categories

    @categories.setter
    def categories(self, categories: List[str]) \
            -> None:
        self._categories = categories

    @property
    def elements(self) \
            -> Series:
        return self._elements

    @elements.setter
    def elements(self, elements: Series) \
            -> None:
        self._elements = elements
        self._set_my_elements()

    @property
    def my_elements(self) \
            -> ItemSeries:
        if not self._my_elements:
            self._set_my_elements()

        return self._my_elements

    @my_elements.setter
    def my_elements(self, elements: ItemSeries) \
            -> None:
        self._my_elements = elements

    def _set_my_elements(self):
        self.my_elements = ItemSeriesFactory.create(
            self.elements,
            self.name
        )

    @property
    def freqs(self) \
            -> List[Tuple[str, int]]:

        freqs = self.my_elements.frequencies_in_alpha_order

        required_n_elements = len(self.categories)

        if len(freqs) < required_n_elements:
            freqs = self.normalize_frequencies(freqs)
        elif len(freqs) > required_n_elements:
            raise CriticalException(
                self.logger,
                "More categories than required: %d vs. %d" % (
                    len(freqs), required_n_elements
                ))

        return freqs

    def show_freqs(self) \
            -> None:

        title = f"Frequencies of {self.name} labels"
        body = self.freqs

        print_in_box(title, body)

    def show_stats(self) \
            -> None:
        self.my_elements.stats.visualize()

    def normalize_frequencies(self, freqs: List[Tuple[str, int]]) \
            -> List[Tuple[str, int]]:

        categories = self.categories

        # Get the sentiments contained in the list of tuples.
        categories_in_tuple = [my_tuple[0] for my_tuple in freqs]

        # Check which sentiment is missing in the list of tuples
        for i in range(0, 3):
            if categories[i] not in categories_in_tuple:
                # Insert a tuple for the missing sentiment with
                # frequency = 0 at the correct alphabetical position
                freqs.insert(i, (categories[i], 0))

        return freqs
