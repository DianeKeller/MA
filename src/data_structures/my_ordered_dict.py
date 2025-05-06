"""
my_ordered_dict.py
------------------
Version 1.0, updated on 2025-05-01

"""

from collections import OrderedDict
from typing import Any, Tuple

from src.utils.dict_utils import dict_to_string


class MyOrderedDict:
    """
    MyOrderedDict class.

    This class is a wrapper around a OrderedDict object. It adds properties
    and methods to the object to simplify access to its key-value pairs and
    manage its contents.

    Attributes
    ----------
    my_dict : OrderedDict
        The 'OrderedDict' object that is wrapped in this class.

    first : tuple
        The first key-value pair in the 'OrderedDict'. Computed property
        without setter.

    second : tuple
        The second key-value pair in the 'OrderedDict'. Computed property
        without setter.

    last : tuple
        The last key-value pair in the 'OrderedDict'. Computed property
        without setter.

    first_value : Any
        The value of the first key-value pair in the 'OrderedDict'. Computed
        property without setter.

    second_value : Any
        The value of the second key-value pair in the 'OrderedDict'. Computed
        property without setter.

    last_value : Any
        The value of the last key-value pair in the 'OrderedDict'. Computed
        property without setter.

    first_key : Any
        The key of the first key-value pair in the 'OrderedDict'. Computed
        property without setter.

    second_key : Any
        The key of the second key-value pair in the 'OrderedDict'. Computed
        property without setter.

    last_key : Any
        The key of the last key-value pair in the 'OrderedDict'. Computed
        property without setter.

    Methods
    -------
    contains(key) -> bool:
        Checks whether the specified key is present in the 'OrderedDict'.

    remove(key) -> None:
        Removes the element with the specified key from the 'OrderedDict' if
        it exists.


    """

    def __init__(self, my_dict: OrderedDict) \
            -> None:
        """
        Constructor.

        Initializes an instance of th MyOrderedDict class with the provided
        OrderedDict.

        Parameters
        ----------
        my_dict : OrderedDict
            The OrderedDict to wrap in this class.

        """
        self.__my_dict = my_dict

    def __bool__(self) \
            -> bool:
        """
        Evaluates to False if the internal OrderedDict is empty.

        True otherwise.

        """

        return bool(self.__my_dict)

    def __str__(self) \
            -> str:
        return dict_to_string(self.my_dict)

    def __len__(self) \
            -> int:
        return len(self.my_dict)

    # region --- Properties

    @property
    def my_dict(self) \
            -> OrderedDict:
        """
        Returns the 'OrderedDict' object that is wrapped in this class.
        """

        return self.__my_dict

    @my_dict.setter
    def my_dict(self, dic: OrderedDict) \
            -> None:
        """
        Sets the 'OrderedDict' object to wrap in this class.
        """

        self.__my_dict = dic

    @property
    def first(self) \
            -> Tuple:
        """
        Returns the first key-value pair in the 'OrderedDict'.
        """

        return next(iter(self.my_dict.items()))

    @property
    def second(self) \
            -> Tuple:
        """
        Returns the second key-value pair in the 'OrderedDict`.
        """

        it = iter(self.my_dict.items())
        next(it)
        return next(it)

    @property
    def last(self) \
            -> Tuple:
        """
        Returns the last key-value pair in the 'OrderedDict'.
        """

        return next(reversed(self.my_dict.items()))

    @property
    def first_value(self) \
            -> Any:
        """
        Returns the value of the first key-value pair in the 'OrderedDict'.
        """

        return self.first[1]

    @property
    def second_value(self) \
            -> Any:
        """
        Returns the value of the second key-value pair in the 'OrderedDict'.
        """

        return self.second[1]

    @property
    def last_value(self) \
            -> Any:
        """
        Returns the value of the last key-value pair in the 'OrderedDict'.
        """

        return self.last[1]

    @property
    def first_key(self) \
            -> Any:
        """
        Returns the key of the first key-value pair in the 'OrderedDict'.
        """
        return self.first[0]

    @property
    def second_key(self) \
            -> Any:
        """
        Returns the key of the second key-value pair in the 'OrderedDict'.
        """
        return self.second[0]

    @property
    def last_key(self) \
            -> Any:
        """
        Returns the key of the last key-value pair in the 'OrderedDict'.
        """

        return self.last[0]

    # endregion --- Properties

    # region --- Methods

    def remove(self, key: Any) \
            -> None:
        """
        Removes the element with the specified key from the 'OrderedDict'.

        Removes the element with the specified key from the 'OrderedDict'
        if it exists.

        Parameters
        ----------
        key : Any
            A key to search in the OrderedDict to remove the
            corresponding key-value pair.

        """

        if self.contains(key):
            self.my_dict.pop(key)

    def contains(self, key: Any) \
            -> bool:
        """
        Checks whether the specified key is present in the 'OrderedDict'.

        Parameters
        ----------
        key : Any
            A key to look for in the OrderedDict.

        Returns
        -------
        bool
            True if the key exists, False otherwise.

        """

        return key in self.my_dict

    # endregion --- Methods
