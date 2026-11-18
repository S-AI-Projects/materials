"""Names dataset and recursive traversal functions.

Preconditions established in source:
- Line 14: names = [...] nested hierarchy definition
- Line 15: "Adam" (first top-level leaf item)
- Line 17: "Bob" (nested list lead item)
- Line 19: "Chet", "Cat" (deeply nested leaves)
- Total leaf items in fixture: 10
"""

from typing import Any, List, Optional, Union

# Source fixture anchor
names = [
    "Adam",
    [
        "Bob",
        [
            "Chet",
            "Cat",
        ],
        "Barb",
        "Bert",
    ],
    "Alex",
    [
        "Bea",
        "Bill",
    ],
    "Ann",
]

# Documented Absent-Result Sentinel
ABSENT_SENTINEL = None


def find_name(target: str, item_list: Optional[Any] = None) -> Optional[str]:
    """Recursively search for a target name in nested item_list.

    Failure & Absent-Result Contract:
    - Success: Returns the found name string.
    - Absent-result sentinel: Returns ABSENT_SENTINEL (None) if the name is not in the tree.
    - Valid empty boundary: item_list=[] returns ABSENT_SENTINEL (None).
    - Failure branch: Non-list/non-string item_list raises TypeError.
    """
    if item_list is None:
        item_list = names

    if not isinstance(item_list, list):
        raise TypeError(f"item_list must be a list, got {type(item_list).__name__}")
    if not isinstance(target, str):
        raise TypeError(f"target must be a string, got {type(target).__name__}")

    for item in item_list:
        if isinstance(item, list):
            res = find_name(target, item)
            if res is not None:
                return res
        elif item == target:
            return item

    return ABSENT_SENTINEL


def count_names(item_list: Optional[Any] = None) -> int:
    """Recursively count leaf name items in nested item_list.

    Failure & Domain Contract:
    - Empty boundary: [] returns 0.
    - Valid fixture names: returns 10.
    - Failure branch: Non-list item_list raises TypeError.
    """
    if item_list is None:
        item_list = names

    if not isinstance(item_list, list):
        raise TypeError(f"item_list must be a list, got {type(item_list).__name__}")

    count = 0
    for item in item_list:
        if isinstance(item, list):
            count += count_names(item)
        else:
            count += 1
    return count
