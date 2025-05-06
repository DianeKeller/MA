"""
type_aliases.py
----------------------
Version 1.0, updated on 2024-12-19

"""

from typing import Dict, List, OrderedDict, Iterable, Any

from datasets import DatasetDict
from pandas import DataFrame

DictKeyType = str | int | None

"""
A dictionary of lists where the keys are column names and the values
lists of column data.
"""
DictOfLists = Dict[str, List[int | float | str]]

ExamplesType = Iterable[Any]
HistoryDataType = List[str] | List[Dict[str, str]]
OrderedDictOfLists = OrderedDict[str, DictOfLists]

"""
A dictionary where the keys are prompt ingredients categories
and the values are lists of possible values the categories can
have.
"""
PromptIngredientsType = Dict[str, List[str]]

"""
A dictionary with the prompts, where the keys are
consecutive prompt numbers starting from 1 and the values are
dictionaries where the keys are position labels and the values
are the texts to insert at the indicated positions.
"""
PromptsDictType = Dict[str, Dict[str, str]]

Serializable = DatasetDict | DataFrame | str | Dict
StatsType = Dict[str, float | int | List[int] | List[float] | List[str]]
ThresholdsType = Dict[str, Dict[str, float]]
