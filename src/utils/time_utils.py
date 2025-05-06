"""
time_utils.py
---------
Version 1.0, updated on 2024-09-12

This module provides utility functions for managing and recording
time and durations. It includes methods to start and stop time
tracking, compute elapsed time in hours, minutes and seconds, and log
or print this information. It also provides functionality to give audible
notifications in case of significant time delays.

Functions
---------
current_date_time() -> str:
    Returns the current date and time in a YYYY-MM-DD_HHhMM string format.

trace() -> None:
    Prints information about the function that called the current function.

beep() -> None:
    Plays a beep sound to notify users.

time_in_hours_minutes_and_seconds(my_time: float) -> str:
    Converts the seconds of a time duration into hours, minutes and seconds.

hours(n_hours: int) -> str:
    Returns the singular or plural form of "hour" depending on the input value.

begin(descr: str = '') -> Tuple[float, str]:
    Starts time recording and displays the start time.

seconds(n_seconds: float, n_decimal_places: int = 0) -> str:
    Returns the singular or plural form of "second" depending on n_seconds.

minutes(n_minutes: int) -> str:
    Returns the singular or plural form of "minute" depending on n_minutes.

end(start: Tuple[float, str], custom_log=False) -> Tuple[float, str]:
    Stops time recording, displays the elapsed time and optionally logs it.

See Also
--------
'Duration' decorator in the time_decorators module.

"""

import inspect
import time
from math import floor
from typing import Tuple

import winsound

from src.utils.print_utils import SEPARATOR, print_double_line

SIGNIFICANT_WAITING_TIME = 60  # seconds
FREQUENCY = 200  # Hertz
BEEP_DURATION = 300  # milliseconds


def hours(n_hours: int) \
        -> str:
    """
    Returns the singular or plural form of "hour" depending on the input value.

    Parameters
    ----------
    n_hours : int
       The number of hours.

    Returns
    -------
    str
       "hour" if n_hours is 1, "hours" otherwise.

    """

    if n_hours == 1:
        return 'hour'

    return 'hours'


def beep() -> None:
    """
    Plays a beep sound to notify users.

    The sound is played for a short duration with the frequency and
    duration set by constants at the top of this module. It can be used to
    signal significant waiting times or task completion.

    """

    winsound.Beep(FREQUENCY, BEEP_DURATION)


def begin(descr: str = '') \
        -> Tuple[float, str]:
    """
    Starts time recording and displays the start time.

    Parameters
    ----------
    descr : str, optional
        A description of the task to display alongside the start time.
        Default is an empty string.

    Returns
    -------
    Tuple[float, str]
        A tuple containing the start time and the description.

    """

    start = (time.time(), descr)

    # Print current date and time
    if descr:
        print(f'Started ({descr}): {time.strftime("%d.%m.%Y %H:%M:%S")}...')
    else:
        print(f'Started: {time.strftime("%d.%m.%Y %H:%M:%S")}...')

    return start


def end(start: Tuple[float, str], custom_log=False) \
        -> Tuple[float, str]:
    """
    Stops time recording, displays the elapsed time and optionally logs it.

    Parameters
    ----------
    start : Tuple[float, str]
        Tuple with the start time and a description.

    custom_log : bool
        If True, this method will not output any logging message. Instead, it
        is left to the caller to output a custom logging message using the
        return value. If False, this method will log a standard logging
        message. Default is False.

    Returns
    -------
    Tuple[float, str]
        A tuple with the elapsed seconds and a formatted string, with the
        elapsed time in hours, minutes, and seconds, that can be used for
        logging.

    """

    my_start, descr = start
    my_end = time.time()
    elapsed_seconds = my_end - my_start
    elapsed_time_str = time_in_hours_minutes_and_seconds(elapsed_seconds)

    if not custom_log:
        print_double_line()
        print(SEPARATOR)
        if descr:
            print(f'Duration ({descr}): {elapsed_time_str}')
        else:
            print(f'Duration: {elapsed_time_str}')

        print_double_line()

        # Only beep if there was significant waiting time.
        if elapsed_seconds > SIGNIFICANT_WAITING_TIME:
            beep()

    return elapsed_seconds, elapsed_time_str


def time_in_hours_minutes_and_seconds(my_time: float) \
        -> str:
    """
    Converts the seconds of a time duration into hours, minutes and seconds.

    Converts a time duration in seconds into a string detailing hours, minutes
    and seconds.

    Parameters
    ----------
    my_time : float
        The time in seconds to convert.

    Returns
    -------
    str
        The time formatted in hours, minutes, and seconds.

    """

    elapsed_time = ''
    elapsed_seconds = my_time
    if my_time > 60:
        elapsed_minutes = floor(my_time / 60)
        elapsed_seconds = my_time % 60
        if elapsed_minutes > 60:
            elapsed_hours = floor(elapsed_minutes / 60)
            elapsed_minutes %= 60
            elapsed_time = f'{elapsed_hours} {hours(elapsed_hours)}, '
        elapsed_time += f'{elapsed_minutes} {minutes(elapsed_minutes)}, '
    if my_time < 1:
        elapsed_time += (f'%2.4f '
                         f'{seconds(elapsed_seconds, 4)}'
                         ) % elapsed_seconds
    else:
        elapsed_time += (f'%2.0f '
                         f'{seconds(elapsed_seconds, 0)}'
                         ) % elapsed_seconds

    return elapsed_time


def minutes(n_minutes: int) \
        -> str:
    """
    Returns the singular or plural form of "minute" depending on n_minutes.

    Returns the singular or plural form of "minute" depending on the
    given number of minutes.

    Parameters
    ----------
    n_minutes : int
        The number of minutes.

    Returns
    -------
    str
        "minute" if n_minutes is 1, "minutes" otherwise.

    """

    if n_minutes == 1:
        return 'minute'

    return 'minutes'


def seconds(n_seconds: float, n_decimal_places: int = 0) \
        -> str:
    """
    Returns the singular or plural form of "second" depending on n_seconds.

    Returns the singular or plural form of "second" depending on the number
    of seconds.

    Parameters
    ----------
    n_seconds : float
        The number of seconds.

    n_decimal_places : int, optional
        The number of decimal places to round the seconds to, by default 0.

    Returns
    -------
    str
        "second" if n_seconds rounds to 1, "seconds" otherwise.

    """

    if round(n_seconds, n_decimal_places) == 1:
        return 'second'

    return 'seconds'


def current_date_time() \
        -> str:
    """
    Returns the current date and time in a YYYY-MM-DD_HHhMM string format.

    Returns
    -------
    str
        The formatted current date and time.

    """

    return str(time.strftime("%Y-%m-%d_%Hh%M"))


def trace() \
        -> None:
    """
    Prints information about the function that called the current function.

    Prints the following information:

    - File name of the calling function
    - Line number of the calling function
    - Method name of the calling function
    - Code calling the current function

    """

    _, filename, linenumber, method, call, _ = inspect.stack()[2]

    print(f"\t Called from: {filename}:{linenumber}, \n"
          f"\t calling method:{method}, \n"
          f"\t call: {call[0].strip()}")
