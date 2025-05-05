from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, cast

from macprefs.constants import OUTPUT_FILE_MAXIMUM_LINE_LENGTH
from macprefs.plist2defaults import (
    _can_decode_unicode,  # noqa: PLC2701
    convert_value,
    is_simple,
    plist_to_defaults_commands,
    to_str,
)
import pytest

if TYPE_CHECKING:
    from macprefs.typing import PlistRoot


@pytest.mark.parametrize(('input_bytes', 'expected'), [
    (b'valid', True),
    (b'\xff\xfe', False),
])
def test_can_decode_unicode(input_bytes: bytes, expected: bool) -> None:  # noqa: FBT001
    assert _can_decode_unicode(input_bytes) == expected


@pytest.mark.parametrize(('input_value', 'expected'), [
    ({
        'key': 'value'
    }, True),
    ({
        'key': b'\xff\xfe'
    }, False),
    ([1, 2, 3], True),
    ([b'\xff\xfe'], False),
    ([datetime.now(tz=timezone.utc)], False),
])
def test_is_simple(input_value: Any, expected: bool) -> None:  # noqa: FBT001
    assert is_simple(input_value) == expected


@pytest.mark.parametrize(('input_value', 'expected'), [
    (b'test', 'test'),
    (b'\xff', 'ff'),
    ('True', 'true'),
    ('False', 'false'),
    ('normal', 'normal'),
])
def test_to_str(input_value: bytes | str, expected: str) -> None:
    assert to_str(input_value) == expected


@pytest.mark.parametrize(('key', 'value', 'prefix', 'expected'), [
    ('key', True, 'defaults write domain', ['defaults write domain key -bool true']),
    ('key', 123, 'defaults write domain', ['defaults write domain key -int 123']),
    ('key', 1.23, 'defaults write domain', ['defaults write domain key -float 1.23']),
    ('key', b'data', 'defaults write domain', ['defaults write domain key -data 64617461']),
    ('key', 'string 2', 'defaults write domain', ["defaults write domain key -string 'string 2'"]),
    ('key', [1, 2], 'defaults write domain',
     ['defaults write domain key -array 1 \\\n                                 2']),
    ('key', {
        'a': 'b'
    }, 'defaults write domain', ['defaults write domain key -dict a b']),
    ('key', datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc), 'defaults write domain',
     ["defaults write domain key -date '2023-01-01 12:00:00 +0000'"]),
    ('key', Exception(), 'defaults write domain', []),
    ('key', b'x' * (OUTPUT_FILE_MAXIMUM_LINE_LENGTH + 1), 'defaults write domain', []),
    ('key', 'x' * (OUTPUT_FILE_MAXIMUM_LINE_LENGTH + 1), 'defaults write domain', []),
])
def test_convert_value(key: str, value: Any, prefix: str, expected: list[str]) -> None:
    assert list(convert_value(key, value, prefix)) == expected


def test_plist_to_defaults_commands(mocker: Any) -> None:
    mock_root = {'key1': 'value1', 'key2': 123}
    mock_key_filter = mocker.MagicMock(return_value=False)
    result = list(
        plist_to_defaults_commands('domain',
                                   cast('PlistRoot', mock_root),
                                   key_filter=mock_key_filter))
    assert result == [
        '# domain',
        'defaults write domain key1 -string value1',
        'defaults write domain key2 -int 123',
        '',
    ]
    mock_key_filter.assert_any_call('domain', 'key1')
    mock_key_filter.assert_any_call('domain', 'key2')


def test_plist_to_defaults_commands_invert_filter(mocker: Any) -> None:
    mock_root = {'key1': 'value1', 'key2': 123}
    mock_key_filter = mocker.MagicMock(return_value=False)
    result = list(
        plist_to_defaults_commands('domain',
                                   cast('PlistRoot', mock_root),
                                   key_filter=mock_key_filter,
                                   invert_filters=True))
    assert result == []
    mock_key_filter.assert_any_call('domain', 'key1')
    mock_key_filter.assert_any_call('domain', 'key2')
