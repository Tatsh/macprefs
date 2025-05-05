from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import asyncio
import logging

from platformdirs import user_config_path
import click

from .config import read_config
from .utils import install_job as do_install_job, prefs_export, setup_logging

__all__ = ('main',)

EXECUTOR = ProcessPoolExecutor()
log = logging.getLogger(__name__)


@click.command('prefs-export', context_settings={'help_option_names': ['-h', '--help']})
@click.option('-C',
              '--config',
              'config_file',
              help='Path to the configuration file.',
              type=click.Path(dir_okay=False, path_type=Path),
              default=user_config_path('macprefs') / 'config.toml')
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
         config_file: Path,
         deploy_key: Path | None = None,
         *,
         commit: bool = False,
         debug: bool = False) -> None:
    """Export preferences."""
    setup_logging(debug=debug)
    config = read_config(config_file)
    co = prefs_export(output_directory,
                      config,
                      deploy_key or config.get('deploy-key'),
                      commit=commit or config.get('commit', False))
    if asyncio.run(co, debug=debug) != 0:
        raise click.Abort


@click.command('macprefs-install-job', context_settings={'help_option_names': ['-h', '--help']})
@click.option('-C',
              '--config',
              'config_file',
              help='Path to the configuration file.',
              type=click.Path(dir_okay=False, path_type=Path),
              default=user_config_path('macprefs') / 'config.toml')
@click.option('-K',
              '--deploy-key',
              help='Key for pushing to Git repository.',
              type=click.Path(dir_okay=False, exists=True, resolve_path=True, path_type=Path))
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
@click.option('-o',
              '--output-directory',
              default=str(Path.home() / '.local/share/prefs-export'),
              help='Where to store the exported data.',
              type=click.Path(file_okay=False, resolve_path=True, path_type=Path))
def install_job(output_directory: Path,
                config_file: Path,
                deploy_key: Path | None = None,
                *,
                debug: bool = False) -> None:
    """Job installer."""
    setup_logging(debug=debug)
    config = read_config(config_file)
    if asyncio.run(do_install_job(output_directory, deploy_key or config.get('deploy-key')),
                   debug=debug) != 0:
        raise click.Abort
