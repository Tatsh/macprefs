from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
import plistlib

from macprefs.exceptions import PropertyListConversionError
from macprefs.utils import (
    chdir,
    defaults_export,
    generate_domains,
    git,
    install_job,
    is_git_installed,
    prefs_export,
    setup_output_directory,
    try_parse_plist,
)
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_is_git_installed(mocker: MockerFixture) -> None:
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=AsyncMock)
    mock_process = AsyncMock()
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    result = await is_git_installed()
    assert result is True
    mock_subprocess.assert_called_once_with('bash', '-c', 'command -v git', stdout=mocker.ANY)


def test_generate_domains(mocker: MockerFixture) -> None:
    mock_glob = mocker.patch('macprefs.utils.Path.glob',
                             return_value=[
                                 Path('bad_.plist'),
                                 Path('test1.plist'),
                                 Path('test2.plist'),
                                 Path('.hidden.plist'),
                             ])
    mocker.patch('macprefs.utils.BAD_DOMAINS', {'test2'})
    mocker.patch('macprefs.utils.BAD_DOMAIN_PREFIXES', {'bad'})
    result = list(generate_domains(['additional_bad_domain']))
    assert result == ['test1', '-globalDomain']
    mock_glob.assert_called_once()


def test_try_parse_plist_valid(mocker: MockerFixture) -> None:
    mock_open = mocker.patch('macprefs.utils.Path.open',
                             mocker.mock_open(read_data=b'<plist></plist>'))
    mock_load = mocker.patch('macprefs.utils.plistlib.load', return_value={'key': 'value'})
    mock_remove_data_fields = mocker.patch('macprefs.utils.remove_data_fields',
                                           return_value={'key': 'value'})
    domain, result = try_parse_plist('test_domain', Path('test.plist'))
    assert domain == 'test_domain'
    assert result == {'key': 'value'}
    mock_open.assert_called_once()
    mock_load.assert_called_once()
    mock_remove_data_fields.assert_called_once()


def test_try_parse_plist_invalid(mocker: MockerFixture) -> None:
    mock_open = mocker.patch('pathlib.Path.open', mocker.mock_open(read_data=b'invalid'))
    mock_load = mocker.patch('plistlib.load', side_effect=ValueError)
    domain, result = try_parse_plist('test_domain', Path('test.plist'))
    assert domain == 'test_domain'
    assert result == {}
    mock_open.assert_called_once()
    mock_load.assert_called_once()


def test_chdir(mocker: MockerFixture) -> None:
    mock_chdir = mocker.patch('os.chdir')
    mocker.patch('pathlib.Path.cwd', return_value=Path('/original'))
    mocker.patch('pathlib.Path.resolve', return_value=Path('/new'))
    with chdir('/new'):
        mock_chdir.assert_called_with(Path('/new').resolve(strict=True))
    mock_chdir.assert_called_with(Path('/original'))


@pytest.mark.asyncio
async def test_git(mocker: MockerFixture) -> None:
    work_tree_path = mocker.MagicMock()
    truediv_mock = mocker.MagicMock()
    truediv_mock.__str__.return_value = '/work_tree/.git'
    truediv_mock.exists.return_value = False
    work_tree_path.resolve.return_value.__truediv__.return_value = truediv_mock
    work_tree_path.__str__.return_value = '/work_tree'
    mocker.patch('macprefs.utils.os.chdir')
    mocker.patch('macprefs.utils.Path')
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=AsyncMock)
    mock_process = AsyncMock()
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    result = await git(['status'], work_tree_path)
    assert result == mock_process
    mock_subprocess.assert_called_with('git',
                                       '--git-dir=/work_tree/.git',
                                       '--work-tree=/work_tree',
                                       'status',
                                       stderr=mocker.ANY)


def test_setup_output_directory(mocker: MockerFixture) -> None:
    mock_mkdir = mocker.patch('pathlib.Path.mkdir')

    out_dir, repo_prefs_dir = setup_output_directory(Path('/output'))

    assert out_dir == Path('/output')
    assert repo_prefs_dir == Path('/output/Preferences')
    mock_mkdir.assert_any_call(exist_ok=True, parents=True)


