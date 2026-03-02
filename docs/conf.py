# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

# Add the project root to the path so we can import warlock_manager
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Project information
project = 'Warlock-Manager'
copyright = '2026, Warlock-Manager Contributors'
author = 'Warlock-Manager Contributors'
version = '1.9.9'
release = '1.9.9~20260301'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Options for HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = None
html_theme_options = {
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
}

# Autodoc configuration
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': False,
    'show-inheritance': True,
}

# Typehints configuration
autodoc_typehints = 'description'
autodoc_typehints_format = 'short'

# MyST configuration
myst_enable_extensions = [
    'colon_fence',
    'deflist',
]

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
