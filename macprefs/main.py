from collections.abc import Iterator
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from itertools import chain
from pathlib import Path
from shlex import quote
from subprocess import CalledProcessError
import asyncio
import asyncio.subprocess as sp
import logging
import operator
import plistlib
import shutil

import click

from .constants import GLOBAL_DOMAIN_ARG, MAX_CONCURRENT_EXPORT_TASKS
from .exceptions import PropertyListConversionError
from .plist2defaults import plist_to_defaults_commands
from .processing import remove_data_fields
from .shell import git
from .typing import PlistRoot

__all__ = ('main',)

EXECUTOR = ProcessPoolExecutor()
logger = logging.getLogger(__name__)


async def _has_git() -> bool:
    return (await (await sp.create_subprocess_exec('bash', '-c', 'command -v git',
                                                   stdout=sp.PIPE)).wait() == 0)


def _generate_domains() -> Iterator[str]:
    for plist in (
            x for x in (Path.home() / 'Library/Preferences').glob('*.plist')
            if x.stem and x.stem != '$(PRODUCT_BUNDLE_IDENTIFIER)' and not x.name.startswith('.')):
        yield plist.stem
    yield GLOBAL_DOMAIN_ARG


def try_parse_plist(domain: str, plist_out: Path) -> tuple[str, PlistRoot]:
    with plist_out.open('rb') as f:
        try:
            plist_parsed = plistlib.load(f)
        except (plistlib.InvalidFileException, ValueError) as e:
            logger.debug('%s: Invalid property list file: %s', f.name, e)
            # If this condition is reached, the domain is likely in the
            # BAD_DOMAINS list so the output will be discarded
            return domain, {}
        return domain, remove_data_fields(plist_parsed)


async def _defaults_export(domain: str, repo_prefs_dir: Path) -> tuple[str, PlistRoot]:
    loop = asyncio.get_running_loop()
    plist_out = (repo_prefs_dir /
                 f'{"globalDomain" if domain == GLOBAL_DOMAIN_ARG else domain}.plist')
    plist_in = (Path.home() / 'Library/Preferences' /
                f'{".GlobalPreferences" if domain == GLOBAL_DOMAIN_ARG else domain}.plist')
    try:
        await loop.run_in_executor(None, shutil.copy, plist_in, plist_out)
    except PermissionError:
        # Restrictive environment
        return domain, {}
    logger.info('Copied %s to %s.', plist_in, plist_out)
    return await loop.run_in_executor(None, try_parse_plist, domain, plist_out)


def _setup_out_dir(out_dir: Path) -> tuple[Path, Path]:
    repo_prefs_dir = out_dir / 'Preferences'
    out_dir.mkdir(exist_ok=True, parents=True)
    repo_prefs_dir.mkdir(exist_ok=True, parents=True)
    return out_dir, repo_prefs_dir


async def _do_main(out_dir: Path, deploy_key: Path | None = None, *, commit: bool = False) -> None:
    loop = asyncio.get_running_loop()
    has_git = await _has_git()
    out_dir, repo_prefs_dir = await loop.run_in_executor(None, _setup_out_dir, out_dir)
    export_tasks = []
    all_data: list[tuple[str, PlistRoot]] = []
    for domain in _generate_domains():
        export_tasks.append(_defaults_export(domain, repo_prefs_dir))
        if len(export_tasks) == MAX_CONCURRENT_EXPORT_TASKS:
            all_data.extend(await asyncio.gather(*export_tasks))
            export_tasks = []
    all_data.extend(await asyncio.gather(*export_tasks))
    exec_defaults = Path(out_dir) / 'exec-defaults.sh'
    tasks = []
    known_domains = []
    with exec_defaults.open('w+') as f:
        f.write('#!/usr/bin/env bash\n')
        f.write('# shellcheck disable=SC1003,SC1010,SC1112,SC2016,SC2088\n')
        f.write('# This file is generated, but is versioned.\n\n')
        for domain, root in sorted(all_data, key=operator.itemgetter(0)):
            if not root:  # Skip empty dicts
                continue
            for line in plist_to_defaults_commands(domain, root):
                f.write(f'{line}\n')
            out_domain = ('globalDomain' if domain == GLOBAL_DOMAIN_ARG else domain)
            known_domains.append(out_domain)
            plist_path = repo_prefs_dir / f'{out_domain}.plist'
            logger.debug('Executing: plutil -convert xml1 %s', quote(plist_path.name))
            p = await asyncio.create_subprocess_exec('plutil', '-convert', 'xml1', plist_path)
            tasks.append(asyncio.create_task(p.wait()))
    exec_defaults.chmod(0o755)
    rejected_defaults = Path(out_dir) / 'rejected-defaults.sh'
    with rejected_defaults.open('w+') as f:
        f.write('# Rejected defaults values.\n')
        f.write('# shellcheck disable=SC1003,SC1010,SC1112,SC2016,SC2088\n')
        f.write('# This file is generated, but is versioned.\n\n')
        for domain, root in sorted(all_data, key=operator.itemgetter(0)):
            if not root:  # Skip empty dicts
                continue
            for line in plist_to_defaults_commands(domain,
                                                   root,
                                                   domain_filter=None,
                                                   inverse_filters=True):
                f.write(f'{line}\n')
    assert len(known_domains) > 0
    results = (await asyncio.wait(tasks))[0]
    if any(future.result() != 0 for future in results):
        raise PropertyListConversionError
    if has_git and (delete_with_git := [
            str(x) for x in repo_prefs_dir.iterdir()
            if x.name != '.gitignore' and x.name[:-6] not in known_domains and x.exists()
            if not x.is_dir()
    ]):
        # Clean up very old plists
        await git(chain(('rm', '-f', '--ignore-unmatch', '--'), delete_with_git), out_dir)
        logger.debug('Executing: rm -f -- %s', ' '.join(map(quote, delete_with_git)))
        p = await asyncio.create_subprocess_exec('rm', '-f', '--', *delete_with_git, stderr=sp.PIPE)
        await p.wait()
    if has_git and commit:
        logger.debug('Committing changes.')
        await git(('add', '.'), out_dir)
        try:
            await git(('commit', '--no-gpg-sign', '--quiet', '--no-verify',
                       '--author=macprefs <macprefs@tat.sh>', '-m',
                       f'Automatic commit @ {datetime.now(tz=timezone.utc).strftime("%c")}'),
                      out_dir)
            if deploy_key:
                stdout = (await git(('branch', '--show-current'), out_dir)).stdout
                assert stdout is not None
                await git(('push', '-u', '--porcelain', '--no-signed', 'origin',
                           (await stdout.read()).decode().strip()), out_dir)
        except CalledProcessError:
            logger.info('Likely no changes to commit.')


