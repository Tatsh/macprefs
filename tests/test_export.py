from asyncio.subprocess import Process
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
import base64

from click.testing import CliRunner
from macprefs import prefs_export
from pytest_mock.plugin import MockerFixture

# spell-checker: disable
SAFARI_PLIST_BASE64 = ('YnBsaXN0MDDRAQJfEBFSZXNldENsb3VkSGlzdG9yeQkICx8AAAAAAAABAQAAAAAAAAADAAAAAAA'
                       'AAAAAAAAAAAAAIA==')
# spell-checker: enable


def create_entry(name: str) -> MagicMock:
    m = MagicMock(spec=Path)
    m.name = name
    m.stem = Path(name).stem
    return m


def test_export_no_args_no_git_no_plutil(runner: CliRunner, mocker: MockerFixture) -> None:
    def sp_exec_mock(command: str, *args: Any, **kwargs: Any) -> MagicMock:
        p = MagicMock(spec=Process)
        p.returncode = 1
        return p

    def path_truediv(append: str) -> MagicMock:
        m = MagicMock(spec=Path)
        if append == 'Library/Preferences':
            m.glob.return_value = (create_entry('$(PRODUCT_BUNDLE_IDENTIFIER).plist'),
                                   create_entry('.aaaa.plist'),
                                   create_entry('com.apple.Safari.plist'),
                                   create_entry('com.apple.Music.plist'),
                                   create_entry('com.apple.TV.plist'))
        return m

    path_mock = mocker.patch('macprefs.main.Path')
    path_mock.home.return_value.__truediv__.side_effect = path_truediv
    # _setup_out_dir
    path_mock.return_value.resolve.return_value.__truediv__.return_value = MagicMock(spec=Path)
    # plist_out in _defaults_export()  # noqa: ERA001
    (path_mock.return_value.resolve.return_value.__truediv__.return_value.__truediv__.return_value.
     open.return_value.__enter__.return_value) = BytesIO(base64.b64decode(SAFARI_PLIST_BASE64))
    shell = mocker.patch('macprefs.main.sp.create_subprocess_exec', side_effect=sp_exec_mock)
    shutil_copy_mock = mocker.patch('macprefs.main.shutil.copy')
    run = runner.invoke(prefs_export, '--debug')
    assert shutil_copy_mock.call_count >= 1
    assert run.exit_code == 1
    assert shell.call_count == 1
