from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, cast
import logging
import re

from .filters import BAD_KEYS
from .filters.bad_keys_re import BAD_KEYS_RE

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from .typing import MutablePlistList, MutablePlistRoot, PlistList, PlistRoot

__all__ = ('make_key_filter', 'remove_data_fields', 'remove_data_fields_list')

log = logging.getLogger(__name__)


def make_key_filter(bad_keys_re_addendum: Iterable[str] | None = None,
                    bad_keys_addendum: Mapping[str, set[str]] | None = None,
                    *,
                    reset_re: bool = False,
                    reset_bad_keys: bool = False) -> Callable[[str, str], bool]:
    bad_keys_re = ('|'.join(set(bad_keys_re_addendum or [])) if reset_re else f'{BAD_KEYS_RE}|' +
                   '|'.join(set(bad_keys_re_addendum or [])))
    bad_keys = (bad_keys_addendum or {}) if reset_bad_keys else {
        **BAD_KEYS,
        **(bad_keys_addendum or {})
    }

    def should_ignore_key(domain: str, key: str) -> bool:
        if bad_keys_re and re.match(bad_keys_re, key):
            log.debug('Skipping %s-%s because it matched the bad keys RE.', domain, key)
            return True
        if domain in bad_keys and key in bad_keys[domain]:
            log.debug('Skipping %s-%s because it matched the bad keys dict.', domain, key)
            return True
        if domain in bad_keys:
            for x in {y for y in bad_keys[domain] if y.startswith('re:')}:
                if re.match(x[3:], key):
                    log.debug('Skipping %s-%s because it matched regular expression.', key, domain)
                    return True
        return False

    return should_ignore_key


def remove_data_fields_list(pl_list: PlistList) -> PlistList:
    """Clean up data fields from a :py:class:`macprefs.typing.PlistList`."""
    ret = cast('MutablePlistList', deepcopy(pl_list))
    index = 0
    for value in pl_list:
        if not isinstance(value, bytes):
            if isinstance(value, dict):
                ret[index] = cast('MutablePlistRoot', remove_data_fields(value))
            elif isinstance(value, list):
                ret[index] = cast('MutablePlistList', remove_data_fields_list(value))
            if isinstance(value, (list, dict)) and not ret[index]:
                del ret[index]
            index = max(0, index - 1)
            continue
        del ret[index]
        index = max(0, index - 1)
    return ret


def remove_data_fields(root: PlistRoot) -> PlistRoot:
    """Clean up data fields from a :py:class:`macprefs.typing.PlistRoot`."""
    ret = cast('MutablePlistRoot', deepcopy(root))
    for key, value in root.items():
        if not isinstance(value, bytes):
            if isinstance(value, list):
                ret[key] = cast('MutablePlistList', remove_data_fields_list(value))
            elif isinstance(value, dict):
                ret[key] = cast('MutablePlistRoot', remove_data_fields(value))
            if isinstance(value, (list, dict, set)) and not ret[key]:
                del ret[key]
            continue
        del ret[key]
    return ret
