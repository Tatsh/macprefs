import plistlib

from click.testing import CliRunner
from deepdiff import DeepDiff
from macprefs import install_job
from pytest_mock.plugin import MockerFixture

EXPECTED_PLIST = {
    'Label': 'sh.tat.macprefs',
    'ProgramArguments': ['/bin/prefs-export', '--output-directory', 'output-dir', '--commit'],
    'RunAtLoad': True,
    'StartCalendarInterval': {
        'Hour': 0,
        'Minute': 0
    }
}

INSTALL_JOB_AWAIT_COUNT = 5


def test_install_job_no_args(runner: CliRunner, mocker: MockerFixture) -> None:
    written = b''

    def write(s: bytes) -> None:
        nonlocal written
        written += s

    sp_exec = mocker.patch('macprefs.main.sp.create_subprocess_exec')
    sp_exec.return_value.stdout.read.return_value = b'/bin/prefs-export'
    sp_exec.return_value.returncode = 0
    path_mock = mocker.patch('macprefs.main.Path')
    path_mock.return_value.resolve.return_value = 'output-dir'
    (path_mock.home.return_value.__truediv__.return_value.open.return_value.__enter__.return_value.
     write.side_effect) = write
    run = runner.invoke(install_job, '--debug')
    path_mock.home.return_value.__truediv__.return_value.open.return_value.__enter__.assert_called()
    path_mock.return_value.resolve.assert_called()
    data = plistlib.loads(written)
    assert not DeepDiff(
        data, EXPECTED_PLIST, exclude_paths=['StandardErrorPath', 'StandardOutPath'])
    assert sp_exec.await_count == INSTALL_JOB_AWAIT_COUNT
    assert run.exit_code == 0


def test_install_exec_error(runner: CliRunner, mocker: MockerFixture) -> None:
    sp_exec = mocker.patch('macprefs.main.sp.create_subprocess_exec')
    sp_exec.return_value.stdout.read.return_value = b'/bin/prefs-export'
    sp_exec.return_value.returncode = 1
    path_mock = mocker.patch('macprefs.main.Path')
    path_mock.return_value.resolve.return_value = 'output-dir'
    run = runner.invoke(install_job, '--debug')
    path_mock.home.return_value.__truediv__.return_value.open.return_value.__enter__.assert_called()
    path_mock.return_value.resolve.assert_called()
    assert sp_exec.await_count == INSTALL_JOB_AWAIT_COUNT
    assert run.exit_code != 0
