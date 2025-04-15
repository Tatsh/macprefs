from collections.abc import Mapping, Sequence, ValuesView
from datetime import datetime
from typing import Any

from .typing import ComplexInnerTypes

__all__ = ('SimpleArg', 'is_simple', 'to_str')


def _can_decode_unicode(x: bytes) -> bool:
    try:
        x.decode('utf-8')
    except UnicodeDecodeError:
        return False
    return True


SimpleArg = Mapping[Any, ComplexInnerTypes] | Sequence[ComplexInnerTypes] | ValuesView[str]


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
