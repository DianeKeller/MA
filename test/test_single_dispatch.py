"""
test_single_dispatch.py
"""

from functools import singledispatch
from typing import Any


@singledispatch
def func_test_filter(value: Any):
    return "Generic function called"


@func_test_filter.register(int)
@func_test_filter.register(float)
def _(value):
    return "Specialized function for int/float called"


def test_single_dispatch():
    assert func_test_filter("hello") == "Generic function called"
    assert func_test_filter(10) == "Specialized function for int/float called"
    assert func_test_filter(2.7) == ("Specialized function for int/float "
                                     "called")
