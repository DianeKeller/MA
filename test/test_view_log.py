"""
test_view_log.py
----------------

Tests view_log.

Notes
-----
The tests use a built-in fixture "capfd" to capture stdout and
stderr output.

"""

import os

import pytest

from view_log import print_log, print_reverse_log


@pytest.fixture
def mock_log_file(temp_dir):
    """
    Creates a mock log file in the temporary directory.
    """
    log_file_path = os.path.join(temp_dir, "test.log")
    with open(log_file_path, 'w') as f:
        # Create a file with 20 lines:
        f.writelines([f"Line {i}\n" for i in range(1, 21)])
    return log_file_path


def test_print_log(capfd, mock_log_file):
    print_log(mock_log_file, max_lines=5)

    # Capture everything that was printed to the console during the test
    # execution
    out, err = capfd.readouterr()

    expected_output = ''.join([f"Line {i}\n" for i in range(16, 21)])
    assert out == expected_output
    print("Captured Output:", out)


def test_print_reverse_log(capfd, mock_log_file):
    print_reverse_log(mock_log_file, max_lines=5)

    # Capture everything that was printed to the console during the test
    # execution
    out, err = capfd.readouterr()

    expected_output = ''.join([f"Line {i}\n" for i in reversed(range(16, 21))])
    assert out == expected_output
    print("Captured Output:", out)


def test_print_log_default_lines(capfd, mock_log_file):
    print_log(mock_log_file)

    # Capture everything that was printed to the console during the test
    # execution
    out, err = capfd.readouterr()

    expected_output = ''.join([f"Line {i}\n" for i in range(11, 21)])
    assert out == expected_output
    print("Captured Output:", out)


def test_print_reverse_log_default_lines(capfd, mock_log_file):
    print_reverse_log(mock_log_file)

    # Capture everything that was printed to the console during the test
    # execution
    out, err = capfd.readouterr()

    expected_output = ''.join([f"Line {i}\n" for i in reversed(range(11, 21))])
    assert out == expected_output
    print("Captured Output:", out)
