from __future__ import annotations

from typing import TYPE_CHECKING
import plistlib
import subprocess as sp
import sys

from anyio import Path as AnyioPath
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
                                   new_callable=mocker.AsyncMock)
    mock_process = mocker.AsyncMock()
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    result = await is_git_installed()
    assert result is True
    mock_subprocess.assert_called_once_with('bash', '-c', 'command -v git', stdout=mocker.ANY)


@pytest.mark.asyncio
async def test_generate_domains(mocker: MockerFixture) -> None:
    mock_glob = mocker.AsyncMock()
    mock_glob.__aiter__.return_value = [
        AnyioPath('bad_.plist'),
        AnyioPath('test1.plist'),
        AnyioPath('test2.plist'),
        AnyioPath('.hidden.plist')
    ]
    mocker.patch('macprefs.utils.Path.glob', return_value=mock_glob)
    mocker.patch('macprefs.utils.BAD_DOMAINS', {'test2'})
    mocker.patch('macprefs.utils.BAD_DOMAIN_PREFIXES', {'bad'})
    result = [x async for x in generate_domains(['additional_bad_domain'], [])]
    assert result == ['test1', '-globalDomain']
    mock_glob.__aiter__.assert_called_once()


@pytest.mark.asyncio
async def test_try_parse_plist_valid(mocker: MockerFixture) -> None:
    mock_open = mocker.patch('macprefs.utils.Path.open')
    mock_load = mocker.patch('macprefs.utils.plistlib.load', return_value={'key': 'value'})
    mock_remove_data_fields = mocker.patch('macprefs.utils.remove_data_fields',
                                           return_value={'key': 'value'})
    domain, result = await try_parse_plist('test_domain', AnyioPath('test.plist'))
    assert domain == 'test_domain'
    assert result == {'key': 'value'}
    mock_open.assert_called_once()
    mock_load.assert_called_once()
    mock_remove_data_fields.assert_called_once()


@pytest.mark.asyncio
async def test_try_parse_plist_invalid(mocker: MockerFixture) -> None:
    mock_open = mocker.patch('pathlib.Path.open')
    mock_load = mocker.patch('plistlib.load', side_effect=ValueError)
    domain, result = await try_parse_plist('test_domain', AnyioPath('test.plist'))
    assert domain == 'test_domain'
    assert result == {}
    mock_open.assert_called_once()
    mock_load.assert_called_once()


@pytest.mark.asyncio
async def test_chdir(mocker: MockerFixture) -> None:
    mock_chdir = mocker.patch('os.chdir')
    mocker.patch('anyio.Path.cwd', return_value=AnyioPath('/original'))
    mocker.patch('anyio.Path.resolve', return_value=AnyioPath('/new'))
    new_path = AnyioPath('/new')
    async with chdir('/new'):
        mock_chdir.assert_called_with(await new_path.resolve(strict=True))
    mock_chdir.assert_called_with(AnyioPath('/original'))


@pytest.mark.asyncio
async def test_git(mocker: MockerFixture) -> None:
    work_tree_path = mocker.AsyncMock(spec=AnyioPath)
    truediv_mock = mocker.AsyncMock()
    truediv_mock.__str__.return_value = '/work_tree/.git'
    truediv_mock.exists.return_value = mocker.AsyncMock(return_value=False)
    work_tree_path.resolve.return_value.__truediv__.return_value = truediv_mock
    work_tree_path.__str__.return_value = '/work_tree'
    mocker.patch('macprefs.utils.os.chdir')
    mock_path = mocker.patch('macprefs.utils.Path')
    mock_resolved = mocker.AsyncMock()
    mock_path.return_value.resolve.return_value = mock_resolved
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=mocker.AsyncMock)
    mock_process = mocker.AsyncMock()
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    result = await git(['status'], work_tree_path)
    assert result == mock_process
    mock_subprocess.assert_called_with('git',
                                       '--git-dir=/work_tree/.git',
                                       '--work-tree=/work_tree',
                                       'status',
                                       stderr=mocker.ANY)


