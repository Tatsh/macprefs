macprefs
========
.. only:: html

   .. image:: https://img.shields.io/pypi/pyversions/macprefs.svg?color=blue&logo=python&logoColor=white
      :target: https://www.python.org/
      :alt: Python versions

   .. image:: https://img.shields.io/pypi/v/macprefs
      :target: https://pypi.org/project/macprefs/
      :alt: PyPI - Version

   .. image:: https://img.shields.io/github/v/tag/Tatsh/macprefs
      :target: https://github.com/Tatsh/macprefs/tags
      :alt: GitHub tag (with filter)

   .. image:: https://img.shields.io/github/license/Tatsh/macprefs
      :target: https://github.com/Tatsh/macprefs/blob/master/LICENSE.txt
      :alt: License

   .. image:: https://img.shields.io/github/commits-since/Tatsh/macprefs/v0.3.4/master
      :target: https://github.com/Tatsh/macprefs/compare/v0.3.4...master
      :alt: GitHub commits since latest release (by SemVer including pre-releases)

   .. image:: https://github.com/Tatsh/macprefs/actions/workflows/qa.yml/badge.svg
      :target: https://github.com/Tatsh/macprefs/actions/workflows/qa.yml
      :alt: QA

   .. image:: https://github.com/Tatsh/macprefs/actions/workflows/tests.yml/badge.svg
      :target: https://github.com/Tatsh/macprefs/actions/workflows/tests.yml
      :alt: Tests

   .. image:: https://coveralls.io/repos/github/Tatsh/macprefs/badge.svg?branch=master
      :target: https://coveralls.io/github/Tatsh/macprefs?branch=master
      :alt: Coverage Status

   .. image:: https://readthedocs.org/projects/macprefs/badge/?version=latest
      :target: https://macprefs.readthedocs.org/?badge=latest
      :alt: Documentation Status

   .. image:: https://www.mypy-lang.org/static/mypy_badge.svg
      :target: http://mypy-lang.org/
      :alt: mypy

   .. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
      :target: https://github.com/pre-commit/pre-commit
      :alt: pre-commit

   .. image:: https://img.shields.io/badge/pydocstyle-enabled-AD4CD3
      :target: http://www.pydocstyle.org/en/stable/
      :alt: pydocstyle

   .. image:: https://img.shields.io/badge/pytest-zz?logo=Pytest&labelColor=black&color=black
      :target: https://docs.pytest.org/en/stable/
      :alt: pytest

   .. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
      :target: https://github.com/astral-sh/ruff
      :alt: Ruff

   .. image:: https://static.pepy.tech/badge/macprefs/month
      :target: https://pepy.tech/project/macprefs
      :alt: Downloads

   .. image:: https://img.shields.io/github/stars/Tatsh/macprefs?logo=github&style=flat
      :target: https://github.com/Tatsh/macprefs/stargazers
      :alt: Stargazers

   .. image:: https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor%3Ddid%3Aplc%3Auq42idtvuccnmtl57nsucz72%26query%3D%24.followersCount%26style%3Dsocial%26logo%3Dbluesky%26label%3DFollow%2520%40Tatsh&query=%24.followersCount&style=social&logo=bluesky&label=Follow%20%40Tatsh
      :target: https://bsky.app/profile/Tatsh.bsky.social
      :alt: Follow @Tatsh

   .. image:: https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social
      :target: https://hostux.social/@Tatsh
      :alt: Mastodon Follow

Command and library to export macOS preferences.

.. only:: html

   Installation
   ------------

   .. code-block:: shell

      pip install macprefs

Usage
-----

``prefs-export`` is the main utility. You can export preferences, generate a
`~/.macos <https://github.com/mathiasbynens/dotfiles/blob/main/.macos>`_-like script, and store the
results in a Git repository.

My primary usage is like so:

.. code-block:: shell

   prefs-export --output-directory ~/.config/defaults --commit

.. only:: html

   See the :doc:`commands <commands>` documentation for more details.

.. only:: man

   Commands
   --------
   .. click:: macprefs.main:main
      :prog: prefs-export
      :nested: full

   .. click:: macprefs.main:install_job
      :prog: macprefs-install-job
      :nested: full

About the generated shell script
--------------------------------

A shell script named ``exec-defaults.sh`` will exist in the output directory. It may be executed,
but is primarily for copying ``defaults`` commands for use in your actual ``~/.macos`` file.

Filtered domains and keys
-------------------------

Certain domains are filtered because they generally do not have anything useful to preserve, such
as ``com.apple.EmojiCache`` which only has a cache of Emoji usage data.

Some keys are filtered, as they contain values that often change and are non-useful, such as
session IDs and UI state (e.g. ``QtUi.MainWin(Geometry|State|Pos|Size)`,
`NSStatusItem Preferred Position``).

Automated usage
---------------

A command ``macprefs-install-job`` is included which will install a daily launchd job. The job name
is ``sh.tat.macprefs``.

.. code-block:: text

   Usage: macprefs-install-job [OPTIONS]

     Job installer.

   Options:
     -K, --deploy-key FILE           Key for pushing to Git repository.
     -o, --output-directory DIRECTORY
                                     Where to store the exported data.
     --help                          Show this message and exit.

If the output directory has a ``.git`` directory, a commit will be automatically made. Be aware that
files will be added and removed automatically.

To stop this job permanently, run
``launchctl unload -w ~/Library/LaunchAgents/sh.tat.macprefs.plist``.

To uninstall this job, after stopping permanently, delete
``~/Library/LaunchAgents/sh.tat.macprefs.plist``.

.. only:: html

   .. toctree::
      :maxdepth: 2
      :caption: Contents:

      commands
      config
      lib
      typing

   Indices and tables
   ==================
   * :ref:`genindex`
   * :ref:`modindex`
