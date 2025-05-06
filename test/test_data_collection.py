"""
test_data_collection.py
"""

from typing import Any

from src.data_structures.data_collection import DataCollection, T
from src.utils.data_utils import is_none_or_empty


# Create a dummy subclass of DataCollection for testing
class DummyDataCollection(DataCollection):
    def __init__(self, data=None, name=None):
        super().__init__(data, name)
        self._n_rows = 0
        self._n_cols = 0
        self._col_names = []

    def has_no_data(self, verbose: bool = True) \
            -> bool:
        no_data = is_none_or_empty(self.data)

        if no_data and verbose:
            msg = "No data! Cannot execute operation."
            self._log(msg, "warning")

        return no_data

    @property
    def n_rows(self):
        return self._n_rows

    @property
    def n_cols(self):
        return self._n_cols

    @property
    def col_names(self):
        return self._col_names

    def filter_rows_by_col_value(self, col_name: str, col_value: Any):
        pass

    def min_filter(self: T, col_name: str, min_value: Any):
        pass

    def max_filter(self: T, col_name: str, max_value: Any):
        pass

    def find_single_value_cols(self):
        self._single_value_cols = {"col1": "value1"}

    def drop_single_value_cols(self):
        pass


def test_initialization_and_properties():
    data = "dummy data"
    name = "Test Data"
    collection = DummyDataCollection(data=data, name=name)

    assert collection.data == data
    assert collection.name == name

    # Test property setters
    new_name = "New Test Data"
    collection.name = new_name
    assert collection.name == new_name
