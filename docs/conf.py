"""Configure docs.

See: https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys
from datetime import date

import eeg_positions

curdir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(curdir, "..", "eeg_positions")))

# see: https://sphinx.readthedocs.io/en/1.3/extensions.html
extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_gallery.gen_gallery",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "sphinx_copybutton",
    "sphinxcontrib.bibtex",
    "sphinx_github_role",
]

# configure sphinx-github-role
github_default_org_project = ("sappelhoff", "eeg_positions")

# configure sphinxcontrib.bibtex
bibtex_bibfiles = ["references.bib"]

# configure sphinx-copybutton
copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True

# configure numpydoc
numpydoc_xref_param_type = True
numpydoc_xref_ignore = {
    # words
    "of",
    "shape",
}

# configure sphinx-gallery
sphinx_gallery_conf = {
    "doc_module": ("eeg_positions"),
    "reference_url": {
        "eeg_positions": None,
    },
    "examples_dirs": "../examples",
    "gallery_dirs": "auto_examples",
    "filename_pattern": "^((?!sgskip).)*$",
    "backreferences_dir": "generated",
    "download_all_examples": False,
    "show_signature": False,
    "min_reported_time": 100,
}


# Generate the autosummary
autosummary_generate = True

# General information about the project.
project = "eeg_positions"
copyright = (
    f"2018-{date.today().year}, Stefan Appelhoff et al. (see "
    "<a href='https://github.com/sappelhoff/eeg_positions/blob/main/CITATION.cff'"
    ">CITATION.cff</a>)"
)

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
    "github_type": "star",
    "github_repo": "eeg_positions",
    "github_user": "sappelhoff",
    "show_powered_by": False,
    "sidebar_width": "250px",  # default: 220px
    "page_width": "1040px",  # default: 940px
}

html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
    ],
}

templates_path = ["_templates"]

# When functions from other packages are mentioned, link to them
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "mne": ("https://mne.tools/dev", None),
    "numpy": ("https://numpy.org/devdocs", None),
    "matplotlib": ("https://matplotlib.org", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/dev", None),
}
intersphinx_timeout = 15
