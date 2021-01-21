"""Configure docs.

See: https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
# Copyright (c) 2018-2021, Stefan Appelhoff
# BSD-3-Clause

import os
import sys
from datetime import date

import eeg_positions

curdir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(curdir, "..", "eeg_positions")))

# see: https://sphinx.readthedocs.io/en/1.3/extensions.html
extensions = [
    "sphinx_gallery.gen_gallery",
    "sphinx.ext.githubpages",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "sphinx_copybutton",
]

copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True

numpydoc_xref_param_type = True

# Generate the autosummary
autosummary_generate = True

# General information about the project.
project = "eeg_positions"
copyright = "2018-{}, Stefan Appelhoff".format(date.today().year)
author = "Stefan Appelhoff"
version = eeg_positions.__version__
release = version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Define master doc
master_doc = "index"

# Options for HTML output
html_theme = "alabaster"
html_theme_options = {
    "description": "Compute and plot standard EEG electrode positions.",
    "fixed_sidebar": True,
    "github_button": True,
    "github_repo": "eeg_positions",
    "github_user": "sappelhoff",
}
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
    ],
    "navbar_links": [
        ("Examples", "auto_examples/index"),
        ("API", "api"),
        ("What's new", "whats_new"),
        ("GitHub", "https://github.com/sappelhoff/pyprep", True),
    ],
}

# When functions from other packages are mentioned, link to them
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "mne": ("https://mne.tools/dev", None),
    "numpy": ("https://numpy.org/devdocs", None),
    "matplotlib": ("https://matplotlib.org", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/dev", None),
}
intersphinx_timeout = 15