@pytest.mark.asyncio
async def test_git_with_git_dir_and_ssh_key(mocker: MockerFixture) -> None:
    work_tree = mocker.AsyncMock()
    work_tree.__str__.return_value = '/work_tree'
    git_dir = mocker.AsyncMock()
    git_dir.__str__.return_value = '/work_tree/.git'
    git_dir.resolve.return_value.__truediv__.return_value.__str__.return_value = '/work_tree/.git'
    mocker.patch('macprefs.utils.os.chdir')
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=mocker.AsyncMock)
    mock_process = mocker.AsyncMock()
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    result = await git(['status'], work_tree, git_dir, '/path/to/ssh_key')
    assert result == mock_process
    mock_subprocess.assert_any_call(
        'git',
        '--git-dir=/work_tree/.git',
        '--work-tree=/work_tree',
        'config',
        'core.sshCommand',
        'ssh -i /path/to/ssh_key -F /dev/null -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no',  # noqa: E501
        stderr=mocker.ANY)
    mock_subprocess.assert_any_call('git',
                                    '--git-dir=/work_tree/.git',
                                    '--work-tree=/work_tree',
                                    'status',
                                    stderr=mocker.ANY)
    assert mock_subprocess.call_count == 2


@pytest.mark.asyncio
async def test_git_no_git_dir(mocker: MockerFixture) -> None:
    work_tree = mocker.AsyncMock(spec=AnyioPath)
    work_tree.__str__.return_value = '/work_tree'
    truediv_mock = mocker.AsyncMock()
    truediv_mock.__str__.return_value = '/work_tree/.git'
    truediv_mock.exists = mocker.AsyncMock(return_value=False)
    work_tree.resolve.return_value.__truediv__.return_value = truediv_mock
    mock_chdir = mocker.MagicMock()
    mock_chdir.__aenter__.return_value = None
    mock_chdir.__aexit__.return_value = None
    mocker.patch('macprefs.utils.chdir', mock_chdir)
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=mocker.AsyncMock)
    mock_process = mocker.AsyncMock()
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    result = await git(['status'], work_tree)
    assert result == mock_process
    mock_subprocess.assert_any_call('git', 'init', stdout=mocker.ANY, stderr=mocker.ANY)


@pytest.mark.asyncio
async def test_git_error(mocker: MockerFixture) -> None:
    work_tree = mocker.AsyncMock(spec=AnyioPath)
    work_tree.__str__.return_value = '/work_tree'
    git_dir = mocker.AsyncMock(spec=AnyioPath)
    git_dir.__str__.return_value = '/work_tree/.git'
    git_dir.resolve.return_value.__truediv__.return_value.__str__.return_value = '/work_tree/.git'
    mocker.patch('macprefs.utils.os.chdir')
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=mocker.AsyncMock)
    mock_process = mocker.AsyncMock()
    mock_process.wait.return_value = 1
    mock_subprocess.return_value = mock_process
    with pytest.raises(sp.CalledProcessError):
        await git(['status'], work_tree, git_dir, '/path/to/ssh_key')


@pytest.mark.asyncio
async def test_setup_output_directory(mocker: MockerFixture) -> None:
    mock_repo_prefs_dir = mocker.AsyncMock()
    output_dir_path = mocker.AsyncMock()
    output_dir_path.__truediv__.return_value = mock_repo_prefs_dir
    out_dir, repo_prefs_dir = await setup_output_directory(output_dir_path)
    assert out_dir == output_dir_path
    assert repo_prefs_dir == mock_repo_prefs_dir
    output_dir_path.mkdir.assert_any_call(exist_ok=True, parents=True)


@pytest.mark.asyncio
async def test_defaults_export(mocker: MockerFixture) -> None:
    mock_copy = mocker.patch('shutil.copy')
    mock_try_parse = mocker.patch('macprefs.utils.try_parse_plist',
                                  return_value=('domain', {
                                      'key': 'value'
                                  }))
    mock_plist_in = mocker.AsyncMock()
    mock_utils_home = mocker.patch('macprefs.utils.Path.home', new_callable=mocker.AsyncMock)
    mock_utils_home.return_value.__truediv__.return_value.__truediv__.return_value = mock_plist_in
    if sys.version_info >= (3, 14):
        mock_plist_in.copy = mocker.AsyncMock()
    else:
        # Cannot set/mock __getattr__() so make copy() raise the attribute error.
        mock_plist_in.copy = mocker.AsyncMock(side_effect=AttributeError('copy'))
    mock_path = mocker.AsyncMock(spec=AnyioPath)
    mock_plist_out = mocker.AsyncMock()
    mock_path.__truediv__.return_value = mock_plist_out
    result = await defaults_export('domain', mock_path)
    assert result == ('domain', {'key': 'value'})
    if sys.version_info >= (3, 14):
        mock_plist_in.copy.assert_awaited_once_with(mock_plist_out)
    else:
        mock_copy.assert_called_once()
    mock_try_parse.assert_called_once()


