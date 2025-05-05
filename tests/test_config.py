from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from macprefs.config import read_config
from macprefs.exceptions import ConfigTypeError
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_read_config_no_file(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=False)
    mock_logger = mocker.patch('macprefs.config.log.debug')
    result = read_config()
    assert result == {}
    mock_logger.assert_called_once_with('No configuration file found. Using defaults.')


def test_read_config_file_exists(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=True)
    mocker.patch('macprefs.config.Path.read_text', return_value='')
    mock_tomlkit_loads = mocker.patch('macprefs.config.tomlkit.loads',
                                      return_value={'tool': {
                                          'macprefs': {
                                              'key': 'value'
                                          }
                                      }})
    result = read_config(Path('/fake/path'))
    assert result == {
        'extend-ignore-keys': {},
        'extend-ignore-key-regexes': [],
        'extend-ignore-domain-prefixes': [],
        'extend-ignore-domains': [],
    }
    mock_tomlkit_loads.assert_called_once()


def test_read_config_invalid_mapping(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=True)
    mocker.patch('macprefs.config.Path.read_text', return_value='')
    mocker.patch('macprefs.config.tomlkit.loads',
                 return_value={'tool': {
                     'macprefs': {
                         'ignore-keys': 'not-a-dict'
                     }
                 }})
    with pytest.raises(ConfigTypeError, match='dict of keys to lists of strings'):
        read_config(Path('/fake/path'))


def test_read_config_invalid_sequence(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=True)
    mocker.patch('macprefs.config.Path.read_text', return_value='')
    mocker.patch('macprefs.config.tomlkit.loads',
                 return_value={'tool': {
                     'macprefs': {
                         'ignore-key-regexes': 123
                     }
                 }})
    with pytest.raises(ConfigTypeError, match='list of strings'):
        read_config(Path('/fake/path'))


def test_read_config_invalid_sequence_inner_type(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=True)
    mocker.patch('macprefs.config.Path.read_text', return_value='')
    mocker.patch('macprefs.config.tomlkit.loads',
                 return_value={'tool': {
                     'macprefs': {
                         'ignore-key-regexes': [1, 2, 3]
                     }
                 }})
    with pytest.raises(ConfigTypeError, match='list of strings'):
        read_config(Path('/fake/path'))


def test_read_config_list_of_strings(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=True)
    mocker.patch('macprefs.config.Path.read_text', return_value='')
    mocker.patch('macprefs.config.tomlkit.loads',
                 return_value={'tool': {
                     'macprefs': {
                         'ignore-key-regexes': ['a', 'b', 'c']
                     }
                 }})
    result = read_config(Path('/fake/path'))
    assert result == {
        'extend-ignore-keys': {},
        'extend-ignore-key-regexes': [],
        'extend-ignore-domain-prefixes': [],
        'extend-ignore-domains': [],
        'ignore-key-regexes': ['a', 'b', 'c']
    }


def test_read_config_dict_to_invalid_type(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=True)
    mocker.patch('macprefs.config.Path.read_text', return_value='')
    mocker.patch('macprefs.config.tomlkit.loads',
                 return_value={'tool': {
                     'macprefs': {
                         'extend-ignore-keys': {
                             'key1': 11
                         },
                     }
                 }})
    with pytest.raises(ConfigTypeError, match='must be of type dict of keys to lists of strings'):
        read_config(Path('/fake/path'))


def test_read_config_dict_to_invalid_type_inner(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=True)
    mocker.patch('macprefs.config.Path.read_text', return_value='')
    mocker.patch('macprefs.config.tomlkit.loads',
                 return_value={'tool': {
                     'macprefs': {
                         'extend-ignore-keys': {
                             'key1': [11]
                         },
                     }
                 }})
    with pytest.raises(ConfigTypeError, match='must be of type dict of keys to lists of strings'):
        read_config(Path('/fake/path'))


def test_read_config_dict(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=True)
    mocker.patch('macprefs.config.Path.read_text', return_value='')
    mocker.patch(
        'macprefs.config.tomlkit.loads',
        return_value={'tool': {
            'macprefs': {
                'extend-ignore-keys': {
                    'key1': ['a', 'b', 'c'],
                },
            }
        }})
    result = read_config(Path('/fake/path'))
    assert result == {
        'extend-ignore-keys': {
            'key1': ['a', 'b', 'c'],
        },
        'extend-ignore-key-regexes': [],
        'extend-ignore-domain-prefixes': [],
        'extend-ignore-domains': []
    }


def test_read_config_deploy_key_warning(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=False)
    mock_path = mocker.MagicMock()
    mock_path.return_value.exists.side_effect = [True, False]
    mock_path.return_value.read_text.return_value = ''
    mocker.patch('macprefs.config.tomlkit.loads',
                 return_value={'tool': {
                     'macprefs': {
                         'deploy-key': '/fake/deploy-key'
                     }
                 }})
    mock_logger = mocker.patch('macprefs.config.log.warning')
    result = read_config(mock_path)
    mock_logger.assert_called_once_with('Deploy key `%s` does not exist.', '/fake/deploy-key')
    assert result == {
        'extend-ignore-keys': {},
        'extend-ignore-key-regexes': [],
        'extend-ignore-domain-prefixes': [],
        'extend-ignore-domains': []
    }


def test_read_config_deploy_key(mocker: MockerFixture) -> None:
    mocker.patch('macprefs.config.Path.exists', return_value=True)
    mock_path = mocker.MagicMock()
    mock_path.return_value.exists.side_effect = [True, False]
    mock_path.return_value.read_text.return_value = ''
    mocker.patch('macprefs.config.tomlkit.loads',
                 return_value={'tool': {
                     'macprefs': {
                         'deploy-key': '/fake/deploy-key'
                     }
                 }})
    result = read_config(mock_path)
    assert result == {
        'extend-ignore-keys': {},
        'extend-ignore-key-regexes': [],
        'extend-ignore-domain-prefixes': [],
        'extend-ignore-domains': [],
        'deploy-key': '/fake/deploy-key'
    }
