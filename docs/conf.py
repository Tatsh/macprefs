"""
Configuration file for the Sphinx documentation builder.
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
from datetime import datetime
from operator import itemgetter
from typing import Final
from pathlib import Path
import sys

import tomlkit

PARENT_DIR = Path(__file__).parent.parent
print(PARENT_DIR / 'pyproject.toml')

with (PARENT_DIR / 'pyproject.toml').open() as f:
    tool = tomlkit.load(f).unwrap()['tool']
    authors, name, version = itemgetter('authors', 'name', 'version')(tool['poetry'])

# region Path setup
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, str(PARENT_DIR))
# endregion

author: Final[str] = authors[0]
copyright: Final[str] = str(datetime.now().year)  # noqa: A001
project: Final[str] = name
'''The full version, including alpha/beta/rc tags.'''
release: Final[str] = f'v{version}'
'''
Add any Sphinx extension module names here, as strings. They can be extensions
coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
'''
extensions: Final[list[str]] = (['sphinx.ext.autodoc', 'sphinx.ext.napoleon'] +
                                (['sphinx_click'] if tool.get('scripts') else []))
'''Add any paths that contain templates here, relative to this directory.'''
templates_path: Final[list[str]] = ['_templates']
'''
list of patterns, relative to source directory, that match files and
directories to ignore when looking for source files. This pattern also affects
html_static_path and html_extra_path.
'''
exclude_patterns: Final[list[str]] = []
master_doc: Final[str] = 'index'
'''
Add any paths that contain custom static files (such as style sheets) here,
relative to this directory. They are copied after the builtin static files, so
a file named "default.css" will overwrite the builtin "default.css".
'''
html_static_path: Final[list[str]] = []
'''
The theme to use for HTML and HTML Help pages.  See the documentation for a
list of builtin themes.
'''
html_theme: Final[str] = 'alabaster'
