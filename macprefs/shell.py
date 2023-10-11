from os import chdir
from pathlib import Path
from shlex import quote
from subprocess import CalledProcessError
from typing import Iterable
import asyncio
import asyncio.subprocess as sp
import logging

__all__ = ('git',)

log = logging.getLogger(__name__)


async def git(cmd: Iterable[str],
              work_tree: Path,
              git_dir: Path | None = None,
              ssh_key: str | None = None) -> sp.Process:
    """Run a Git command."""
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
                    '-o StrictHostKeyChecking=no')), work_tree)
    cmd_list = list(cmd)
    rest = ' '.join(map(quote, cmd_list))
    log.debug('Running: git "--git-dir=%s" "--work-tree=%s" %s', git_dir, work_tree, rest)
    p = await asyncio.create_subprocess_exec('git',
                                             f'--git-dir={git_dir}',
                                             f'--work-tree={work_tree}',
                                             *cmd_list,
                                             stderr=sp.PIPE)
    if (await p.wait()) != 0:
        assert p.returncode is not None
        assert p.stderr is not None
        stderr = (await p.stderr.read()).decode()
        raise CalledProcessError(p.returncode, cmd_list, stderr=stderr)
    return p
