"""
action.py
----------
Version 1.0, updated on 2025-01-09

"""

from __future__ import annotations

from enum import Enum


class Action(Enum):
    """
    Actions class.
    
    """

    PROMPT_ENGINEERING = 1
    SENTIMENT_ANALYSIS = 2
    EVALUATION = 3
    PROMPT_GROUP_EVALUATION = 4
    PROMPT_OPTIMIZATION = 5