from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from shlex import quote
from subprocess import CalledProcessError
from typing import IO, TYPE_CHECKING, Any
import asyncio
import asyncio.subprocess as sp
import logging
import logging.config
import operator
import os
import plistlib
import shutil

from anyio import Path
from platformdirs import user_log_path
import anyio
import anyio.to_thread

from .constants import GLOBAL_DOMAIN_ARG, MAX_CONCURRENT_EXPORT_TASKS
from .exceptions import PropertyListConversionError
from .filters.bad_domains import BAD_DOMAINS, BAD_DOMAIN_PREFIXES
from .plist2defaults import plist_to_defaults_commands
from .processing import make_key_filter, remove_data_fields
from .typing import PlistRoot

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterable

    from .typing import PlistRoot

__all__ = ('defaults_export', 'generate_domains', 'git', 'install_job', 'is_git_installed',
           'prefs_export', 'setup_logging', 'setup_output_directory')

log = logging.getLogger(__name__)


def setup_logging(*,
                  debug: bool = False,
                  force_color: bool = False,
                  no_color: bool = False) -> None:  # pragma: no cover
    """Set up logging configuration."""
    logging.config.dictConfig({
        'disable_existing_loggers': True,
        'root': {
            'level': 'DEBUG' if debug else 'INFO',
            'handlers': ['console'],
        },
        'formatters': {
            'default': {
                '()': 'colorlog.ColoredFormatter',
                'force_color': force_color,
                'format': (
                    '%(light_cyan)s%(asctime)s%(reset)s | %(log_color)s%(levelname)-8s%(reset)s | '
                    '%(light_green)s%(name)s%(reset)s:%(light_red)s%(funcName)s%(reset)s:'
                    '%(blue)s%(lineno)d%(reset)s - %(message)s'),
                'no_color': no_color,
            }
        },
        'handlers': {
            'console': {
                'class': 'colorlog.StreamHandler',
                'formatter': 'default',
            }
        },
        'loggers': {
            'macprefs': {
                'level': 'DEBUG' if debug else 'INFO',
                'handlers': ['console'],
                'propagate': False,
            }
        },
        'version': 1
    })


async def is_git_installed() -> bool:
    return (await (await sp.create_subprocess_exec('bash', '-c', 'command -v git',
                                                   stdout=sp.PIPE)).wait() == 0)


async def generate_domains(bad_domains_addendum: Iterable[str],
                           bad_domain_prefixes_addendum: Iterable[str],
                           *,
                           reset_domains: bool = False,
                           reset_prefixes: bool = False) -> AsyncIterator[str]:
    all_bad_domains = (bad_domains_addendum
                       if reset_domains else {*BAD_DOMAINS, *bad_domains_addendum})
    all_bad_domain_prefixes = (bad_domain_prefixes_addendum if reset_prefixes else
                               {*BAD_DOMAIN_PREFIXES, *bad_domain_prefixes_addendum})
    lib_prefs_path = (await Path.home()) / 'Library/Preferences'
    async for plist in lib_prefs_path.glob('*.plist'):
        if plist.stem in all_bad_domains:
            log.debug('Skipping `%s` because it is in the ignored domains list.', plist.stem)
            continue
        if plist.name.startswith('.'):
            log.debug('Skipping `%s` because it begins with a `.`.', plist.stem)
            continue
        has_ignored_prefix = False
        for prefix in all_bad_domain_prefixes:
            if plist.stem.startswith(prefix):
                log.debug('Skipping `%s` because it begins with `%s`.', plist.stem, prefix)
                has_ignored_prefix = True
                break
        if not has_ignored_prefix:
            yield plist.stem
    yield GLOBAL_DOMAIN_ARG


async def try_parse_plist(domain: str, plist_out: Path) -> tuple[str, PlistRoot]:
    async with await plist_out.open('rb') as f:
        try:
            plist_parsed = await anyio.to_thread.run_sync(plistlib.load, f.wrapped)
        except (plistlib.InvalidFileException, ValueError) as e:
            log.debug('%s: Invalid property list file: %s', f.name, e)
            # If this condition is reached, the domain is likely in the
            # BAD_DOMAINS list so the output will be discarded
            return domain, {}
        return domain, remove_data_fields(plist_parsed)


@asynccontextmanager
async def chdir(path: os.PathLike[Any] | str) -> AsyncIterator[None]:
    """Change directory context manager."""
    old_cwd = await Path.cwd()
    path = Path(path)
    try:
        os.chdir(await path.resolve(strict=True))
        yield
    finally:
        os.chdir(old_cwd)


