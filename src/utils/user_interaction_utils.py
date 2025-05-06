"""
user_interaction_utils.py
-------------------------
Version 1.0, updated on 2024-12-19

This module provides utility functions for user interaction.

Functions
---------
ask_continue_without_saving(timeout: int = 60) -> bool:
    Prompts the user to decide whether to continue without saving results.

ask_save_and_continue(timeout: int = 60) -> bool:
    Prompts the user to decide whether to save the results and continue.

get_user_input(prompt: str, timeout: int = 60) -> bool:
    Handles user input with a timeout and validates the response.

"""

import threading

import keyboard

from src.sentiment_analysis.retrieval.custom_exceptions import \
    CancelledByUserException

# Set a default timeout value.
# Should be at least 5 seconds to allow for the user to react.
TIMEOUT: int = 60  # seconds


def ask_continue(msg: str = '') \
        -> bool:
    """
    Waits for the user to press any key.

    Returns
    -------
    bool
        True if the user hits a key.

    """

    print("%s Press any key to continue..." % msg)
    keyboard.read_event()

    return True


def ask_continue_or_cancel(timeout: int = TIMEOUT) \
        -> bool:
    """
    Prompts the user to decide whether to continue or cancel.

    Prompts the user to decide whether to continue or cancel the current
    operation.

    The user is prompted with a "y/n" question. If the user does not respond
    within the specified timeout, the function defaults to "no" ('n').

    Parameters
    -----------
    timeout : int
        Time in seconds to wait for user input before defaulting. Defaults to
        the global TIMEOUT constant.

    Returns
    -------
    bool
        True if the user chooses 'y' (yes), False if 'n' (no).

    """

    prompt = "Do you want to continue? (y/n): "

    user_choice = get_user_input(prompt, timeout, default='n')

    if not user_choice:
        raise CancelledByUserException()

    return user_choice


def ask_save_and_continue(timeout: int = TIMEOUT) \
        -> bool:
    """
    Prompts the user to decide whether to save the results and continue.

    The user is prompted with a "y/n" question. If the user does not respond
    within the specified timeout, the function defaults to "yes" ('y').

    Parameters
    -----------
    timeout : int
        Time in seconds to wait for user input before defaulting. Defaults to
        the global TIMEOUT constant.

    Returns
    -------
    bool
        True if the user chooses 'y' (yes), False if 'n' (no).

    """

    prompt = "Do you want to save the results and continue? (y/n): "

    return get_user_input(prompt, timeout, default='y')


def ask_continue_without_saving(timeout: int = TIMEOUT) \
        -> bool:
    """
    Prompts the user to decide whether to continue without saving results.

    The user is asked whether they want to discard the results and continue
    without saving. If the user does not respond within the specified timeout,
    the function defaults to "yes" ('y').

    Parameters
    ----------
    timeout : int
        Time in seconds to wait for user input before defaulting. Defaults
        to the global TIMEOUT constant.

    Returns
    -------
    bool: True if the user chooses 'y' (yes), False if 'n' (no).

    """

    prompt = ("Do you want to discard the results and continue without "
              "saving? (y/n): ")

    return get_user_input(prompt, timeout, default='y')


def get_user_input(prompt: str, timeout: int = TIMEOUT, default: str = 'y') \
        -> bool:
    """
    Handles user input with a timeout and validates the response.

    This function presents a prompt to the user and waits for input in a
    separate thread. If the user does not respond within the specified timeout,
    it defaults to 'y' (yes). If the user provides invalid input, they are
    prompted again until they enter 'y' or 'n'.

    Parameters
    ----------
    prompt : str
        The message to display to the user.

    timeout : int
        Time in seconds to wait for user input before defaulting. Defaults
        to the global TIMEOUT constant.

    default : str
        Default response if no input is received within the timeout.

    Returns
    -------
    bool: True if the user chooses 'y' (yes), False if 'n' (no).

    """

    input_event = threading.Event()
    # Use a list to store user input to modify it within the thread
    user_input = [default]

    def get_input() \
            -> None:
        """
        Handles user input in a separate thread.

        """

        nonlocal user_input
        user_input[0] = input(prompt).strip().lower()
        input_event.set()  # Signal that input was received

    input_thread = threading.Thread(target=get_input)
    input_thread.start()
    input_thread.join(timeout)

    if not input_event.is_set():
        print(
            f"\nNo input received within {timeout} seconds. Defaulting to "
            f"{default}."
        )
        return default == 'y'

    # Validate user input
    while user_input[0] not in ('y', 'n'):
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")
        user_input[0] = input(prompt).strip().lower()

    return user_input[0] == 'y'
