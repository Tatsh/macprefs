from __future__ import annotations

from datetime import datetime
from shlex import quote
from typing import TYPE_CHECKING, Any
import logging

from .constants import OUTPUT_FILE_MAXIMUM_LINE_LENGTH

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from .typing import PlistRoot, SimpleArg

__all__ = ('plist_to_defaults_commands',)

log = logging.getLogger(__name__)


def _can_decode_unicode(x: bytes) -> bool:
    try:
        x.decode()
    except UnicodeDecodeError:
        return False
    return True


def is_simple(x: SimpleArg) -> bool:
    """Check if a value is a simple type of value."""
    if isinstance(x, dict):
        x = x.values()
    for y in x:
        if (isinstance(y, (datetime, list, dict))
                or (isinstance(y, bytes) and not _can_decode_unicode(y))):
            return False
    return True


def to_str(x: bytes | str) -> str:
    """Convert a value to a string for shell."""
    if isinstance(x, bytes):
        try:
            return x.decode('utf-8')
        except UnicodeDecodeError:
            return ''.join(f'{y:x}' for y in x)
    ret = str(x)
    return ret.lower() if ret in {'True', 'False'} else ret


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
        printed_value = quote(''.join(f'{z:x}' for z in value))
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
                               key_filter: Callable[[str, str], bool] | None = None,
                               *,
                               invert_filters: bool = False) -> Iterator[str]:
    """
    Given a :py:class:`macprefs.typing.PlistRoot`, generate ``defaults write`` commands.

    Parameters
    ----------
    domain : str
        The preferences domain.
    root : PlistRoot
        The root of the preferences dictionary.
    key_filter : Callable[[str, str], bool] | None
        A function that takes a domain and key and returns ``True`` if the key should be ignored.
    invert_filters : bool
        If ``True``, invert the key filter.

    Yields
    ------
    str
        Lines for output into a shell script.
    """
    values: list[str] = []
    prefix = f'defaults write {quote(domain)}'
    if key_filter and invert_filters:
        orig_key_filter = key_filter

        def inverted(d: str, k: str) -> bool:
            return not orig_key_filter(d, k)

        key_filter = inverted
    for key, value in sorted(root.items()):
        if key_filter and key_filter(domain, key):
            continue
        values.extend(convert_value(key, value, prefix))
    if values:
        yield f'# {domain}'
        yield from values
        yield ''
