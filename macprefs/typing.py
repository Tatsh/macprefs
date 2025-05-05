from __future__ import annotations

from collections.abc import Mapping, Sequence, ValuesView
from datetime import datetime
from typing import Any, TypeAlias

__all__ = ('ComplexInnerTypes', 'PlistList', 'PlistRoot', 'PlistValue', 'SimpleArg')

ComplexInnerTypes: TypeAlias = list[Any] | Mapping[str, Any] | bytes
"""Non-scalar inner types of a property list."""
PlistValue: TypeAlias = Mapping[str, Any] | list[Any] | bool | int | float | str | datetime | bytes
"""Value inside a property list."""
PlistList: TypeAlias = Sequence[PlistValue]
"""List inside a property list."""
PlistRoot: TypeAlias = Mapping[str, PlistValue]
"""Root of a dictionary."""

SimpleArg: TypeAlias = Mapping[Any,
                               ComplexInnerTypes] | Sequence[ComplexInnerTypes] | ValuesView[str]
