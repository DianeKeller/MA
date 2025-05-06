"""
view_log.py
-----------
Version 1.0, updated on 2024-12-06

This is a python script executable from the command line. It prints the
contents of a log file, with an option to display the content in reverse
order. If a maximum number of lines is not specified, the script will
output the newest 10 log messages.

Usage
-----
To view the newest 10 log messages in normal order (newest last):
>>> python view_log.py path\\yourlogfile.log

To view the newest N log messages in normal order (newest last):
>>> python view_log.py path\\yourlogfile.log N

To view the messages in reverse order (newest first), add '-r', e.g.:
>>> python view_log.py path\\yourlogfile.log -r
>>> python view_log.py path\\yourlogfile.log N -r

"""

import sys


def print_log(log_file, max_lines: int = 10):
    """
    Print the last 'max_lines' lines from the log file 'log_file'.

    Parameters
    ----------
    log_file : str
        The path to the log file.

    max_lines : int
        The maximum number of lines to print. Defaults to 10.

    """

    with open(log_file, 'r') as f:
        for line in f.readlines()[-max_lines:]:
            print(line.rstrip())


def print_reverse_log(log_file, max_lines=10):
    """
    Print the last 'max_lines' lines of the log file in reverse order.

    Parameters
    ----------
    log_file : str
        The path to the log file.

    max_lines : int
        The maximum number of lines to print. Defaults to 10.

    """

    with open(log_file, 'r') as f:
        for line in reversed(f.readlines()[-max_lines:]):
            print(line.rstrip())


def main(args):
    # Show the docstring as a help message if the script is not called
    # correctly.
    if len(args) < 2 or len(args) > 4:
        print(__doc__)
        sys.exit(1)

    max_lines = 0
    log_file = args[1]
    reverse = False

    # Check the arguments:
    for arg in args[2:]:
        if arg.isdigit():
            max_lines = int(arg)
        elif arg == '-r':
            reverse = True
        else:
            print(f"Invalid argument: {arg}")
            print(__doc__)
            sys.exit(1)

    if reverse:
        print_reverse_log(log_file, max_lines)
    else:
        print_log(log_file, max_lines)


if __name__ == '__main__':
    main(sys.argv)
