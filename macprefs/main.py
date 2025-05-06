from __future__ import annotations

from pathlib import Path
import asyncio
import logging

from anyio import Path as AnyioPath
from platformdirs import user_config_path, user_data_path
import click

from .config import read_config
from .utils import install_job as do_install_job, prefs_export, setup_logging

__all__ = ('main',)

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
              type=click.Path(dir_okay=False, exists=True, path_type=AnyioPath, resolve_path=True))
@click.option('-c', '--commit', help='Commit the changes with Git.', is_flag=True)
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
@click.option('-o',
              '--output-directory',
              default=user_data_path('macprefs'),
              help='Where to store the exported data.',
              type=click.Path(file_okay=False, path_type=AnyioPath, resolve_path=True))
def main(output_directory: AnyioPath,
         config_file: Path,
         deploy_key: AnyioPath | None = None,
         *,
         commit: bool = False,
         debug: bool = False) -> None:
    """Export preferences."""
    setup_logging(debug=debug)
    config = read_config(config_file)
    config_deploy_key = config.get('deploy-key')
    co = prefs_export(AnyioPath(output_directory),
                      config,
                      deploy_key or (AnyioPath(config_deploy_key) if config_deploy_key else None),
                      commit=commit or config.get('commit', False))
    asyncio.run(co, debug=debug)


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
              type=click.Path(dir_okay=False, exists=True, resolve_path=True, path_type=AnyioPath))
@click.option('-d', '--debug', help='Enable debug logging.', is_flag=True)
@click.option('-o',
              '--output-directory',
              default=str(user_data_path('macprefs')),
              help='Where to store the exported data.',
              type=click.Path(file_okay=False, resolve_path=True, path_type=Path))
def install_job(output_directory: AnyioPath,
                config_file: Path,
                deploy_key: AnyioPath | None = None,
                *,
                debug: bool = False) -> None:
    """Job installer."""
    setup_logging(debug=debug)
    config = read_config(config_file)
    config_deploy_key = config.get('deploy-key')
    if asyncio.run(do_install_job(
            output_directory, deploy_key
            or (AnyioPath(config_deploy_key) if config_deploy_key else None)),
                   debug=debug) != 0:
        raise click.Abort
