# pylint: disable=too-many-locals,too-many-branches
from datetime import datetime
from shlex import quote
from typing import AsyncIterator
import re

from .filters import BAD_DOMAINS, BAD_DOMAIN_PREFIXES, BAD_KEYS, BAD_KEYS_RE
from .mp_typing import PlistRoot
from .utils import is_simple, setup_logging_stderr, to_str

__all__ = ('plist_to_defaults_commands', )


async def plist_to_defaults_commands(
        domain: str,
        root: PlistRoot,
        debug: bool = False) -> AsyncIterator[str]:
    """Given a PlistRoot, generate a series of `defaults write` commands."""
    if domain in BAD_DOMAINS:
        return
    for prefix in BAD_DOMAIN_PREFIXES:
        if domain.startswith(prefix):
            return

    yield f'# {domain}'

    prefix = f'defaults write {quote(domain)}'
    log = setup_logging_stderr(verbose=debug)

    for key, value in sorted(root.items()):
        if re.match(BAD_KEYS_RE, key):
            continue
        if domain in BAD_KEYS and key in BAD_KEYS[domain]:
            continue
        if domain in BAD_KEYS:
            found = False
            for x in filter(lambda y: y.startswith('re:'),
                            list(BAD_KEYS[domain])):
                if re.match(x[3:], key):
                    found = True
                    break
            if found:
                continue

        if isinstance(value, bool):
            yield f'{prefix} {quote(key)} -bool {"true" if value else "false"}'
        elif isinstance(value, int):
            yield f'{prefix} {quote(key)} -int {quote(str(value))}'
        elif isinstance(value, float):
            yield f'{prefix} {quote(key)} -float {quote(str(value))}'
        elif isinstance(value, bytes):
            if len(value) > 120:
                continue
            printed_value = quote(''.join(hex(z)[2:] for z in value))
            yield f'{prefix} {quote(key)} -data {printed_value}'
        elif isinstance(value, str):
            if len(value) > 120:
                continue
            yield f'{prefix} {quote(key)} -string {quote(value)}'
        elif isinstance(value, list) and await is_simple(value):
            first = (quote(str(value[0])) +
                     ' \\\n' if len(value) > 1 else quote(str(value[0])))
            key = quote(key)
            spaces = ' ' * (len(prefix) + 1 + len(key) + 1 + 7)
            # [] required for this line, otherwise TypeError: can only join an
            # iterable
            rest = ' \\\n'.join(
                [f'{spaces}{quote(to_str(x))}' for x in value[1:]])
            yield f'{prefix} {key} -array {"".join(first + rest)}'
        elif isinstance(value, dict) and await is_simple(value):
            dict_values = [
                f'{quote(to_str(x))} {quote(to_str(y))}'
                for x, y in value.items()
            ]
            f_dict_values = (f'{dict_values[0]}\\\n'
                             if len(dict_values) > 1 else dict_values[0])
            key = quote(key)
            spaces = ' ' * (len(prefix) + 1 + len(key) + 1 + 10)
            dict_values_ = ' \\\n'.join(f'{spaces}{x}'
                                        for x in dict_values[1:])
            yield f'{prefix} {key} -dict {f_dict_values}{dict_values_}'
        elif isinstance(value, datetime):
            full_date = quote(value.strftime('%Y-%m-%d %I:%M:%S +0000'))
            yield f'{prefix} {quote(key)} -date {full_date}'
        else:
            log.debug('Skipped %s %s', domain, quote(key))
    yield ''
