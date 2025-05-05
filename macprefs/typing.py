from __future__ import annotations

from collections.abc import Mapping, Sequence, ValuesView
from datetime import datetime
from typing import Any, TypeAlias

__all__ = ('ComplexInnerTypes', 'MutablePlistList', 'MutablePlistRoot', 'MutablePlistValue',
           'PlistList', 'PlistRoot', 'PlistValue', 'SimpleArg')

ComplexInnerTypes: TypeAlias = list[Any] | Mapping[str, Any] | bytes
PlistValue: TypeAlias = Mapping[str, Any] | list[Any] | bool | int | float | str | datetime | bytes
"""Value inside a property list."""
PlistList: TypeAlias = Sequence[PlistValue]
"""List inside a property list."""
PlistRoot: TypeAlias = Mapping[str, PlistValue]
"""Root of a dictionary."""

MutablePlistValue: TypeAlias = dict[str,
                                    Any] | list[Any] | bool | int | float | str | datetime | bytes
"""Mutable value inside a property list."""
MutablePlistList: TypeAlias = list[MutablePlistValue]
"""Mutable list inside a property list."""
MutablePlistRoot: TypeAlias = dict[str, MutablePlistValue]
"""Mutable root of a dictionary."""

SimpleArg: TypeAlias = Mapping[Any,
                               ComplexInnerTypes] | Sequence[ComplexInnerTypes] | ValuesView[str]