async def git(cmd: Iterable[str],
              work_tree: Path,
              git_dir: Path | None = None,
              ssh_key: str | None = None) -> sp.Process:
    """Run a Git command."""
    if not git_dir:
        git_dir = (await work_tree.resolve(strict=True)) / '.git'
        if not (await git_dir.exists()):
            await work_tree.mkdir(parents=True, exist_ok=True)
            async with chdir(work_tree):
                log.debug('Running: git init')
                p = await sp.create_subprocess_exec('git', 'init', stdout=sp.PIPE, stderr=sp.PIPE)
                await p.wait()
    if ssh_key:
        await git(('config', 'core.sshCommand',
                   (f'ssh -i {ssh_key} -F /dev/null -o UserKnownHostsFile=/dev/null '
                    '-o StrictHostKeyChecking=no')), work_tree, git_dir)
    cmd_list = list(cmd)
    rest = ' '.join(map(quote, cmd_list))
    log.debug('Running: git "--git-dir=%s" "--work-tree=%s" %s', git_dir, work_tree, rest)
    p = await sp.create_subprocess_exec('git',
                                        f'--git-dir={git_dir}',
                                        f'--work-tree={work_tree}',
                                        *cmd_list,
                                        stderr=sp.PIPE)
    if (await p.wait()) != 0:
        assert p.returncode is not None
        assert p.stderr is not None
        stderr = (await p.stderr.read()).decode()
        quoted_args = ' '.join(
            quote(x) for x in (f'--git-dir={git_dir}', f'--work-tree={work_tree}'))
        raise CalledProcessError(p.returncode, f'git {quoted_args} {rest}', stderr=stderr)
    return p


async def setup_output_directory(out_dir: Path) -> tuple[Path, Path]:
    repo_prefs_dir = out_dir / 'Preferences'
    await out_dir.mkdir(exist_ok=True, parents=True)
    await repo_prefs_dir.mkdir(exist_ok=True, parents=True)
    return out_dir, repo_prefs_dir


async def defaults_export(domain: str, repo_prefs_dir: Path) -> tuple[str, PlistRoot]:
    plist_out = (repo_prefs_dir /
                 f'{"globalDomain" if domain == GLOBAL_DOMAIN_ARG else domain}.plist')
    plist_in = ((await Path.home()) / 'Library/Preferences' /
                f'{".GlobalPreferences" if domain == GLOBAL_DOMAIN_ARG else domain}.plist')
    try:
        try:
            await plist_in.copy(plist_out)  # type: ignore[attr-defined]
        except AttributeError:  # pragma: no cover
            await anyio.to_thread.run_sync(shutil.copy, plist_in, plist_out)
    except PermissionError:
        # Restrictive environment
        return domain, {}
    log.debug('Copied %s to %s.', plist_in, plist_out)
    return await try_parse_plist(domain, plist_out)


def plistlib_dump_xml(plist: Any, fp: IO[bytes]) -> None:
    plistlib.dump(plist, fp, fmt=plistlib.PlistFormat.FMT_XML)


async def install_job(output_dir: Path, deploy_key: Path | None = None) -> int:
    """Install a launchd job to run macprefs."""
    p = await sp.create_subprocess_exec('bash', '-c', 'command -v prefs-export', stdout=sp.PIPE)
    assert p.stdout is not None
    prefs_export_path = (await p.stdout.read()).decode().strip()
    plist_path = (await Path.home()) / 'Library/LaunchAgents/sh.tat.macprefs.plist'
    log_path = str(user_log_path('macprefs', ensure_exists=True) / 'macprefs.log')
    async with await plist_path.open('wb+') as f:
        await anyio.to_thread.run_sync(
            plistlib_dump_xml, {
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
            }, f.wrapped)
    plist_path_s = str(plist_path)
    cmd: tuple[str, ...] = ('launchctl', 'stop', plist_path_s)
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    await (await sp.create_subprocess_exec(*cmd, stderr=sp.PIPE, stdout=sp.PIPE)).wait()
    cmd = ('launchctl', 'unload', '-w', plist_path_s)
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    await (await sp.create_subprocess_exec(*cmd, stderr=sp.PIPE, stdout=sp.PIPE)).wait()
    cmd = ('launchctl', 'load', '-w', plist_path_s)
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    process1 = await sp.create_subprocess_exec(*cmd)
    await process1.wait()
    cmd = ('launchctl', 'start', plist_path_s)
    log.debug('Running: %s', ' '.join(quote(x) for x in cmd))
    process2 = await sp.create_subprocess_exec(*cmd)
    await process2.wait()
    return 0 if process1.returncode == 0 and process2.returncode == 0 else 1


