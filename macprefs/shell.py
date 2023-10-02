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
              git_dir: Path | None = None,
              work_tree: Path | None = None,
              ssh_key: str | None = None) -> sp.Process:
    """Run a Git command."""
    work_tree = work_tree or Path('.')
    if not git_dir:
        git_dir = Path(work_tree).resolve(strict=True) / '.git'
        if not git_dir.exists():
            work_tree.mkdir(parents=True, exist_ok=True)
            cwd = Path.cwd()
            chdir(work_tree)
            log.debug('Running: git init')
            p = await asyncio.create_subprocess_exec('git', 'init', stdout=sp.PIPE, stderr=sp.PIPE)
            await p.wait()
            chdir(cwd)
    if ssh_key:
        await git(('config', 'core.sshCommand',
                   (f'ssh -i {ssh_key} -F /dev/null -o UserKnownHostsFile=/dev/null '
                    '-o StrictHostKeyChecking=no')))
    cmd_list = list(cmd)
    rest = ' '.join(map(quote, cmd_list))
    log.debug(f'Running: git "--git-dir={git_dir}" "--work-tree={work_tree}" {rest}')
    p = await asyncio.create_subprocess_exec('git',
                                             f'--git-dir={git_dir}',
                                             f'--work-tree={work_tree}',
                                             *cmd_list,
                                             stderr=sp.PIPE)
    if (await p.wait()) != 0:
        assert p.stderr is not None
        stderr = (await p.stderr.read()).decode()
        raise RuntimeError(f'Non-zero return code: {p.returncode}, STDERR: {stderr}')
    return p
