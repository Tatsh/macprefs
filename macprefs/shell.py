from os.path import isfile
from pathlib import Path
from shlex import quote
from typing import Optional, Sequence
import asyncio
import asyncio.subprocess as sp

from .utils import setup_logging_stderr

__all__ = (
    'delete_old_plists',
    'git',
)


async def git(cmd: Sequence[str], check: Optional[bool] = False) -> sp.Process:
    """Run a Git command."""
    rest = ' '.join(map(quote, cmd))
    full_command = f'git {rest}'
    log = setup_logging_stderr(verbose=True)
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


async def delete_old_plists(domains: Sequence[str],
                            repo_prefs_dir: Path) -> None:
    """Use Git to remove no-longer-existant preferences."""
    await git(('rm', '-f') +
              tuple(x for x in (str(repo_prefs_dir.joinpath(f'{y}.plist'))
                                for y in domains) if isfile(x)))
