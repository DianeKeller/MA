"""
item_collection_factories.py
----------------------------
Version 1.0, updated on 2024-09-07

This module provides two generic interfaces that dynamically select the
appropriate method for constructing item lists or item series based on the
type of input data provided. It consists of the ItemListFactory and the
ItemSeriesFactory class and several functions that form single-dispatch
mechanisms for the use of these factory classes.

"""

from functools import singledispatch
from typing import Any, List

from pandas import Series

from logger import Logger
from src.data_structures.item_list import ItemList
from src.data_structures.item_series import ItemSeries
from src.logging_mixin import LoggingMixin

logger = Logger(__name__).get_logger()
log = LoggingMixin().log


# region --- ItemListFactory


@singledispatch
def create_item_list(
        data: Any,
        name: str = ''
) -> ItemList:
    """
    Generic function to create an ItemList from various types of
    input data. This function is the entry point for the singledispatch
    mechanism, which, based on the type of 'data', dynamically
    selects which of the following implementations needs to be executed.

    Parameters:
    ----------
    data :  Any
        The data to populate the ItemList. The specific type of this argument
        determines which implementation of the function is called.

    name : str
        The name of the ItemList. Defaults to an empty string.

    Returns:
    -------
    ItemList
        An ItemList populated with the provided data.

    Raises:
    ------
    NotImplementedError
        If the data type of 'data' is not supported.

    """

    msg = (f"Creation from {type(data).__name__} is not supported. "
           f"Data must be one of the supported data types.")
    if msg:
        logger.error(msg)
        raise NotImplementedError(msg)

    return ItemList([], name)


@create_item_list.register(ItemList)
def _(
        data: ItemList,
        name: str = ''
) -> ItemList:
    """
    Implementation for handling the case that an ItemList is passed to the
    factory.

    Parameters
    ----------
    data : ItemList
        The ItemList to populate the ItemList.

    name : str
        The name of the ItemList. Not needed for this implementation,
        because the provided ItemList should already contain a name. Defaults
        to an empty string.

    """

    return data


@create_item_list.register(ItemSeries)
def _(
        data: ItemSeries,
        name: str = ''
) -> ItemList:
    """
    Implementation for handling the case that an ItemSeries is passed to the
    factory.

    This method converts an ItemSeries object into an ItemList object.

    Parameters
    ----------
    data : ItemSeries
        An ItemSeries object to populate the ItemList.

    name : str
        The name of the ItemList. Not needed for this implementation,
        as the provided ItemSeries object's name is used for the ItemList
        object. Defaults to an empty string.

    """

    return ItemList(data.elements.tolist(), data.name)


@create_item_list.register(Series)
def _(
        data: Series,
        name: str = ''
) -> ItemList:
    """
    Implementation for handling the case that a Series is passed to the
    factory.

    This method converts a pandas Series object into an ItemList object.

    Parameters
    ----------
    data : Series
        A pandas Series object to populate the ItemList.

    name : str
        The name of the ItemList. Defaults to an empty string.

    """

    return ItemList(data.tolist(), name)


@create_item_list.register(list)
def _(
        data: List,
        name: str = ''
) -> ItemList:
    """
    Implementation for handling the case that a list is passed to the
    factory.

    This method wraps the list into an ItemList object.

    Parameters
    ----------
    data : List
        A list to populate the ItemList.

    name : str
        The name of the ItemList. Defaults to an empty string.

    """

    return ItemList(data, name)


class ItemListFactory:
    """
    ItemListFactory class.

    This class provides a factory method to create ItemList instances.

    Methods
    -------
    create(data: Any | None, col_names: list[str] | None=None,
            index_column: str = '', name: str | None = None) -> ItemList:
        Factory method to create an ItemList instance.

    """

    @staticmethod
    def create(
            data: Any,
            name: str = ''
    ) -> ItemList:
        """
        Factory method to create an ItemList instance.

        Parameters
        ----------
        data : Any
            The data to populate the ItemList. The specific type of this
            argument determines which implementation of the create_dataframe
            function is called.

        name : str
            The name for the ItemList, used to identify the data. Defaults
            to an empty string.

        Returns
        -------
        ItemList
            An instance of ItemList populated with the provided data.

        """

        # Delegate to the singledispatch function
        return create_item_list(data, name)


# endregion --- ItemListFactory

# region --- ItemSeriesFactory


@singledispatch
def create_item_series(
        data: Any,
        name: str = ''
) -> ItemSeries:
    """
    Generic function to create an ItemSeries from various types of
    input data. This function is the entry point for the singledispatch
    mechanism, which, based on the type of 'data', dynamically
    selects which of the following implementations needs to be executed.

    Parameters:
    ----------
    data :  Any
        The data to populate the ItemSeries. The specific type of this argument
        determines which implementation of the function is called. Defaults
        to None.

    name : str
        The name of the ItemSeries. Defaults to an empty string.

    Returns:
    -------
    ItemSeries
        An ItemSeries instance populated with the provided data.

    Raises:
    ------
    NotImplementedError
        If the data type of 'data' is not supported.

    """

    msg = (f"Creation from {type(data).__name__} is not supported. "
           f"Data must be one of the supported data types.")
    if msg:
        logger.error(msg)
        raise NotImplementedError(msg)

    return ItemSeries(Series(), name)


@create_item_series.register(ItemSeries)
def _(
        data: ItemSeries,
        name: str = ''
) -> ItemSeries:
    """
    Implementation for handling the case that an ItemSeries is passed to the
    factory.

    Parameters
    ----------
    data : ItemSeries
        The ItemSeries to populate the ItemSeries.

    name : str
        The name of the ItemSeries. Not needed for this implementation,
        because the provided ItemSeries should already contain a name. Defaults
        to an empty string.

    """

    return data


@create_item_series.register(Series)
def _(
        data: Series,
        name: str | None = ''
) -> ItemSeries:
    """
    Implementation for handling the case that a Series is passed to the
    factory.

    This method wraps the series into an ItemSeries object.

    Parameters
    ----------
    data : Series
        A Series to populate the ItemSeries.

    name : str
        The name of the ItemSeries. Defaults to an empty string.

    """

    return ItemSeries(data, name)


class ItemSeriesFactory:
    """
    ItemSeriesFactory class.

    This class provides a factory method to create ItemSeries instances.

    Methods
    -------
    create(data: Any | None, name: str | None = None) -> ItemSeries:
        Factory method to create an ItemSeries instance.

    """

    @staticmethod
    def create(
            data: Any | None = None,
            name: str | None = None
    ) -> ItemSeries:
        """
        Factory method to create an ItemSeries instance.

        Parameters
        ----------
        data : Any | None
            The data to populate the ItemSeries. The specific type of this
            argument determines which implementation of the create_item_series
            function is called.

        name : str
            The name for the ItemSeries, used to identify the data. Default is
            None.

        Returns
        -------
        ItemSeries
            An instance of ItemSeries populated with the provided data.

        """

        # Delegate to the singledispatch function
        return create_item_series(data, name)

# endregion --- ItemSeriesFactory
