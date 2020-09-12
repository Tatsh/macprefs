from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, AnyStr, List, Mapping, Optional, Union, ValuesView
import logging
import plistlib
import sys

from .mp_typing import NonSimpleInnerTypes

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


async def is_simple(
    x: Union[Mapping[Any, NonSimpleInnerTypes], List[NonSimpleInnerTypes],
             ValuesView]
) -> bool:
    """Check if a value is a simple type of value."""
    if isinstance(x, dict):
        x = x.values()
    for y in x:
        if isinstance(y, datetime):
            return False
        if isinstance(y, list):
            return False
        if isinstance(y, dict):
            return False
        if isinstance(y, plistlib.Data):
            return False
        if isinstance(y, bytes):
            try:
                y.decode('utf-8')
            except UnicodeDecodeError:
                return False
    return True


async def to_str(x: AnyStr) -> str:
    """Convert a value to a string for shell."""
    if isinstance(x, bytes):
        return x.decode('utf-8')
    ret = str(x)
    if ret == 'True':
        return 'true'
    if ret == 'False':
        return 'false'
    return ret
