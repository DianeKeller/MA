"""
method_check_decorator.py
"""

from functools import wraps
from typing import Callable, Tuple, Any, Dict


def require_method(*attrs):
    def decorator(operation: Callable):
        @wraps(operation)
        def wrapper(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
            for attr in attrs:
                if not hasattr(self, attr):
                    msg = ("%s method is missing. Cannot proceed." %
                           attr.capitalize())
                    self.log(msg, "error")
                    raise NotImplementedError(msg)
            return operation(self, *args, **kwargs)

        return wrapper

    return decorator
