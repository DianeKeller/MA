"""
setup.py
--------
Version 1.0, updated on 2025-05-01

This module contains code that needs to be executed only once to install the
libraries needed for the execution of the SentimentAnalysis programm.

Notes
-----
Having cloned the SentimentAnalysis program, you should run this module to
install the required libraries for running the programm: Switch to the
SentimentAnalysis folder, open a command line interpreter and call the setup
module like this:

>>> python -m setup

"""
import os
import subprocess
import sys

import nltk

# Install dependencies from requirements.txt
requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
subprocess.check_call(
    [sys.executable, '-m', 'pip', 'install', '-r', requirements_path]
)

# Download NLTK punkt tokenizer
nltk.download('punkt')
nltk.download('punkt_tab')
