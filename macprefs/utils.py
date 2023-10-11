from collections.abc import ValuesView
from datetime import datetime
from typing import TYPE_CHECKING, Any, AnyStr, Mapping, Sequence
import logging
import sys

from loguru import logger

from .mp_typing import ComplexInnerTypes

if TYPE_CHECKING:
    from types import FrameType

__all__ = ('is_simple', 'setup_logging', 'to_str')


class InterceptHandler(logging.Handler):  # pragma: no cover
    """Intercept handler taken from Loguru's documentation."""
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # Find caller from where originated the logged message
        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_log_intercept_handler() -> None:  # pragma: no cover
    """Sets up Loguru to intercept records from the logging module."""
    logging.basicConfig(handlers=(InterceptHandler(),), level=0)


def setup_logging(debug: bool | None = False) -> None:
    """Shared function to enable logging."""
    if debug:  # pragma: no cover
        setup_log_intercept_handler()
        logger.enable('')
    else:
        logger.configure(handlers=(dict(
            format='<level>{message}</level>',
            level='INFO',
            sink=sys.stderr,
        ),))


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


def to_str(x: AnyStr) -> str:
    """Convert a value to a string for shell."""
    if isinstance(x, bytes):
        try:
            return x.decode('utf-8')
        except UnicodeDecodeError:
            return ''.join(hex(y)[2:] for y in x)
    ret = str(x)
    return ret.lower() if ret in ('True', 'False') else ret
