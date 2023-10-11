from datetime import datetime
from shlex import quote
from typing import Any, Callable, Iterator
import logging

from .constants import OUTPUT_FILE_MAXIMUM_LINE_LENGTH
from .mp_typing import PlistRoot
from .processing import should_ignore_domain, should_ignore_key
from .utils import is_simple, to_str

__all__ = ('plist_to_defaults_commands',)

log = logging.getLogger(__name__)


def convert_value(key: str, value: Any, prefix: str) -> Iterator[str]:
    if isinstance(value, bool):
        yield f'{prefix} {quote(key)} -bool {"true" if value else "false"}'
    elif isinstance(value, int):
        yield f'{prefix} {quote(key)} -int {quote(str(value))}'
    elif isinstance(value, float):
        yield f'{prefix} {quote(key)} -float {quote(str(value))}'
    elif isinstance(value, bytes):
        if len(value) > OUTPUT_FILE_MAXIMUM_LINE_LENGTH:
            return
        printed_value = quote(''.join(hex(z)[2:] for z in value))
        yield f'{prefix} {quote(key)} -data {printed_value}'
    elif isinstance(value, str):
        if len(value) > OUTPUT_FILE_MAXIMUM_LINE_LENGTH:
            return
        yield f'{prefix} {quote(key)} -string {quote(value)}'
    elif isinstance(value, list) and is_simple(value):
        first = (quote(str(value[0])) + ' \\\n' if len(value) > 1 else quote(str(value[0])))
        key_quoted = quote(key)
        spaces = ' ' * (len(prefix) + 1 + len(key_quoted) + 1 + 7)
        rest = ' \\\n'.join(f'{spaces}{quote(to_str(x))}' for x in value[1:])
        yield f'{prefix} {key_quoted} -array {"".join(first + rest)}'
    elif isinstance(value, dict) and is_simple(value):
        dict_values = [f'{quote(to_str(x))} {quote(to_str(y))}' for x, y in value.items()]
        f_dict_values = (f'{dict_values[0]}\\\n' if len(dict_values) > 1 else dict_values[0])
        key_quoted = quote(key)
        spaces = ' ' * (len(prefix) + 1 + len(key_quoted) + 1 + 10)
        dict_values_ = ' \\\n'.join(f'{spaces}{x}' for x in dict_values[1:])
        yield f'{prefix} {key_quoted} -dict {f_dict_values}{dict_values_}'
    elif isinstance(value, datetime):
        full_date = quote(value.strftime('%Y-%m-%d %I:%M:%S +0000'))
        yield f'{prefix} {quote(key)} -date {full_date}'


def plist_to_defaults_commands(domain: str,
                               root: PlistRoot,
                               domain_filter: Callable[[str], bool] | None = should_ignore_domain,
                               key_filter: Callable[[str, str], bool] | None = should_ignore_key,
                               inverse_filters: bool = False) -> Iterator[str]:
    """Given a ``PlistRoot``, generate a series of ``defaults write`` commands."""
    if domain_filter and (not domain_filter(domain) if inverse_filters else domain_filter(domain)):
        return
    values: list[str] = []
    prefix = f'defaults write {quote(domain)}'
    for key, value in sorted(root.items()):
        if (key_filter
                and (not key_filter(domain, key) if inverse_filters else key_filter(domain, key))):
            continue
        values.extend(convert_value(key, value, prefix))
    if values:
        yield f'# {domain}'
        yield from values
        yield ''
