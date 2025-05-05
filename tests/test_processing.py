from __future__ import annotations

from typing import TYPE_CHECKING, cast

from macprefs.processing import make_key_filter, remove_data_fields, remove_data_fields_list
import pytest

if TYPE_CHECKING:
    from macprefs.typing import PlistList, PlistRoot
    from pytest_mock import MockerFixture


@pytest.fixture
def mock_bad_keys(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.processing.BAD_KEYS', {'test_domain': {'test_key', 're:^test_.*'}})


@pytest.fixture
def mock_bad_keys_re(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.processing.BAD_KEYS_RE', r'^bad_.*')


def test_make_key_filter_with_reset(mock_bad_keys: None, mock_bad_keys_re: None) -> None:
    filter_func = make_key_filter(reset_re=True, reset_bad_keys=True)
    assert filter_func('test_domain', 'test_key') is False
    assert filter_func('test_domain', 'bad_key') is False
    assert filter_func('test_domain', 'random_key') is False


def test_make_key_filter_with_addendum(mock_bad_keys: None, mock_bad_keys_re: None) -> None:
    filter_func = make_key_filter([r'^custom_.*'], {'custom_domain': {'custom_key'}})
    assert filter_func('custom_domain', 'custom_key') is True
    assert filter_func('test_domain', 'test_key') is True
    assert filter_func('test_domain', 'bad_key') is True
    assert filter_func('test_domain', 'custom_key') is True


def test_make_key_filter_with_regex_match(mock_bad_keys: None, mock_bad_keys_re: None) -> None:
    filter_func = make_key_filter()
    assert filter_func('test_domain', 'test_key') is True
    assert filter_func('test_domain', 'test_regex') is True
    assert filter_func('test_domain', 'bad_key') is True


def test_make_key_filter_with_regex_match_2() -> None:
    filter_func = make_key_filter(bad_keys_addendum={'test_domain': {'re:^test_'}},
                                  reset_bad_keys=True,
                                  reset_re=True)
    assert filter_func('test_domain', 'test_key') is True
    assert filter_func('test_domain', 'test_regex') is True
    assert filter_func('test_domain', 'bad_key') is False


def test_remove_data_fields_list_with_bytes() -> None:
    input_data = [b'test', b'another']
    result = remove_data_fields_list(input_data)
    assert result == []


def test_remove_data_fields_list_with_nested_structures() -> None:
    input_data = [
        {
            'key': b'value'
        },
        [
            b'list_value',
            {
                'nested_key': b'nested_value',
                'k': 'a'
            },
        ],
        b'bytes_value',
        1,
    ]
    result = remove_data_fields_list(cast('PlistList', input_data))
    assert result == [[{'k': 'a'}], 1]


def test_remove_data_fields_with_bytes() -> None:
    input_data = {'key': b'value', 'another_key': b'another_value'}
    result = remove_data_fields(input_data)
    assert result == {}


def test_remove_data_fields_with_nested_structures() -> None:
    input_data = {
        'key': {
            'nested_key': b'nested_value'
        },
        'list_key': [
            b'list_value',
            {
                'deep_key': b'deep_value'
            },
        ],
        'bytes_key': b'bytes_value'
    }
    result = remove_data_fields(cast('PlistRoot', input_data))
    assert result == {}
