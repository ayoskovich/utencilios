# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

project = "utencilios"
copyright = "2023, Anthony Castro-Yoskovich"
author = "Anthony Castro-Yoskovich"

sys.path.insert(0, os.path.abspath("../src/"))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
]
templates_path = ["_templates"]
exclude_patterns = []

# autodoc_mock_imports = ["pandas"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

html_use_index = True
