from datetime import datetime
from typing import Any, Dict, Mapping, List, Sequence, Union
import plistlib

__all__ = (
    'ComplexInnerTypes',
    'PlistList',
    'PlistRoot',
    'PlistValue',
)

ComplexInnerTypes = Union[Sequence[Any], Mapping[str, Any], bytes]
PlistValue = Union[plistlib.Data, Mapping[str, Any], Sequence[Any], bool, int,
                   float, str, datetime, bytes]
PlistList = Sequence[PlistValue]
PlistRoot = Mapping[str, PlistValue]

MutablePlistValue = Union[plistlib.Data, Dict[str, Any], List[Any], bool, int,
                          float, str, datetime, bytes]
MutablePlistList = List[MutablePlistValue]
MutablePlistRoot = Dict[str, MutablePlistValue]
