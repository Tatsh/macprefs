from datetime import datetime
from itertools import chain
from pathlib import Path
from shlex import quote
from typing import AsyncIterator, cast
import asyncio
import asyncio.subprocess as sp
import plistlib
import shutil

from loguru import logger
import click

from .constants import GLOBAL_DOMAIN_ARG, MAX_CONCURRENT_EXPORT_TASKS
from .filters import BAD_DOMAINS
from .mp_typing import PlistRoot
from .plist2defaults import plist_to_defaults_commands
from .processing import remove_data_fields
from .shell import git
from .utils import setup_logging

__all__ = ('main',)


async def _has_git() -> bool:
    p = await sp.create_subprocess_shell('bash -c "command -v git"', stdout=sp.PIPE)
    await p.wait()
    return p.returncode == 0


async def _generate_domains() -> AsyncIterator[str]:
    for plist in (
            x for x in (Path.home() / 'Library/Preferences').glob('*.plist')
            if x.stem and x.stem != '$(PRODUCT_BUNDLE_IDENTIFIER)' and not x.name.startswith('.')):
        yield plist.stem
    yield GLOBAL_DOMAIN_ARG


async def _defaults_export(domain: str, repo_prefs_dir: Path) -> tuple[str, PlistRoot]:
    plist_out = (repo_prefs_dir /
                 f'{"globalDomain" if domain == GLOBAL_DOMAIN_ARG else domain}.plist')
    shutil.copy(
        Path.home() / 'Library/Preferences' /
        f'{".GlobalPreferences" if domain == GLOBAL_DOMAIN_ARG else domain}.plist', plist_out)
    with plist_out.open('rb') as f:
        try:
            plist_parsed = plistlib.load(f)
        except plistlib.InvalidFileException as e:
            logger.debug(f'Invalid property list file: {e}')
            # If this condition is reached, the domain is likely in the
            # BAD_DOMAINS list so the output will be discarded
            return domain, {}
        return domain, await remove_data_fields(plist_parsed)


async def _setup_out_dir(out_dir: Path) -> tuple[Path, Path]:
    repo_prefs_dir = out_dir / 'Preferences'
    out_dir.mkdir(exist_ok=True, parents=True)
    repo_prefs_dir.mkdir(exist_ok=True, parents=True)
    return out_dir, repo_prefs_dir


