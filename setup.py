"""
setup.py
--------
Version 1.0, updated on 2025-05-07

This module contains code that needs to be executed only once to install the
libraries needed for the execution of the SentimentAnalysis programm.

Notes
-----
Run once after cloning the project:
Switch to the SentimentAnalysis folder, open a command line interpreter and
run this:

>>> python -m setup

"""

import os
import subprocess
import sys


PROJECT_DIR = os.path.dirname(__file__)
VENV_DIR = os.path.join(PROJECT_DIR, ".venv")
REQUIREMENTS_PATH = os.path.join(PROJECT_DIR, "requirements.txt")

def in_venv():
    return hasattr(sys, 'real_prefix') or (sys.prefix != sys.base_prefix)


def create_venv():
    print("⚠️  Keine virtuelle Umgebung gefunden.")
    print("🔧 Erstelle virtuelle Umgebung unter '.venv' ...")
    subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    print("✅ Virtuelle Umgebung erstellt.")
    print("♻️ Starte setup.py innerhalb der neuen Umgebung neu...\n")

    # Plattform-spezifischer Aufruf
    if os.name == 'nt':
        activate = os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        activate = os.path.join(VENV_DIR, "bin", "python")

    subprocess.check_call([activate, "-m", "setup"])
    sys.exit(0)


def install_requirements():

    print("📦 Installing dependencies from requirements.txt...")

    if not os.path.exists(REQUIREMENTS_PATH):
        print("📦 requirements.txt nicht gefunden.")
        return

    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS_PATH]
    )


def download_nltk():
    print("📥 Downloading NLTK tokenizer models...")
    import nltk
    nltk.download('punkt')
    # nltk.download('punkt_tab') # obsolete


def main():
    if not in_venv():
        create_venv()

    install_requirements()
    download_nltk()
    print(
        "\n✅ Setup finished. The SentimentAnalysis program is ready to run."
    )


if __name__ == "__main__":
    main()
