from diffcheck.lock import FileName
from diffcheck.local import LocalContentLockStore
from diffcheck.remote import RemoteContentLockStore
from dataclasses import dataclass, field
from typing import Dict, Any, List, TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')

@dataclass
class DictDifferences(Generic[K, V]):
    new_keys: List[K] = field(default_factory=list)
    updated_keys: List[K] = field(default_factory=list)
    deleted_keys: List[K] = field(default_factory=list)

def get_dict_differences(dict1: Dict[K, V], dict2: Dict[K, V]) -> DictDifferences[K, V]:
    differences = DictDifferences[K, V]()

    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    differences.new_keys = list(keys2 - keys1)
    differences.deleted_keys = list(keys1 - keys2)

    common_keys = keys1.intersection(keys2)

    for key in common_keys:
        if dict1[key] != dict2[key]:
            differences.updated_keys.append(key)

    return differences


async def get_local_remote_diff():
    """
    Get the list of files that are in the local lock but not in the remote lock.
    """
    local_store = LocalContentLockStore()
    remote_store = RemoteContentLockStore()

    local_lock = local_store.get()
    remote_lock = await remote_store.get()

    return get_dict_differences(local_lock, remote_lock)


