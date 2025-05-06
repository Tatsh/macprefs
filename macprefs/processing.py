from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, cast
import logging
import re

from .filters import BAD_KEYS
from .filters.bad_keys_re import BAD_KEYS_RE

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from .typing import PlistList, PlistRoot

__all__ = ('make_key_filter', 'remove_data_fields', 'remove_data_fields_list')

log = logging.getLogger(__name__)


def make_key_filter(bad_keys_re_addendum: Iterable[str] | None = None,
                    bad_keys_addendum: Mapping[str, set[str]] | None = None,
                    *,
                    reset_re: bool = False,
                    reset_bad_keys: bool = False) -> Callable[[str, str], bool]:
    """Create a function to filter out ignored keys."""
    bad_keys_re = ('|'.join(set(bad_keys_re_addendum or [])) if reset_re else f'{BAD_KEYS_RE}|' +
                   '|'.join(set(bad_keys_re_addendum or []))).rstrip('|')
    bad_keys = (bad_keys_addendum or {}) if reset_bad_keys else {
        **BAD_KEYS,
        **(bad_keys_addendum or {})
    }
    log.debug('Ignored keys RE: %s', bad_keys_re)

    def should_ignore_key(domain: str, key: str) -> bool:
        if bad_keys_re and re.match(bad_keys_re, key):
            log.debug('Skipping %s[%s] because it matched the ignored keys RE.', domain, key)
            return True
        if domain in bad_keys and key in bad_keys[domain]:
            log.debug('Skipping %s[%s] because it matched the ignored keys dict.', domain, key)
            return True
        if domain in bad_keys:
            for x in {y for y in bad_keys[domain] if y.startswith('re:')}:
                if re.match(x[3:], key):
                    log.debug('Skipping %s[%s] because it matched regular expression.', key, domain)
                    return True
        return False

    return should_ignore_key


def remove_data_fields_list(pl_list: PlistList) -> PlistList:
    """Clean up data fields from a :py:class:`macprefs.typing.PlistList`."""
    ret: list[Any] = []
    for value in pl_list:
        val: Any = deepcopy(value)
        if isinstance(value, bytes):
            continue
        if isinstance(value, list):
            val = remove_data_fields_list(value)
        elif isinstance(value, dict):
            val = remove_data_fields(value)
        if isinstance(value, list | dict) and not val:
            continue
        ret.append(val)
    return cast('PlistList', ret)


def remove_data_fields(root: PlistRoot) -> PlistRoot:
    """Clean up data fields from a :py:class:`macprefs.typing.PlistRoot`."""
    ret: dict[str, Any] = {}
    for key, value in root.items():
        val: Any = deepcopy(value)
        if isinstance(value, bytes):
            continue
        if isinstance(value, list):
            val = remove_data_fields_list(val)
        elif isinstance(value, dict):
            val = remove_data_fields(val)
        if isinstance(value, list | dict) and not val:
            continue
        ret[key] = val
    return cast('PlistRoot', ret)
