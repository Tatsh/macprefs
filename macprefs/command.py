#!/usr/bin/env python
# pylint: disable=too-many-locals,compare-to-zero
from itertools import chain
from os import chmod, listdir, makedirs
from os.path import realpath
from pathlib import Path
from shlex import quote
from typing import AsyncIterator, List, Tuple
import argparse
import asyncio
import asyncio.subprocess as sp
import plistlib
import sys

from .constants import GLOBAL_DOMAIN_ARG, MAX_CONCURRENT_EXPORT_TASKS
from .filters import BAD_DOMAINS
from .mp_typing import PlistRoot
from .plist2defaults import plist_to_defaults_commands
from .processing import remove_data_fields
from .shell import git
from .utils import setup_logging_stderr

__all__ = ('main', )


async def _has_git() -> bool:
    p = await sp.create_subprocess_shell('bash -c "command -v git"',
                                         stdout=sp.PIPE)
    await p.wait()
    return p.returncode == 0


async def _generate_domains() -> AsyncIterator[str]:
    for plist in (x for x in (
            Path.home().joinpath('Library/Preferences').glob('*.plist'))
                  if x.stem and x.stem != '$(PRODUCT_BUNDLE_IDENTIFIER)'
                  and not x.name.startswith('.')):
        yield plist.stem
    yield GLOBAL_DOMAIN_ARG


async def _defaults_export(domain: str,
                           repo_prefs_dir: Path,
                           debug: bool = False) -> Tuple[str, PlistRoot]:
    command = f'defaults export {quote(domain)}'
    out_domain = 'globalDomain' if domain == GLOBAL_DOMAIN_ARG else domain
    plist_out = repo_prefs_dir.joinpath(f'{out_domain}.plist')
    path_quoted = quote(str(plist_out))
    command += f' {path_quoted}'
    log = setup_logging_stderr(verbose=debug)
    log.debug('Running: %s', command)
    p = await asyncio.create_subprocess_shell(command,
                                              stdout=sp.PIPE,
                                              stderr=sp.PIPE)
    await p.wait()
    if p.returncode != 0:
        assert p.stderr is not None
        err = (await p.stderr.read()).decode('utf-8')
        raise RuntimeError(
            f'Non-zero exit status from defaults. STDERR: {err}')
    with plist_out.open('rb') as f:
        return domain, await remove_data_fields(plistlib.load(f))


async def _setup_out_dir(out_dir: str) -> Tuple[str, Path]:
    out_dir = realpath(out_dir)
    repo_prefs_dir = Path(out_dir).joinpath('Preferences')
    # pylint: disable=too-many-try-statements
    try:
        makedirs(out_dir)
        makedirs(str(repo_prefs_dir))
    except FileExistsError:
        pass
    # pylint: enable=too-many-try-statements
    return out_dir, repo_prefs_dir


async def _main(out_dir: str, debug: bool = False) -> int:
    log = setup_logging_stderr(verbose=debug)
    has_git = await _has_git()

    out_dir, repo_prefs_dir = await _setup_out_dir(out_dir)
    export_tasks = []
    all_data: List[Tuple[str, PlistRoot]] = []
    async for domain in _generate_domains():
        # spell-checker: disable
        if domain in ('com.apple.Music', 'com.apple.TV',
                      'com.apple.identityservices.idstatuscache',
                      'com.apple.security.KCN'):
            # spell-checker: enable
            continue
        export_tasks.append(_defaults_export(domain, repo_prefs_dir, debug))
        if len(export_tasks) == MAX_CONCURRENT_EXPORT_TASKS:
            all_data.extend(await asyncio.gather(*export_tasks))
            export_tasks = []
    all_data.extend(await asyncio.gather(*export_tasks))

    exec_defaults = Path(out_dir).joinpath('exec-defaults.sh')
    tasks = []
    known_domains = []
    with exec_defaults.open('w+') as f:
        f.write('#!/usr/bin/env bash\n')
        f.write('# shellcheck disable=SC1112,SC2088,SC1010,SC2016,SC1003\n')
        f.write('# This file is generated, but is versioned.\n\n')
        for domain, root in sorted(all_data, key=lambda x: x[0]):
            if not root:
                continue
            async for line in plist_to_defaults_commands(domain, root, debug):
                f.write(line + '\n')
            out_domain = ('globalDomain'
                          if domain == GLOBAL_DOMAIN_ARG else domain)
            known_domains.append(out_domain)
            plist_path = repo_prefs_dir.joinpath(f'{out_domain}.plist')
            cmd = f'plutil -convert xml1 {quote(str(plist_path))}'
            log.debug('Executing: %s', cmd)
            p = await asyncio.create_subprocess_shell(cmd)
            tasks.append(p.wait())
    chmod(str(exec_defaults), 0o755)
    await asyncio.wait(tasks)

    if has_git:
        # Clean up very old plists
        delete_with_git = [
            str(j[1])
            for j in ((file, file_)
                      for file, file_ in ((x, repo_prefs_dir.joinpath(x))
                                          for x in listdir(str(repo_prefs_dir))
                                          if x != '.gitignore')
                      if file[:-6] not in known_domains and file_.exists()
                      if not file_.is_dir())
        ]
        await git(chain(('rm', '-f', '--ignore-unmatch', '--'),
                        delete_with_git),
                  check=True,
                  work_tree=out_dir,
                  debug=debug)
        all_files = ' '.join(map(quote, delete_with_git))
        cmd = f'rm -f -- {all_files}'
        log.debug('Executing: %s', cmd)
        p = await asyncio.create_subprocess_shell(f'rm -f -- {all_files}')
        await p.wait()

    delete_with_git_ = []
    delete_with_rm = []
    for x in BAD_DOMAINS:
        if x == 'MobileMeAccounts':
            continue
        plist = repo_prefs_dir.joinpath(f'{x}.plist')
        delete_with_git_.append(str(plist))
        delete_with_rm.append(quote(str(plist)))
    if has_git:
        await git(chain(('rm', '-f', '--ignore-unmatch', '--'),
                        delete_with_git_),
                  check=True,
                  debug=debug,
                  work_tree=out_dir)
    deletions = ' '.join(delete_with_rm)
    cmd = f'rm -f -- {deletions}'
    log.debug('Executing: %s', cmd)
    p = await asyncio.create_subprocess_shell(cmd)
    await p.wait()

    return 0


def main() -> int:
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-directory', default='.')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    ret = loop.run_until_complete(
        _main(args.output_directory, debug=args.debug))
    loop.close()
    return ret


if __name__ == "__main__":
    sys.exit(main())
