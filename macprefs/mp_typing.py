from datetime import datetime
from typing import Any, Mapping, Sequence

__all__ = ('ComplexInnerTypes', 'MutablePlistList', 'MutablePlistRoot', 'MutablePlistValue',
           'PlistList', 'PlistRoot', 'PlistValue')

ComplexInnerTypes = list[Any] | Mapping[str, Any] | bytes
PlistValue = Mapping[str, Any] | list[Any] | bool | int | float | str | datetime | bytes
PlistList = Sequence[PlistValue]
PlistRoot = Mapping[str, PlistValue]

MutablePlistValue = dict[str, Any] | list[Any] | bool | int | float | str | datetime | bytes
MutablePlistList = list[MutablePlistValue]
MutablePlistRoot = dict[str, MutablePlistValue]