async def prefs_export(out_dir: Path,
                       config: dict[str, Any] | None = None,
                       deploy_key: Path | None = None,
                       *,
                       commit: bool = False) -> None:
    """
    Export filtered preferences to a directory.

    Also writes scripts `exec-defaults.sh` and `rejected-defaults.sh` to the output directory, both
    of which contain ``defaults`` commands to set preferences equivalent to the exported property
    list files.
    """
    config = config or {}
    has_git = await is_git_installed()
    out_dir, repo_prefs_dir = await setup_output_directory(out_dir)
    export_tasks = []
    all_data: list[tuple[str, PlistRoot]] = []
    async for domain in generate_domains(
        {*config.get('extend-ignore-domains', []), *config.get('ignore-domains', [])}, {
            *config.get('extend-ignore-domain-prefixes', []),
            *config.get('ignore-domain-prefixes', [])
        },
            reset_domains='ignore-domains' in config,
            reset_prefixes='ignore-domain-prefixes' in config):
        export_tasks.append(defaults_export(domain, repo_prefs_dir))
        if len(export_tasks) == MAX_CONCURRENT_EXPORT_TASKS:
            all_data.extend(await asyncio.gather(*export_tasks))
            export_tasks = []
    all_data.extend(await asyncio.gather(*export_tasks))
    exec_defaults = out_dir / 'exec-defaults.sh'
    tasks = []
    known_domains = []
    key_filter = make_key_filter(
        {*config.get('extend-ignore-key-regexes', []), *config.get('ignore-key-regexes', [])}, {
            **config.get('extend-ignore-keys', {}),
            **config.get('ignore-keys', {})
        },
        reset_re='ignore-key-regexes' in config,
        reset_bad_keys='ignore-keys' in config)
    async with await exec_defaults.open('w+') as f:
        await f.write('#!/usr/bin/env bash\n')
        await f.write('# shellcheck disable=SC1003,SC1010,SC1112,SC2016,SC2088\n')
        await f.write('# This file is generated, but is versioned.\n\n')
        for domain, root in sorted(all_data, key=operator.itemgetter(0)):
            if not root:  # Skip empty dicts
                continue
            for line in plist_to_defaults_commands(domain, root, key_filter):
                await f.write(f'{line}\n')
            out_domain = ('globalDomain' if domain == GLOBAL_DOMAIN_ARG else domain)
            known_domains.append(out_domain)
            plist_path = repo_prefs_dir / f'{out_domain}.plist'
            log.debug('Executing: plutil -convert xml1 %s', quote(plist_path.name))
            p = await sp.create_subprocess_exec('plutil', '-convert', 'xml1', plist_path)
            tasks.append(asyncio.create_task(p.wait()))
    await exec_defaults.chmod(0o755)
    rejected_defaults = out_dir / 'rejected-defaults.sh'
    async with await rejected_defaults.open('w+') as f:
        await f.write('# Rejected defaults values.\n')
        await f.write('# shellcheck disable=SC1003,SC1010,SC1112,SC2016,SC2088\n')
        await f.write('# This file is generated, but is versioned.\n\n')
        for domain, root in sorted(all_data, key=operator.itemgetter(0)):
            if not root:  # Skip empty dicts
                continue
            for line in plist_to_defaults_commands(domain, root, key_filter, invert_filters=True):
                await f.write(f'{line}\n')
    assert len(known_domains) > 0
    results = (await asyncio.wait(tasks))[0]
    if any(future.result() != 0 for future in results):
        raise PropertyListConversionError
    if has_git and (delete_with_git := [
            str(x) async for x in repo_prefs_dir.iterdir()
            if x.name != '.gitignore' and x.name[:-6] not in known_domains and (await x.exists())
            if not (await x.is_dir())
    ]):
        # Clean up very old plists
        await git(('rm', '-f', '--ignore-unmatch', '--', *delete_with_git), out_dir)
        log.debug('Executing: rm -f -- %s', ' '.join(map(quote, delete_with_git)))
        p = await sp.create_subprocess_exec('rm', '-f', '--', *delete_with_git, stderr=sp.PIPE)
        await p.wait()
    if has_git and commit:
        log.debug('Committing changes.')
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
            log.info('Likely no changes to commit.')
