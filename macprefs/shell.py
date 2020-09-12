from itertools import chain
from os import chdir, getcwd, makedirs
from os.path import isfile, realpath
from pathlib import Path
from shlex import quote
from typing import Iterable, Optional
import asyncio
import asyncio.subprocess as sp

from .utils import setup_logging_stderr

__all__ = (
    'delete_old_plists',
    'git',
)


async def git(cmd: Iterable[str],
              check: Optional[bool] = False,
              work_tree: str = '.',
              git_dir: Optional[Path] = None) -> sp.Process:
    """Run a Git command."""
    log = setup_logging_stderr(verbose=True)
    rest = ' '.join(map(quote, cmd))
    if not git_dir:
        git_dir = Path(realpath(work_tree)).joinpath('.git')
        if not git_dir.exists():
            try:
                makedirs(work_tree)
            except FileExistsError:
                pass
            cwd = getcwd()
            chdir(work_tree)
            log.debug('Running: git init')
            p = await asyncio.create_subprocess_shell('git init',
                                                      stdout=sp.PIPE,
                                                      stderr=sp.PIPE)
            await p.wait()
            chdir(cwd)
    full_command = (f'git "--git-dir={git_dir}" '
                    f'"--work-tree={work_tree}" {rest}')
    log.debug('Running: %s', full_command)
    p = await asyncio.create_subprocess_shell(full_command,
                                              stdout=sp.PIPE,
                                              stderr=sp.PIPE)
    await p.wait()
    if check and p.returncode != 0:
        assert p.stderr is not None
        stderr = (await p.stderr.read()).decode('utf-8')
        raise RuntimeError(
            f'Non-zero return code: {p.returncode}, STDERR: {stderr}')
    return p


async def delete_old_plists(domains: Iterable[str],
                            repo_prefs_dir: Path,
                            work_tree: str = '.',
                            git_dir: Optional[Path] = None) -> None:
    """Use Git to remove no-longer-existant preferences."""
    await git(chain(('rm', '-f'),
                    (x for x in (str(repo_prefs_dir.joinpath(f'{y}.plist'))
                                 for y in domains) if isfile(x))),
              work_tree=work_tree,
              git_dir=git_dir)
