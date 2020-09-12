from datetime import datetime
from typing import Any, Dict, List, Union
import plistlib

__all__ = (
    'NonSimpleInnerTypes',
    'PlistList',
    'PlistRoot',
    'PlistValue',
)

NonSimpleInnerTypes = Union[List[Any], Dict[str, Any], bytes]
PlistValue = Union[plistlib.Data, Dict[str, Any], List[Any], bool, int, float,
                   str, datetime, bytes]
PlistList = List[PlistValue]
PlistRoot = Dict[str, PlistValue]