@pytest.mark.asyncio
async def test_defaults_export_permission_error(mocker: MockerFixture) -> None:
    mock_copy = mocker.patch('shutil.copy', side_effect=PermissionError)
    mock_try_parse = mocker.patch('macprefs.utils.try_parse_plist',
                                  return_value=('domain', {
                                      'key': 'value'
                                  }))
    mock_plist_in = mocker.AsyncMock()
    mock_utils_home = mocker.patch('macprefs.utils.Path.home', new_callable=mocker.AsyncMock)
    mock_utils_home.return_value.__truediv__.return_value.__truediv__.return_value = mock_plist_in
    if sys.version_info >= (3, 14):
        mock_plist_in.copy = mocker.AsyncMock(side_effect=PermissionError)
    else:
        # Cannot set/mock __getattr__() so make copy() raise the attribute error.
        mock_plist_in.copy = mocker.AsyncMock(side_effect=AttributeError('copy'))
    mock_path = mocker.AsyncMock(spec=AnyioPath)
    mock_plist_out = mocker.AsyncMock()
    mock_path.__truediv__.return_value = mock_plist_out
    result = await defaults_export('domain', mock_path)
    assert result == ('domain', {})
    if sys.version_info >= (3, 14):
        mock_plist_in.copy.assert_awaited_once_with(mock_plist_out)
    else:
        mock_copy.assert_called_once()
    assert mock_try_parse.call_count == 0


