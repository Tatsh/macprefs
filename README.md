# macprefs

[![Python versions](https://img.shields.io/pypi/pyversions/macprefs.svg?color=blue&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI - Version](https://img.shields.io/pypi/v/macprefs)](https://pypi.org/project/macprefs/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/macprefs)](https://github.com/Tatsh/macprefs/tags)
[![License](https://img.shields.io/github/license/Tatsh/macprefs)](https://github.com/Tatsh/macprefs/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/macprefs/v0.4.0/master)](https://github.com/Tatsh/macprefs/compare/v0.4.0...master)
[![QA](https://github.com/Tatsh/macprefs/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/macprefs/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/macprefs/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/macprefs/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/macprefs/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/macprefs?branch=master)
[![Documentation Status](https://readthedocs.org/projects/macprefs/badge/?version=latest)](https://macprefs.readthedocs.org/?badge=latest)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-enabled-AD4CD3)](http://www.pydocstyle.org/en/stable/)
[![pytest](https://img.shields.io/badge/pytest-zz?logo=Pytest&labelColor=black&color=black)](https://docs.pytest.org/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/macprefs/month)](https://pepy.tech/project/macprefs)
[![Stargazers](https://img.shields.io/github/stars/Tatsh/macprefs?logo=github&style=flat)](https://github.com/Tatsh/macprefs/stargazers)

[![@Tatsh](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor%3Ddid%3Aplc%3Auq42idtvuccnmtl57nsucz72%26query%3D%24.followersCount%26style%3Dsocial%26logo%3Dbluesky%26label%3DFollow%2520%40Tatsh&query=%24.followersCount&style=social&logo=bluesky&label=Follow%20%40Tatsh)](https://bsky.app/profile/Tatsh.bsky.social)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social)](https://hostux.social/@Tatsh)

Command and library to export macOS preferences.

## Installation

### Pip

```shell
pip install macprefs
```

## Usage

```plain
Usage: prefs-export [OPTIONS]

  Export preferences.

Options:
  -C, --config FILE               Path to the configuration file.
  -K, --deploy-key FILE           Key for pushing to Git repository.
  -c, --commit                    Commit the changes with Git.
  -d, --debug                     Enable debug logging.
  -o, --output-directory DIRECTORY
                                  Where to store the exported data.
  -h, --help                      Show this message and exit.
```

`prefs-export` is the main utility. You can export preferences, generate a
[`~/.macos`](https://github.com/mathiasbynens/dotfiles/blob/main/.macos)-like script, and store the
results in a Git repository.

My primary usage is like so:

```shell
prefs-export --output-directory ~/.config/defaults --commit
```

The default output directory is `~/Library/Application Support/macprefs`.

## Configuration

The configuration file is a TOML file. By default `prefs-export` checks for the path
`~/Library/Application Support/macprefs/config.toml`. Example file:

```toml
# The extend-* options extend the default values used by macprefs.
[tool.macprefs]
extend-ignore-keys = {'domain_name': ['key-to-ignore1', 're:^key-to-ignore']}
extend-ignore-domain-prefixes = ['org.gimp.gimp-']
extend-ignore-domains = ['domain1', 'domain2']
extend-ignore-key-regexes = ['QuickLookPreview_[A-Z0-9-\\.]+']
# Only set these if you want to override the default values used by macprefs.
# ignore-domain-prefixes = []
# ignore-domains = []
# ignore-key-regexes = []
# ignore-keys = {}

deploy-key = '/path/to/deploy-key'
```

In `extend-ignore-keys` and `ignore-keys`, a string value to ignore can be prefixed with `re:` to
indicate it is a regular expression.

## About the generated shell script

A shell script named `exec-defaults.sh` will exist in the output directory. It may be executed, but
is primarily for copying `defaults` commands for use in your actual `~/.macos` file.

### Filtered domains and keys

Certain domains are filtered because they generally do not have anything useful to preserve, such
as `com.apple.EmojiCache` which only has a cache of Emoji usage data.

Some keys are filtered, as they contain values that often changing and non-useful values such as
session IDs and UI state (e.g. `QtUi.MainWin(Geometry|State|Pos|Size)`,
`NSStatusItem Preferred Position`).

## Automated usage

A command `macprefs-install-job` is included which will install a daily launchd job. The job name is
`sh.tat.macprefs`

```plain
Usage: macprefs-install-job [OPTIONS]

  Job installer.

Options:
  -K, --deploy-key FILE           Key for pushing to Git repository.
  -o, --output-directory DIRECTORY
                                  Where to store the exported data.
  --help                          Show this message and exit.
```

If the output directory has a `.git` directory, a commit will be automatically made. Be aware that
files will be added and removed automatically.

To stop this job permanently, run `launchctl unload -w ~/Library/LaunchAgents/sh.tat.macprefs.plist`.

To uninstall this job, after stopping permanently, delete `~/Library/LaunchAgents/sh.tat.macprefs.plist`.