async def _main(out_dir: Path,
                deploy_key: Path | None = None,
                *,
                commit: bool = False,
                debug: bool = False) -> int:
    try:
        await _do_main(out_dir, deploy_key, commit=commit)
    except Exception:
        if debug:
            logger.exception('Caught exception.')
        return 1
    return 0


@click.command('prefs-export', context_settings={'help_option_names': ['-h', '--help']})
@click.option('-K',
              '--deploy-key',
              help='Key for pushing to Git repository.',
              type=click.Path(dir_okay=False, exists=True, path_type=Path, resolve_path=True))
@click.option('-c', '--commit', help='Commit the changes with Git.', is_flag=True)
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
@click.option('-o',
              '--output-directory',
              default=Path.home() / '.local/share/prefs-export',
              help='Where to store the exported data.',
              type=click.Path(file_okay=False, path_type=Path, resolve_path=True))
def main(output_directory: Path,
         deploy_key: Path | None = None,
         *,
         commit: bool = False,
         debug: bool = False) -> None:
    """Export preferences."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.ERROR)
    if (asyncio.run(_main(output_directory, commit=commit, debug=debug, deploy_key=deploy_key),
                    debug=debug) != 0):
        raise click.Abort


async def _install_job(output_dir: Path, deploy_key: Path | None = None) -> int:
    p = await sp.create_subprocess_exec('bash', '-c', 'command -v prefs-export', stdout=sp.PIPE)
    assert p.stdout is not None
    prefs_export_path = (await p.stdout.read()).decode().strip()
    home = Path.home()
    plist_path = home / 'Library/LaunchAgents/sh.tat.macprefs.plist'
    log_path = f'{home}/Library/Logs/macprefs.log'
    with plist_path.open('wb+') as f:
        plistlib.dump(
            {
                'Label':
                    'sh.tat.macprefs',
                'ProgramArguments': [
                    prefs_export_path, '--output-directory',
                    str(output_dir.resolve(strict=True)), '--commit'
                ] + (['--deploy-key', deploy_key.resolve(strict=True)] if deploy_key else []),
                'RunAtLoad':
                    True,
                'StandardErrorPath':
                    log_path,
                'StandardOutPath':
                    log_path,
                'StartCalendarInterval': {
                    'Hour': 0,
                    'Minute': 0
                }
            },
            f,
            fmt=plistlib.PlistFormat.FMT_XML)
    await (await sp.create_subprocess_exec('launchctl',
                                           'stop',
                                           plist_path,
                                           stderr=sp.PIPE,
                                           stdout=sp.PIPE)).wait()
    await (await sp.create_subprocess_exec('launchctl',
                                           'unload',
                                           '-w',
                                           plist_path,
                                           stderr=sp.PIPE,
                                           stdout=sp.PIPE)).wait()
    process1 = await sp.create_subprocess_exec('launchctl', 'load', '-w', plist_path)
    await process1.wait()
    process2 = await sp.create_subprocess_exec('launchctl', 'start', plist_path)
    await process2.wait()
    return 0 if process1.returncode == 0 and process2.returncode == 0 else 1


@click.command('macprefs-install-job', context_settings={'help_option_names': ['-h', '--help']})
@click.option('-K',
              '--deploy-key',
              help='Key for pushing to Git repository.',
              type=click.Path(dir_okay=False, exists=True, resolve_path=True))
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
@click.option('-o',
              '--output-directory',
              default=str(Path.home() / '.local/share/prefs-export'),
              help='Where to store the exported data.',
              type=click.Path(file_okay=False, resolve_path=True))
def install_job(output_directory: str,
                deploy_key: str | None = None,
                *,
                debug: bool = False) -> None:
    """Job installer."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.ERROR)
    if (asyncio.run(_install_job(Path(output_directory),
                                 Path(deploy_key) if deploy_key else None),
                    debug=debug) != 0):
        raise click.Abort