@pytest.mark.asyncio
async def test_defaults_export(mocker: MockerFixture) -> None:
    mock_copy = mocker.patch('shutil.copy')
    mock_try_parse = mocker.patch('macprefs.utils.try_parse_plist',
                                  return_value=('domain', {
                                      'key': 'value'
                                  }))
    result = await defaults_export('domain', Path('/repo_prefs_dir'))
    assert result == ('domain', {'key': 'value'})
    mock_copy.assert_called_once()
    mock_try_parse.assert_called_once()


@pytest.mark.asyncio
async def test_install_job(mocker: MockerFixture) -> None:
    mock_plistlib_dump = mocker.patch('macprefs.utils.plistlib.dump')
    mock_plist_path = mocker.MagicMock()
    mock_plist_path.__str__.return_value = '/a/path/to/com.sh.tat.macprefs.plist'
    mock_user_log_path = mocker.patch('macprefs.utils.user_log_path')
    mock_user_log_path.return_value.__truediv__.return_value.__str__.return_value = '/a/log-path/macprefs.log'  # noqa: E501
    mock_path_home = mocker.patch('macprefs.utils.Path.home')
    mock_path_home.return_value.__truediv__.return_value = mock_plist_path
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=AsyncMock)
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.stdout.read.return_value = b'output'
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    mock_path = mocker.MagicMock(name='/output_dir')
    mock_path.resolve.return_value.__str__.return_value = '/output_dir'
    result = await install_job(mock_path)
    mock_plistlib_dump.assert_called_once_with(
        {
            'Label': 'sh.tat.macprefs',
            'ProgramArguments': ['output', '--output-directory', '/output_dir', '--commit'],
            'RunAtLoad': True,
            'StandardErrorPath': '/a/log-path/macprefs.log',
            'StandardOutPath': '/a/log-path/macprefs.log',
            'StartCalendarInterval': {
                'Hour': 0,
                'Minute': 0
            }
        },
        mock_plist_path.open.return_value.__enter__.return_value,
        fmt=plistlib.PlistFormat.FMT_XML)
    assert result == 0
    assert mock_subprocess.call_count == 5
    assert mock_subprocess.await_count == 5
    mock_subprocess.assert_has_awaits([
        mocker.call('bash', '-c', 'command -v prefs-export', stdout=-1),
        mocker.call('launchctl',
                    'stop',
                    '/a/path/to/com.sh.tat.macprefs.plist',
                    stderr=-1,
                    stdout=-1),
        mocker.call('launchctl',
                    'unload',
                    '-w',
                    '/a/path/to/com.sh.tat.macprefs.plist',
                    stderr=-1,
                    stdout=-1),
        mocker.call('launchctl', 'load', '-w', '/a/path/to/com.sh.tat.macprefs.plist'),
        mocker.call('launchctl', 'start', '/a/path/to/com.sh.tat.macprefs.plist')
    ])


@pytest.mark.asyncio
async def test_prefs_export_error(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.utils.sp.create_subprocess_exec', new_callable=AsyncMock)
    mocker.patch('macprefs.utils.Path')
    mock_is_git_installed = mocker.patch('macprefs.utils.is_git_installed', return_value=True)
    mock_setup_output_directory = mocker.patch(
        'macprefs.utils.setup_output_directory',
        return_value=(Path('/out_dir'), Path('/repo_prefs_dir')))
    mock_generate_domains = mocker.patch('macprefs.utils.generate_domains',
                                         return_value=['domain1', 'domain2'])
    mock_defaults_export = mocker.patch('macprefs.utils.defaults_export',
                                        new_callable=AsyncMock,
                                        side_effect=[('domain1', {
                                            'key': 'value'
                                        }), ('domain2', {
                                            'key': 'value'
                                        })])
    mocker.patch('macprefs.utils.git', new_callable=AsyncMock)
    mock_out_dir = mocker.MagicMock()
    with pytest.raises(PropertyListConversionError):
        await prefs_export(mock_out_dir, commit=True)
    mock_is_git_installed.assert_called_once()
    mock_setup_output_directory.assert_called_once()
    mock_generate_domains.assert_called_once()
    mock_defaults_export.assert_called()
