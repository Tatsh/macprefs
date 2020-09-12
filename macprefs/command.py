#!/usr/bin/env python
from os import listdir, makedirs
from os.path import realpath
from pathlib import Path
from shlex import quote
from typing import AsyncIterator, List, Optional, Tuple
import argparse
import asyncio
import asyncio.subprocess as sp
import plistlib
import sys

from .constants import (DOMAIN_SPLIT_DELIMITER, GLOBAL_DOMAIN_ARG,
                        MAX_CONCURRENT_EXPORT_TASKS)
from .filters import BAD_DOMAINS
from .mp_typing import PlistRoot
from .plist2defaults import plist_to_defaults_commands
from .processing import remove_data_fields
from .shell import delete_old_plists, git
from .utils import setup_logging_stderr

__all__ = ('main', )


async def _generate_domains(repo_prefs_dir: Path) -> AsyncIterator[str]:
    log = setup_logging_stderr(verbose=True)
    prefs_dir = Path.home().joinpath('Library/Preferences')
    can_skip: List[int] = []
    p = await asyncio.create_subprocess_shell('defaults domains',
                                              stdout=sp.PIPE)
    deletions = []
    assert p.stdout is not None
    domains_list = (await p.stdout.read()).decode('utf-8').replace(
        ',', '').split(DOMAIN_SPLIT_DELIMITER)
    for i, domain in enumerate(domains_list):
        if (len(domain.strip()) == 0
                or domain == '$(PRODUCT_BUNDLE_IDENTIFIER)'):
            deletions.append(domain)
            continue
        if not prefs_dir.joinpath(f'{domain}.plist').exists():
            p = await asyncio.create_subprocess_shell(
                f'defaults read {quote(domain)}',
                stdout=sp.PIPE,
                stderr=sp.PIPE)
            await p.wait()
            if p.returncode != 0:
                candidates = list(prefs_dir.glob(f'{domain}*'))
                if not candidates:
                    if i in can_skip:
                        deletions.append(domain)
                        continue
                    assert p.stderr is not None
                    if b'does not exist' in await p.stderr.read():
                        log.info('"%s" listed but does not exist',
                                 domain.strip())
                        deletions.append(domain)
                        continue
                    raise ValueError(f'Not sure how to handle {domain}')
                if len(candidates) != 1:
                    candidates_joined = ', '.join(x.name for x in candidates)
                    raise ValueError(
                        f'Multiple candidates: {candidates_joined}')
                domain = candidates[0].stem
                can_skip.extend(
                    range(i + 1,
                          i + len(domain.split(DOMAIN_SPLIT_DELIMITER))))
                yield domain
        else:
            yield domain
    yield GLOBAL_DOMAIN_ARG
    await delete_old_plists(deletions, repo_prefs_dir)


async def _defaults_export(
        domain: str, repo_prefs_dir: Path) -> Tuple[str, Optional[PlistRoot]]:
    command = f'defaults export {quote(domain)}'
    out_domain = 'globalDomain' if domain == GLOBAL_DOMAIN_ARG else domain
    plist_out = repo_prefs_dir.joinpath(f'{out_domain}.plist')
    path_quoted = quote(str(plist_out))
    command += f' {path_quoted}'
    log = setup_logging_stderr(verbose=True)
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


async def _main(out_dir: str) -> int:
    out_dir = realpath(out_dir)
    try:
        makedirs(out_dir)
    except FileExistsError:
        pass
    repo_prefs_dir = Path(out_dir).joinpath('Preferences')

    export_tasks = []
    all_data: List[Tuple[str, Optional[PlistRoot]]] = []
    async for domain in _generate_domains(repo_prefs_dir):
        # spell-checker: disable
        if domain in ('com.apple.Music', 'com.apple.TV',
                      'com.apple.identityservices.idstatuscache',
                      'com.apple.security.KCN'):
            # spell-checker: enable
            continue
        export_tasks.append(_defaults_export(domain, repo_prefs_dir))
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
            async for line in plist_to_defaults_commands(domain, root):
                f.write(line + '\n')
            out_domain = ('globalDomain'
                          if domain == GLOBAL_DOMAIN_ARG else domain)
            known_domains.append(out_domain)
            plist_path = repo_prefs_dir.joinpath(f'{out_domain}.plist')
            p = await asyncio.create_subprocess_shell(
                f'plutil -convert xml1 {quote(str(plist_path))}')
            tasks.append(p.wait())

    await asyncio.wait(tasks)

    log = setup_logging_stderr(verbose=True)

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
    await git(['rm', '-f', '--ignore-unmatch', '--'] + delete_with_git,
              check=True)
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
    await git(['rm', '-f', '--ignore-unmatch', '--'] + delete_with_git_,
              check=True)
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
    args = parser.parse_args()
    return asyncio.run(_main(args.output_directory))


if __name__ == "__main__":
    sys.exit(main())
