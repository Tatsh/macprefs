from copy import deepcopy
import plistlib

from .mp_typing import PlistList, PlistRoot

__all__ = (
    'remove_data_fields',
    'remove_data_fields_list',
)


async def remove_data_fields_list(pl_list: PlistList) -> PlistList:
    """Clean up data fields from a PlistList."""
    ret = deepcopy(pl_list)
    index = 0
    for value in pl_list:
        if not isinstance(value, plistlib.Data):
            if isinstance(value, dict):
                ret[index] = await remove_data_fields(value)
            elif isinstance(value, list):
                ret[index] = await remove_data_fields_list(value)
            if ((isinstance(value, list) or isinstance(value, dict))
                    and not ret[index]):
                del ret[index]
            index = max(0, index - 1)
            continue
        del ret[index]
        index = max(0, index - 1)
    return ret


async def remove_data_fields(root: PlistRoot) -> PlistRoot:
    """Clean up data fields from a PlistRoot."""
    ret = deepcopy(root)
    for key, value in root.items():
        if not isinstance(value, plistlib.Data):
            if isinstance(value, list):
                ret[key] = await remove_data_fields_list(value)
            elif isinstance(value, dict):
                ret[key] = await remove_data_fields(value)
            if isinstance(value, (list, dict, set)) and not ret[key]:
                del ret[key]
            continue
        del ret[key]
    return ret