@pytest.mark.asyncio
async def test_install_job(mocker: MockerFixture) -> None:
    mock_plistlib_dump = mocker.patch('macprefs.utils.plistlib.dump')
    mock_plist_path = mocker.AsyncMock()
    mock_plist_path.__str__.return_value = '/a/path/to/com.sh.tat.macprefs.plist'
    mock_user_log_path = mocker.patch('macprefs.utils.user_log_path')
    mock_user_log_path.return_value.__truediv__.return_value.__str__.return_value = '/a/log-path/macprefs.log'  # noqa: E501
    mock_path_home = mocker.patch('macprefs.utils.Path.home')
    mock_path_home.return_value.__truediv__.return_value = mock_plist_path
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=mocker.AsyncMock)
    mock_process = mocker.AsyncMock()
    mock_process.returncode = 0
    mock_process.stdout.read.return_value = b'output'
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    mock_path = mocker.MagicMock(name='/output_dir')
    mock_path.resolve.return_value.__str__.return_value = '/output_dir'
    result = await install_job(mock_path)
    mock_plistlib_dump.assert_called_once_with(
        {
            'EnvironmentVariables': {
                'NO_COLOR': '1',
            },
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
        mock_plist_path.open.return_value.__aenter__.return_value.wrapped,
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
    mocker.patch('macprefs.utils.MAX_CONCURRENT_EXPORT_TASKS', 2)
    mocker.patch('macprefs.utils.sp.create_subprocess_exec', new_callable=mocker.AsyncMock)
    mocker.patch('macprefs.utils.Path')
    mock_is_git_installed = mocker.patch('macprefs.utils.is_git_installed', return_value=True)
    mock_out_dir = mocker.AsyncMock()
    mock_repo_prefs_dir = mocker.AsyncMock()
    mock_setup_output_directory = mocker.patch('macprefs.utils.setup_output_directory',
                                               return_value=(mock_out_dir, mock_repo_prefs_dir))
    mock_generate_domains = mocker.AsyncMock()
    mock_generate_domains.__aiter__.return_value = ['domain1', 'domain2', 'domain3']
    mocker.patch('macprefs.utils.generate_domains', return_value=mock_generate_domains)
    mock_defaults_export = mocker.patch('macprefs.utils.defaults_export',
                                        new_callable=mocker.AsyncMock,
                                        side_effect=[('domain1', {
                                            'key': 'value'
                                        }), ('domain2', {
                                            'key': 'value'
                                        }), ('domain3', {})])
    mocker.patch('macprefs.utils.git', new_callable=mocker.AsyncMock)
    mock_out_dir.__truediv__.return_value = mocker.AsyncMock()
    mock_out_dir.__truediv__.return_value.__aenter__.return_value.open.return_value = mocker.AsyncMock(  # noqa: E501
    )
    mock_repo_prefs_dir.__truediv__.return_value.name = 'out.plist'
    with pytest.raises(PropertyListConversionError):
        await prefs_export(mock_out_dir, commit=True)
    mock_is_git_installed.assert_called_once()
    mock_setup_output_directory.assert_called_once()
    mock_generate_domains.__aiter__.assert_called_once()
    mock_defaults_export.assert_called()


@pytest.mark.asyncio
async def test_prefs_export(mocker: MockerFixture) -> None:
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=mocker.AsyncMock)
    mock_process = mocker.AsyncMock()
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    mocker.patch('macprefs.utils.Path')
    mock_out_dir = mocker.AsyncMock()
    mock_repo_prefs_dir = mocker.AsyncMock()
    mock_setup_output_directory = mocker.patch('macprefs.utils.setup_output_directory',
                                               return_value=(mock_out_dir, mock_repo_prefs_dir))
    mock_generate_domains = mocker.AsyncMock()
    mock_generate_domains.__aiter__.return_value = ['domain1', 'domain2', 'domain3', 'rejected1']
    mocker.patch('macprefs.utils.generate_domains', return_value=mock_generate_domains)
    mock_defaults_export = mocker.patch('macprefs.utils.defaults_export',
                                        new_callable=mocker.AsyncMock,
                                        side_effect=[
                                            ('domain1', {
                                                'key': 'value'
                                            }),
                                            ('domain2', {
                                                'key': 'value'
                                            }),
                                            ('domain3', {}),
                                            ('rejected1', {
                                                'key': 'value'
                                            }),
                                        ])
    mocker.patch('macprefs.utils.git', new_callable=mocker.AsyncMock)
    mock_is_git_installed = mocker.patch('macprefs.utils.is_git_installed', return_value=False)
    mock_exec_defaults_io = mocker.AsyncMock()
    mock_out_dir.__truediv__.return_value = mocker.AsyncMock()
    mock_out_dir.__truediv__.return_value.open.return_value.__aenter__.return_value = mock_exec_defaults_io  # noqa: E501
    mock_repo_prefs_dir.__truediv__.return_value.name = 'out.plist'
    mocker.patch('macprefs.utils.make_key_filter', return_value=lambda d, _: d == 'rejected1')
    await prefs_export(mock_out_dir, commit=True)
    mock_exec_defaults_io.write.assert_has_calls([
        mocker.call('#!/usr/bin/env bash\n'),
        mocker.call('# shellcheck disable=SC1003,SC1010,SC1112,SC2016,SC2088\n'),
        mocker.call('# This file is generated, but is versioned.\n\n'),
        mocker.call('# domain1\n'),
        mocker.call('defaults write domain1 key -string value\n'),
        mocker.call('\n'),
        mocker.call('# domain2\n'),
        mocker.call('defaults write domain2 key -string value\n'),
        mocker.call('\n'),
        mocker.call('# Rejected defaults values.\n'),
        mocker.call('# shellcheck disable=SC1003,SC1010,SC1112,SC2016,SC2088\n'),
        mocker.call('# This file is generated, but is versioned.\n\n'),
        mocker.call('# rejected1\n'),
        mocker.call('defaults write rejected1 key -string value\n'),
        mocker.call('\n'),
    ])
    mock_is_git_installed.assert_called_once()
    mock_setup_output_directory.assert_called_once()
    mock_generate_domains.__aiter__.assert_called_once()
    mock_defaults_export.assert_called()


@pytest.mark.asyncio
async def test_prefs_export_git_error(mocker: MockerFixture) -> None:
    mock_logger = mocker.patch('macprefs.utils.log.info')
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=mocker.AsyncMock)
    mock_process = mocker.AsyncMock()
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    mocker.patch('macprefs.utils.Path')
    mock_out_dir = mocker.AsyncMock(spec=AnyioPath)
    mock_repo_prefs_dir = mocker.AsyncMock(spec=AnyioPath)
    mock_setup_output_directory = mocker.patch('macprefs.utils.setup_output_directory',
                                               return_value=(mock_out_dir, mock_repo_prefs_dir))
    mock_generate_domains = mocker.AsyncMock()
    mock_generate_domains.__aiter__.return_value = ['domain1', 'domain2', 'domain3', 'rejected1']
    mocker.patch('macprefs.utils.generate_domains', return_value=mock_generate_domains)
    mock_defaults_export = mocker.patch('macprefs.utils.defaults_export',
                                        new_callable=mocker.AsyncMock,
                                        side_effect=[
                                            ('domain1', {
                                                'key': 'value'
                                            }),
                                            ('domain2', {
                                                'key': 'value'
                                            }),
                                            ('domain3', {}),
                                            ('rejected1', {
                                                'key': 'value'
                                            }),
                                        ])
    mock_git = mocker.patch('macprefs.utils.git', new_callable=mocker.AsyncMock)
    mock_git_branch_process = mocker.AsyncMock()
    mock_git_branch_process.stdout.read = mocker.AsyncMock(return_value=b'branch')
    mock_git.side_effect = [
        mock_process, mock_process, mock_process, mock_git_branch_process,
        sp.CalledProcessError(1, 'git')
    ]
    mock_is_git_installed = mocker.patch('macprefs.utils.is_git_installed', return_value=True)
    mock_out_dir.__truediv__.return_value = mocker.AsyncMock()
    mock_out_dir.__truediv__.return_value.open = mocker.AsyncMock()
    mock_repo_prefs_dir.__truediv__.return_value.name = 'out.plist'
    mocker.patch('macprefs.utils.make_key_filter', return_value=lambda d, _: d == 'rejected1')
    test1_plist = mocker.AsyncMock(spec=AnyioPath)
    test1_plist.name = 'test1.plist'
    test1_plist.exists.return_value = True
    test1_plist.is_dir.return_value = False
    iterdir_iterator = mocker.AsyncMock()
    mock_repo_prefs_dir.iterdir.return_value = iterdir_iterator
    iterdir_iterator.__aiter__.return_value = [test1_plist]
    mock_deploy_key = mocker.AsyncMock(spec=AnyioPath)
    await prefs_export(mock_out_dir, deploy_key=mock_deploy_key, commit=True)
    mock_is_git_installed.assert_called_once()
    mock_setup_output_directory.assert_called_once()
    mock_generate_domains.__aiter__.assert_called_once()
    mock_defaults_export.assert_called()
    assert mock_git.call_count == 5
    mock_logger.assert_called_once_with('Likely no changes to commit.')


