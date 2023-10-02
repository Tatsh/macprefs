# macprefs

[![QA](https://github.com/Tatsh/macprefs/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/macprefs/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/macprefs/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/macprefs/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/macprefs/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/macprefs?branch=master)
[![Documentation Status](https://readthedocs.org/projects/macprefs/badge/?version=latest)](https://macprefs.readthedocs.io/en/latest/?badge=latest)
![PyPI - Version](https://img.shields.io/pypi/v/macprefs)
![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/macprefs)
![GitHub](https://img.shields.io/github/license/Tatsh/macprefs)
![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/macprefs/v0.3.4/master)

Export and keep track of changes to your preferences.

## How to use

```plain
Usage: prefs-export [OPTIONS]

  Export preferences.

Options:
  -K, --deploy-key FILE           Key for pushing to Git repository.
  -c, --commit                    Commit the changes with Git.
  -d, --debug                     Enable debug logging.
  -o, --output-directory DIRECTORY
                                  Where to store the exported data.
  --help                          Show this message and exit.
```

`prefs-export` is the main utility. You can export preferences, generate a
[`~/.macos`](https://github.com/mathiasbynens/dotfiles/blob/main/.macos)-like script, and store the
results in a Git repository.

My primary usage is like so:

```shell
prefs-export -o ~/.config/defaults -c
```

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
