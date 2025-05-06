"""
data_source_factory.py
-----------------------
Version 1.0, validated on 2025-05-01

This module provides a factory function to create and instantiate a new data
source strategy based on a provided name prefix, strategy name and file name.

Functions
---------
get_data_source_strategy(data_source_prefix, strategy_name, name=None) -> T:
    Dynamically creates and returns an instance of the data source strategy.

"""

from typing import TypeVar

from src.data_sources.data_source_strategy import DataSourceStrategy
from src.utils.class_utils import instantiate_class_from_module_name
from src.utils.string_utils import StringUtils

T = TypeVar('T', bound=DataSourceStrategy)


def get_data_source_strategy(
        data_source_prefix: str,
        strategy_name: str,
        name: str | None = None
) -> T:
    """
    Dynamically creates and returns an instance of a data source strategy.

    This function dynamically creates and returns an instance of the
    specified data source strategy. It constructs a full class name by
    combining the 'data_source_prefix' and 'strategy_name' with the suffix
    'Strategy'. It then loads the corresponding class and returns an
    instance of it.

    Parameters
    ----------
    data_source_prefix : str
        A string designing the data source. This string is prefixed to the
        strategy name. In the case of the MAD-TSC data source, it is used to
        represent the first part of the data source name only, i.e. 'mad'.

    strategy_name: str
        A string designing the strategy. This is supposed to be the
        identifying middle name part of the data source strategy to use,
        which is needed to distinguish between different strategies that can
        be applied to the same data source.

        For the MAD-TSC data source, since there is no need to distinguish
        between multiple possible strategies, the second part of the data
        source name ('tsc') is used to set the 'strategy name' so that the
        present method can dynamically compose a full strategy name.

    name: str | None
        The name of the strategy, used for printing and logging purposes. The
        default is None, allowing the concrete strategy to set its own default
        name.

    Returns
    -------
    An instance of the specified strategy class.

    Notes
    -----
    The strategy name must match the corresponding class name exactly,
    including case sensitivity, as this function dynamically constructs the
    full name and loads the class.

    Examples
    --------

    .. code-block:: python

        >>> from src.data_sources.mad_tsc_strategy import MadTscStrategy

        >>> file_name = "test_file"
        >>> strategy: MadTscStrategy = get_data_source_strategy(
        ...         'mad', 'tsc', file_name
        ... )

    """

    full_strategy_name = (
        f"{data_source_prefix.capitalize()}"
        f"{StringUtils.first_char_to_upper(strategy_name)}"
        "Strategy"
    )

    converted_name = StringUtils.convert_class_name_into_module_name(
        full_strategy_name
    )

    module_name = (
        f"src.data_sources."
        f"{converted_name}"
    )

    return instantiate_class_from_module_name(
        module_name, full_strategy_name, name
    )