@pytest.mark.asyncio
async def test_prefs_export_git_no_deploy_key(mocker: MockerFixture) -> None:
    mock_subprocess = mocker.patch('macprefs.utils.sp.create_subprocess_exec',
                                   new_callable=mocker.AsyncMock)
    mock_process = mocker.AsyncMock()
    mock_process.wait.return_value = 0
    mock_subprocess.return_value = mock_process
    mocker.patch('macprefs.utils.Path')
    mock_out_dir = mocker.AsyncMock(spec=AnyioPath)
    mock_repo_prefs_dir = mocker.AsyncMock(spec=AnyioPath)
    mock_setup_output_directory = mocker.patch('macprefs.utils.setup_output_directory',
                                               return_value=(mock_out_dir, mock_repo_prefs_dir))
    mock_generate_domains = mocker.AsyncMock()
    mock_generate_domains.__aiter__.return_value = ['domain1', 'domain2', 'domain3', 'rejected1']
    mocker.patch('macprefs.utils.generate_domains', return_value=mock_generate_domains)
    mock_defaults_export = mocker.patch('macprefs.utils.defaults_export',
                                        new_callable=mocker.AsyncMock,
                                        side_effect=[
                                            ('domain1', {
                                                'key': 'value'
                                            }),
                                            ('domain2', {
                                                'key': 'value'
                                            }),
                                            ('domain3', {}),
                                            ('rejected1', {
                                                'key': 'value'
                                            }),
                                        ])
    mock_git = mocker.patch('macprefs.utils.git', new_callable=mocker.AsyncMock)
    mock_git.return_value = mock_process
    mock_is_git_installed = mocker.patch('macprefs.utils.is_git_installed', return_value=True)
    mock_out_dir.__truediv__.return_value = mocker.AsyncMock()
    mock_out_dir.__truediv__.return_value.open = mocker.AsyncMock()
    mock_repo_prefs_dir.__truediv__.return_value.name = 'out.plist'
    mocker.patch('macprefs.utils.make_key_filter', return_value=lambda d, _: d == 'rejected1')
    test1_plist = mocker.AsyncMock(spec=AnyioPath)
    test1_plist.name = 'test1.plist'
    test1_plist.exists.return_value = True
    test1_plist.is_dir.return_value = False
    iterdir_iterator = mocker.AsyncMock()
    mock_repo_prefs_dir.iterdir.return_value = iterdir_iterator
    iterdir_iterator.__aiter__.return_value = [test1_plist]
    await prefs_export(mock_out_dir, commit=True)
    mock_is_git_installed.assert_called_once()
    mock_setup_output_directory.assert_called_once()
    mock_generate_domains.__aiter__.assert_called_once()
    mock_defaults_export.assert_called()
    assert mock_git.call_count == 3
