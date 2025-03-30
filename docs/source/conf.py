# Configuration file for the Sphinx documentation builder.

import os
import sys

from lumache import __version__

# Source code dir relative to this file;
# used by api.rst's autosummary
sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))


# -- Project information

project = 'Lumache'
copyright = '2021, Graziella'
author = 'Graziella'

release = __version__
version = __version__

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
