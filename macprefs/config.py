"""Configuration file parsing and validation."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
import logging

import tomlkit

from .exceptions import ConfigTypeError

log = logging.getLogger(__name__)

_DEPLOY_KEY = 'deploy-key'
_DICT_KEYS_MSG = 'dict of keys to lists of strings'


def read_config(config_file: Path | None = None) -> dict[str, Any]:
    """
    Read and validate the configuration file.

    Returns
    -------
    dict[str, Any]
        Parsed configuration, or an empty dict if no file was found.

    Raises
    ------
    ConfigTypeError
        If the configuration structure is invalid.
    """
    if not config_file or not config_file.exists():
        log.debug('No configuration file found. Using defaults.')
        return {}
    log.debug('Parsing configuration file `%s`.', config_file)
    config = tomlkit.loads(config_file.read_text()).get('tool', {}).get('macprefs', {})
    ret: dict[str, Any] = {
        'extend-ignore-keys': {},
        'extend-ignore-key-regexes': [],
        'extend-ignore-domain-prefixes': [],
        'extend-ignore-domains': []
    }
    for key in ('extend-ignore-keys', 'ignore-keys'):
        if key in config:
            if not isinstance(config[key], Mapping):
                raise ConfigTypeError(key, _DICT_KEYS_MSG)
            for val in config[key].values():
                if not isinstance(val, Sequence):
                    raise ConfigTypeError(key, _DICT_KEYS_MSG)
                for v in val:
                    if not isinstance(v, str):
                        raise ConfigTypeError(key, _DICT_KEYS_MSG)
            ret[key] = config[key]
    for key in ('extend-ignore-key-regexes', 'extend-ignore-domain-prefixes',
                'extend-ignore-domains', 'ignore-key-regexes', 'ignore-domain-prefixes',
                'ignore-domains'):
        if key in config:
            if not isinstance(config[key], Sequence):
                raise ConfigTypeError(key, 'list of strings')
            for item in config[key]:
                if not isinstance(item, str):
                    raise ConfigTypeError(key, 'list of strings')
            ret[key] = config[key]
    if _DEPLOY_KEY in config:
        if not Path(config[_DEPLOY_KEY]).exists():
            log.warning('Deploy key `%s` does not exist.', config[_DEPLOY_KEY])
        else:
            ret[_DEPLOY_KEY] = config[_DEPLOY_KEY]
    return ret
