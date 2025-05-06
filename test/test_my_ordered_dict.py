"""
test_my_ordered_dict.py
"""

from collections import OrderedDict

from src.data_structures.my_ordered_dict import MyOrderedDict


def test_ordered_dict():
    """
    Create an empty ordered dictionary.
    Assert that the length of the dictionary is 0.

    """
    odict = OrderedDict()
    assert len(odict) == 0


def test_my_ordered_dict():
    """
    Test if the given dictionary is an instance of OrderedDict.
    Create a new instance of MyOrderedDict.
    Test if the new instance's dictionary is an instance of OrderedDict.
    Test if the length of the new instance's dictionary is 0.
    Test if the length of the new instance is 0.

    """

    odict = OrderedDict()
    assert isinstance(odict, OrderedDict)

    my_ordered_dict = MyOrderedDict(odict)
    assert isinstance(my_ordered_dict.my_dict, OrderedDict)
    assert len(my_ordered_dict.my_dict) == 0
    assert len(my_ordered_dict) == 0
