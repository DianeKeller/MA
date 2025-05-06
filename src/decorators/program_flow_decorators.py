"""
program_flow_decorators.py
--------------------------
Version 1.0, updated on 2024-12-19

"""
from time import sleep

from settings import DEBUG_MODE
from src.utils.user_interaction_utils import ask_continue


def analysis_breakpoint(msg: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if DEBUG_MODE:
                if ask_continue(
                        "%s.%s - Breakpoint reached."
                        % (func.__module__, func.__name__)
                ):
                    return func(*args, **kwargs)
        return wrapper
    return decorator
