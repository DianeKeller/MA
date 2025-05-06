"""
statistics_factory.py
----------------------
Version 1.0, updated on 2024-12-04

"""

from __future__ import annotations

from typing import List, TYPE_CHECKING

from pandas import Series

from src.stats.analyzer import Analyzer
from src.stats.statistics_strategy import StatisticsStrategy
from src.utils.class_utils import instantiate_class_from_module_name
from src.utils.late_imports import LateImports
from src.utils.string_utils import StringUtils

if TYPE_CHECKING:
    from src.data_structures.item_series import ItemSeries
    from src.data_structures.item_list import ItemList


def _get_statistics_strategy(stat_category: str, items: ItemList) \
        -> StatisticsStrategy:
    """
    Dynamically creates and returns an instance of the statistics strategy
    that corresponds to the specified strategy name.

    Parameters
    ----------

    stat_category : str
        The statistical category forming the first part of the strategy's
        name, e.g. 'frequency', 'count', 'length'.

    items : ItemList
        The items to analyze with the strategy.

    Returns
    -------
    An instance of the specified strategy class.

    """

    strategy_name = (
            stat_category.lower().capitalize() + "Strategy"
    )

    module_name = (
        f"src.stats."
        f"{StringUtils.convert_class_name_into_module_name(strategy_name)}"
    )

    return instantiate_class_from_module_name(
        module_name, strategy_name, items
    )


def get_analyzer(
        stat_category: str,
        items: ItemList | ItemSeries | Series | List
) -> Analyzer:
    """
    Dynamically creates and returns an instance of the StatisticalAnalyzer
    class using the statistics strategy corresponding to the specified
    statistics category.

    Parameters
    ----------
    stat_category : str
        The statistical category forming the first part of the strategy's
        name, e.g. 'frequency', 'count', 'length'.

    items : ItemList | ItemSeries | Series | List
        The items to analyze with the strategy.

    Returns
    -------
    Analyzer
        An instance of the StatisticalAnalyzer class that uses the specified
        statistics strategy.

    """

    # Prevent circular imports
    item_list_factory_cls = LateImports.get_item_list_factory_class()

    items = item_list_factory_cls().create(items)

    strategy = _get_statistics_strategy(stat_category, items)
    return Analyzer(strategy)