async def _main(out_dir: Path,
                debug: bool = False,
                commit: bool = False,
                deploy_key: str | None = None) -> int:
    try:
        has_git = await _has_git()
        out_dir, repo_prefs_dir = await _setup_out_dir(out_dir)
        export_tasks = []
        all_data: list[tuple[str, PlistRoot]] = []
        async for domain in _generate_domains():
            # spell-checker: disable
            if domain in ('com.apple.Music', 'com.apple.TV',
                          'com.apple.identityservices.idstatuscache', 'com.apple.security.KCN'):
                # spell-checker: enable
                continue
            export_tasks.append(_defaults_export(domain, repo_prefs_dir))
            if len(export_tasks) == MAX_CONCURRENT_EXPORT_TASKS:
                all_data.extend(await asyncio.gather(*export_tasks))
                export_tasks = []
        all_data.extend(await asyncio.gather(*export_tasks))
        exec_defaults = Path(out_dir) / 'exec-defaults.sh'
        is_new = not exec_defaults.exists()
        tasks = []
        known_domains = []
        with exec_defaults.open('w+') as f:
            f.write('#!/usr/bin/env bash\n')
            f.write('# shellcheck disable=SC1003,SC1010,SC1112,SC2016,SC2088\n')
            f.write('# This file is generated, but is versioned.\n\n')
            for domain, root in sorted(all_data, key=lambda x: x[0]):
                if not root:
                    continue
                async for line in plist_to_defaults_commands(domain, root, debug):
                    f.write(line + '\n')
                out_domain = ('globalDomain' if domain == GLOBAL_DOMAIN_ARG else domain)
                known_domains.append(out_domain)
                plist_path = repo_prefs_dir / f'{out_domain}.plist'
                cmd = f'plutil -convert xml1 {quote(str(plist_path))}'
                logger.debug(f'Executing: {cmd}')
                p = await asyncio.create_subprocess_shell(cmd)
                tasks.append(asyncio.create_task(p.wait()))
        exec_defaults.chmod(0o755)
        results = cast(set[asyncio.Future[int]], (await asyncio.wait(tasks))[0])
        if any(future.result() != 0 for future in results):
            raise RuntimeError('At least one plist conversion failed')
        if has_git and not is_new:
            # Clean up very old plists
            delete_with_git = [
                str(j[1]) for j in ((file, file_)
                                    for file, file_ in ((x, repo_prefs_dir.joinpath(x))
                                                        for x in repo_prefs_dir.iterdir()
                                                        if x != '.gitignore')
                                    if str(file)[:-6] not in known_domains and file_.exists()
                                    if not file_.is_dir())
            ]
            await git(chain(('rm', '-f', '--ignore-unmatch', '--'), delete_with_git),
                      check=True,
                      work_tree=out_dir)
            all_files = ' '.join(map(quote, delete_with_git))
            cmd = f'rm -f -- {all_files}'
            logger.debug('Executing: %s', cmd)
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
            await git(chain(('rm', '-f', '--ignore-unmatch', '--'), delete_with_git_),
                      check=True,
                      work_tree=out_dir)
        deletions = ' '.join(delete_with_rm)
        cmd = f'rm -f -- {deletions}'
        logger.debug('Executing: %s', cmd)
        p = await asyncio.create_subprocess_shell(cmd)
        await p.wait()
        if has_git and commit:
            logger.debug('Committing changes')
            await git(('add', '.'), work_tree=out_dir, check=True)
            await git(('commit', '--no-gpg-sign', '--quiet', '--no-verify',
                       '--author=macprefs <macprefs@tat.sh>', '-m',
                       f'Automatic commit @ {datetime.now().strftime("%c")}'),
                      work_tree=out_dir,
                      check=True)
            if deploy_key:
                stdout = (await git(('branch', '--show-current'), check=True,
                                    work_tree=out_dir)).stdout
                assert stdout is not None
                await git(('push', '-u', '--porcelain', '--no-signed', 'origin',
                           (await stdout.read()).decode().strip()),
                          work_tree=out_dir,
                          check=True)
    except Exception as e:
        if debug:
            logger.exception(e)
        return 1
    return 0


@click.command('prefs-export')
@click.option('-K',
              '--deploy-key',
              help='Key for pushing to Git repository.',
              type=click.Path(dir_okay=False, exists=True, resolve_path=True))
@click.option('-c', '--commit', help='Commit the changes with Git.', is_flag=True)
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
@click.option('-o',
              '--output-directory',
              default='.',
              help='Where to store the exported data.',
              type=click.Path(file_okay=False, resolve_path=True))
def main(commit: bool = False,
         debug: bool = False,
         deploy_key: str | None = None,
         output_directory: str = '.') -> None:
    """Export preferences."""
    setup_logging(debug)
    if (asyncio.run(_main(Path(output_directory), debug=debug, commit=commit,
                          deploy_key=deploy_key),
                    debug=debug) != 0):
        raise click.Abort()


async def _install_job(output_dir: Path, deploy_key: Path | None = None) -> int:
    p = await sp.create_subprocess_shell('bash -c "command -v prefs-export"', stdout=sp.PIPE)
    assert p.stdout is not None
    prefs_export_path = (await p.stdout.read()).decode().strip()
    home = Path.home()
    plist_path = home / 'Library/LaunchAgents/sh.tat.macprefs.plist'
    log_path = f'{home}/Library/Logs/macprefs.log'
    with plist_path.open('wb+') as f:
        plistlib.dump(dict(
            Label='sh.tat.macprefs',
            ProgramArguments=[
                prefs_export_path, '--output-directory',
                output_dir.resolve(strict=True), '--commit'
            ] + (['--deploy-key', deploy_key.resolve(strict=True)] if deploy_key else []),
            RunAtLoad=True,
            StandardErrorPath=log_path,
            StandardOutPath=log_path,
            StartCalendarInterval=dict(Hour=0, Minute=0)),
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


@click.command('macprefs-install-job')
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
def install_job(output_directory: str, debug: bool = False, deploy_key: str | None = None) -> None:
    """Job installer."""
    setup_logging(debug)
    if (asyncio.run(_install_job(Path(output_directory),
                                 Path(deploy_key) if deploy_key else None),
                    debug=debug) != 0):
        raise click.Abort()
