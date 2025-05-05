from __future__ import annotations

from collections.abc import Mapping, Sequence, ValuesView
from datetime import datetime
from typing import Any

__all__ = ('ComplexInnerTypes', 'MutablePlistList', 'MutablePlistRoot', 'MutablePlistValue',
           'PlistList', 'PlistRoot', 'PlistValue', 'SimpleArg')

ComplexInnerTypes = list[Any] | Mapping[str, Any] | bytes
PlistValue = Mapping[str, Any] | list[Any] | bool | int | float | str | datetime | bytes
PlistList = Sequence[PlistValue]
PlistRoot = Mapping[str, PlistValue]

MutablePlistValue = dict[str, Any] | list[Any] | bool | int | float | str | datetime | bytes
MutablePlistList = list[MutablePlistValue]
MutablePlistRoot = dict[str, MutablePlistValue]

SimpleArg = Mapping[Any, ComplexInnerTypes] | Sequence[ComplexInnerTypes] | ValuesView[str]
