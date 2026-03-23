macprefs
========

.. include:: badges.rst

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
