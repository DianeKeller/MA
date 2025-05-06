"""
loggable.py
"""

from typing import runtime_checkable, Protocol


@runtime_checkable
class Loggable(Protocol):
    """
    Protocol for classes that can be logged.

    This class is needed to give mixins the ability to assert
    that classes that implement the mixin adhere to this protocol and
    provide a '_log' method that the mixin can use.

    """

    def _log(self, message: str, level: str = 'info'):
        ...
