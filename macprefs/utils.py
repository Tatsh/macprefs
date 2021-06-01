from collections.abc import ValuesView
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, AnyStr, Mapping, Optional, Sequence, Union
import logging
import sys

from .mp_typing import ComplexInnerTypes

__all__ = (
    'is_simple',
    'setup_logging_stderr',
    'to_str',
)


@lru_cache()
def setup_logging_stderr(name: Optional[str] = None,
                         verbose: bool = False) -> logging.Logger:
    """Logging utility."""
    name = name if name else Path(sys.argv[0]).name
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG if verbose else logging.INFO)
    channel = logging.StreamHandler(sys.stderr)
    channel.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    channel.setLevel(logging.DEBUG if verbose else logging.INFO)
    log.addHandler(channel)
    return log


async def _can_decode_unicode(x: bytes) -> bool:
    try:
        x.decode('utf-8')
    except UnicodeDecodeError:
        return False
    return True


SimpleArg = Union[Mapping[Any, ComplexInnerTypes],
                    Sequence[ComplexInnerTypes], ValuesView[str]]


async def is_simple(x: SimpleArg) -> bool:
    """Check if a value is a simple type of value."""
    if isinstance(x, dict):
        x = x.values()
    for y in x:
        if (isinstance(y, (datetime, list, dict))
                or (isinstance(y, bytes) and not await _can_decode_unicode(y))):
            return False
    return True


def to_str(x: AnyStr) -> str:
    """Convert a value to a string for shell."""
    if isinstance(x, bytes):
        try:
            return x.decode('utf-8')
        except UnicodeDecodeError:
            return ''.join(hex(y)[2:] for y in x)
    ret = str(x)
    return ret.lower() if ret in ('True', 'False') else ret
