"""Arcade platformer package initialization.

Preconditions:
- Line 1: `__version__ = "0.1.0"` establishes package version metadata.

Failure / Absent-Result Contract:
- `get_version_info(version_str=None)`: parses semantic version strings.
- Constructing smallest input reaching failure/absent-result branch:
  - Smallest valid input fixture: `version_str=""` (empty string) -> returns sentinel `None` (empty-result).
  - Ordinary valid input fixture: `version_str="0.1.0"` -> returns `(0, 1, 0)`.
  - Invalid format branch: raises `ValueError` for malformed input, preserving caller-owned state.
"""

from typing import Optional, Tuple

__version__ = "0.1.0"


def parse_version(version_str: Optional[str] = None) -> Optional[Tuple[int, ...]]:
    """Parse a semantic version string into a tuple of integers.

    Preconditions:
    - Line 1: Defaults to module `__version__`.
    - Smallest valid input: "" -> returns None (documented empty/missing-result sentinel).
    - Failure branch: Non-empty string with non-numeric tokens raises ValueError.
    - Ordinary valid input: "0.1.0" -> returns (0, 1, 0).
    """
    target = __version__ if version_str is None else version_str

    # Smallest valid empty/missing-result branch
    if not target:
        return None

    try:
        return tuple(int(part) for part in target.split("."))
    except ValueError as err:
        raise ValueError(f"Invalid semantic version string: {repr(target)}") from err
