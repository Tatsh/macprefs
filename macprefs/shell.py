from os import chdir
from pathlib import Path
from shlex import quote
from typing import Iterable
import asyncio
import asyncio.subprocess as sp
import logging

__all__ = ('git',)

log = logging.getLogger(__name__)


async def git(cmd: Iterable[str],
              check: bool | None = False,
              debug: bool = False,
              git_dir: Path | None = None,
              work_tree: Path | None = None,
              ssh_key: str | None = None) -> sp.Process:
    """Run a Git command."""
    work_tree = work_tree or Path('.')
    rest = ' '.join(map(quote, cmd))
    if not git_dir:
        git_dir = Path(work_tree).resolve(strict=True) / '.git'
        if not git_dir.exists():
            work_tree.mkdir(parents=True, exist_ok=True)
            cwd = Path.cwd()
            chdir(work_tree)
            log.debug('Running: git init')
            p = await asyncio.create_subprocess_shell('git init', stdout=sp.PIPE, stderr=sp.PIPE)
            await p.wait()
            chdir(cwd)
    if ssh_key:
        await git(('config', 'core.sshCommand',
                   (f'ssh -i {ssh_key} -F /dev/null -o UserKnownHostsFile=/dev/null '
                    '-o StrictHostKeyChecking=no')))
    full_command = (f'git "--git-dir={git_dir}" '
                    f'"--work-tree={work_tree}" {rest}')
    log.debug('Running: %s', full_command)
    p = await asyncio.create_subprocess_shell(full_command, stdout=sp.PIPE, stderr=sp.PIPE)
    await p.wait()
    if check and p.returncode != 0:
        assert p.stderr is not None
        stderr = (await p.stderr.read()).decode('utf-8')
        raise RuntimeError(f'Non-zero return code: {p.returncode}, STDERR: {stderr}')
    return p
