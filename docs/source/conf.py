"""
conf.py
-------
Version 1.0, updated on 2025-05-01

"""

from sphinx.application import Sphinx
from sphinx.ext.autodoc import Options
from typing import List, Any

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

# sys.path.insert(0, os.path.abspath('.'))
source_dir = os.path.dirname(__file__)
docs_dir = os.path.join(source_dir, "..")
project_root = os.path.abspath(os.path.join(docs_dir, ".."))
src_dir = os.path.join(project_root, "src")
sys.path.insert(0, src_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, ".."))

print(f"PATH: {sys.path}")

# -- Project information -----------------------------------------------------

project = 'SentimentAnalysis'
copyright = '2024, Diane Keller'
author = 'Diane Keller'

# The full version, including alpha/beta/rc tags
release = '0.1'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.inheritance_diagram'
]

# Napoleon settings See documentation at
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
napoleon_include_init_with_doc = True
napoleon_include_special_with_doc = True
napoleon_include_private_with_doc = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# https://www.sphinx-doc.org/en/master/usage/theming.html#themes

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
# html_theme = 'basic'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


def add_inheritance_diagram(
        app: Sphinx,
        what: str,
        name: str,
        obj: Any,
        options: Options,
        lines: List[str])\
-> None:
    """
    Adds an inheritance diagram directive to each module in the rst files.

    Parameters
    ----------
    app: Sphinx
        The Sphinx application object.

    what: str
        The type of the object being documented (e.g., 'class', 'function').

    name: str
        The name of the object.

    options: Options
        The options given to the autodoc directive.

    lines: List[str]
        The lines of the rst file.

    """

    if what == "class":
        diagram_directive = ".. inheritance-diagram:: {}".format(name)
        diagram_options = "   :parts: 1"

        # Insert the directive at the beginning of the docstring lines
        # making sure there is a blank line before and after the directive

        lines.append("")
        lines.append(".. inheritance-diagram:: {}".format(name))
        lines.append("   :parts: 1")


def setup(app: Sphinx):
    """
    This function will be called when Sphinx starts the build process.

    Parameters
    ----------
    app: Sphinx
        The Sphinx application object

    """
    app.connect("autodoc-process-docstring", add_inheritance_diagram)
