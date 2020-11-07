# macprefs

Export and keep track of changes to your preferences.

## How to use

```
usage: prefs-export [-h] [-o OUTPUT_DIRECTORY] [-c]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Where to store the exported data
  -c, --commit          Commit the changes with Git
```

`prefs-export` is the main utility. You can export preferences, generate a [`~/.macos`](https://github.com/mathiasbynens/dotfiles/blob/main/.macos)-like script, and store the results in a Git repository.

My primary usage is like so:

```shell
prefs-export -o ~/.config/defaults -c
```

## About the generated shell script

A shell script named `exec-defaults.sh` will exist in the output directory. It may be executed, but is primarily for copying `defaults` commands for use in your actual `~/.macos` file.

### Filtered domains and keys

Certain domains are filtered because they generally do not have anything useful to preserve, such as `com.apple.EmojiCache` which only has a cache of Emoji usage data.

Some keys are filtered, as they contain values that often changing and non-useful values such as session IDs and UI state (e.g. `QtUi.MainWin(Geometry|State|Pos|Size)`, `NSStatusItem Preferred Position`).

## Automated usage

A command `macprefs-install-job` is included which will install a daily launchd job. The job name is `sh.tat.macprefs`

```
usage: macprefs-install-job [-h] [-o OUTPUT_DIRECTORY]

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Where to store the exported data
```

If the output directory has a `.git` directory, a commit will be automatically made. Be aware that files will be added and removed automatically.

To stop this job permanently, run `launchctl unload -w ~/Library/LaunchAgents/sh.tat.macprefs.plist`.

To uninstall this job, after stopping permanently, delete `~/Library/LaunchAgents/sh.tat.macprefs.plist`.
