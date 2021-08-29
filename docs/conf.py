# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('./../'))


# -- Project information -----------------------------------------------------

project = 'VoxelBotUtils'
copyright = '2020 Kae Bartlett'
author = 'Kae Bartlett'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.linkcode",
    # "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinx_rtd_theme",
]

autodoc_default_options = {
    "member-order": "bysource",
    "imported-members": True,
    'members': True,
    'special-members': '__init__',
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'discord': ('https://novus.readthedocs.io/en/latest', None),
    'aiohttp': ('https://docs.aiohttp.org/en/stable/', None),
    'asyncpg': ('https://magicstack.github.io/asyncpg/current/', None),
    'aioredis': ('https://aioredis.readthedocs.io/en/v1.3.0/', None),
    'upgradechat': ('https://upgradechatpy.readthedocs.io/en/latest/', None),
    # 'aiodogstatsd': ('https://gr1n.github.io/aiodogstatsd/', None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']
html_css_files = [
    ('custom_css.css', {'priority': 100}),
]
master_doc = 'index'
needs_sphinx = "2.0"

# Add some things to the start of the file so we can nicely inherit stuff from the D.py docs
rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
"""
