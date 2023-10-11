from copy import deepcopy
from typing import cast
import logging
import re

from .filters import BAD_DOMAINS, BAD_DOMAIN_PREFIXES, BAD_KEYS, BAD_KEYS_RE
from .mp_typing import MutablePlistList, MutablePlistRoot, PlistList, PlistRoot

__all__ = ('remove_data_fields', 'remove_data_fields_list')

logger = logging.getLogger(__name__)


def should_ignore_domain(domain: str) -> bool:
    return domain in BAD_DOMAINS or any(domain.startswith(prefix) for prefix in BAD_DOMAIN_PREFIXES)


def should_ignore_key(domain: str, key: str) -> bool:
    if re.match(BAD_KEYS_RE, key):
        logger.debug('Skipping %s because it matched the bad keys RE.', key)
        return True
    if domain in BAD_KEYS and key in BAD_KEYS[domain]:
        logger.debug('Skipping %s because it matched the bad keys dict.', key)
        return True
    if domain in BAD_KEYS:
        for x in filter(lambda y: y.startswith('re:'), list(BAD_KEYS[domain])):
            if re.match(x[3:], key):
                logger.debug('Skipping %s because it matched a regexp in %s.', key, domain)
                return True
    return False


def remove_data_fields_list(pl_list: PlistList) -> PlistList:
    """Clean up data fields from a ``PlistList``."""
    ret = cast(MutablePlistList, deepcopy(pl_list))
    index = 0
    for value in pl_list:
        if not isinstance(value, bytes):
            if isinstance(value, dict):
                ret[index] = cast(MutablePlistRoot, remove_data_fields(value))
            elif isinstance(value, list):
                ret[index] = cast(MutablePlistList, remove_data_fields_list(value))
            if isinstance(value, (list, dict)) and not ret[index]:
                del ret[index]
            index = max(0, index - 1)
            continue
        del ret[index]
        index = max(0, index - 1)
    return ret


def remove_data_fields(root: PlistRoot) -> PlistRoot:
    """Clean up data fields from a ``PlistRoot``."""
    ret = cast(MutablePlistRoot, deepcopy(root))
    for key, value in root.items():
        if not isinstance(value, bytes):
            if isinstance(value, list):
                ret[key] = cast(MutablePlistList, remove_data_fields_list(value))
            elif isinstance(value, dict):
                ret[key] = cast(MutablePlistRoot, remove_data_fields(value))
            if isinstance(value, (list, dict, set)) and not ret[key]:
                del ret[key]
            continue
        del ret[key]
    return ret
