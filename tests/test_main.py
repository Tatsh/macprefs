from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from click.testing import CliRunner
from macprefs.main import install_job, main
from platformdirs import user_data_path
import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture


@pytest.fixture
def mock_do_install_job(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('macprefs.main.do_install_job', return_value=0)


@pytest.fixture
def mock_setup_logging(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('macprefs.main.setup_logging')


@pytest.fixture
def mock_config(mocker: MockerFixture) -> MagicMock:
    return mocker.patch('macprefs.main.read_config', return_value={})


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_main_success(runner: CliRunner, mock_setup_logging: MagicMock, mock_config: MagicMock,
                      mocker: MockerFixture) -> None:
    mock_prefs_export = mocker.patch('macprefs.main.prefs_export', return_value=0)
    result = runner.invoke(main, ['--debug', '--commit'])
    assert result.exit_code == 0
    mock_config.assert_called_once()
    mock_setup_logging.assert_called_once_with(debug=True, loggers=mocker.ANY)
    mock_prefs_export.assert_called_once()


def test_main_with_config(runner: CliRunner, mocker: MockerFixture,
                          mock_setup_logging: MagicMock) -> None:
    mock_prefs_export = mocker.patch('macprefs.main.prefs_export', return_value=0)
    config_path = '/path/to/config.toml'
    result = runner.invoke(main, ['--config', config_path])
    assert result.exit_code == 0
    mock_prefs_export.assert_called_once_with(mocker.ANY, mocker.ANY, None, commit=False)
    mock_setup_logging.assert_called_once_with(debug=False, loggers=mocker.ANY)


def test_install_job_success(runner: CliRunner, mock_do_install_job: MagicMock,
                             mock_setup_logging: MagicMock, mocker: MockerFixture) -> None:
    result = runner.invoke(install_job, ['--debug'])
    assert result.exit_code == 0
    mock_setup_logging.assert_called_once_with(debug=True, loggers=mocker.ANY)
    mock_do_install_job.assert_called_once()


def test_install_job_failure(runner: CliRunner, mock_setup_logging: MagicMock,
                             mocker: MockerFixture, mock_config: MagicMock) -> None:
    mock_do_install_job = mocker.patch('macprefs.main.do_install_job', return_value=1)
    result = runner.invoke(install_job, ['--debug'])
    assert result.exit_code != 0
    mock_config.assert_called_once()
    mock_setup_logging.assert_called_once_with(debug=True, loggers=mocker.ANY)
    mock_do_install_job.assert_called_once()


def test_install_job_with_deploy_key(runner: CliRunner, mock_do_install_job: MagicMock,
                                     mock_setup_logging: MagicMock, mock_config: MagicMock,
                                     mocker: MagicMock) -> None:
    deploy_key_path = '/dev/null'
    result = runner.invoke(install_job, ['--deploy-key', deploy_key_path])
    assert result.exit_code == 0
    mock_config.assert_called_once()
    prefs_dir = user_data_path('macprefs')
    mock_do_install_job.assert_called_once_with(prefs_dir, Path(deploy_key_path))
    mock_setup_logging.assert_called_once_with(debug=False, loggers=mocker.ANY)
