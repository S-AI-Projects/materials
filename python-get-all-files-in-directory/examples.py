"""
Python Get All Files in Directory - Examples and Specifications.

Source Contract & Preconditions:
- Line 1: `import pathlib`
  All file system path interactions use `pathlib.Path`.
- Line 64 (Source Fixture / Data Anchor):
  `SKIP_DIRS = ["temp", "temporary_files", "logs"]`
  Establishes default list of junk directory names to exclude during traversal.
- Line 71: `large_dir.rglob("*")`
  Traverses items recursively within a directory hierarchy.
- Line 72: `if set(item.parts).isdisjoint(SKIP_DIRS):`
  Precondition for file retention: An item is included if and only if its path parts
  do not intersect with any directory name in SKIP_DIRS.
- Line 76-82:
  `[item for item in large_dir.rglob("*") if set(item.parts).isdisjoint(SKIP_DIRS)]`
  Comprehension accumulating retained Path objects while preserving order.
"""

import pathlib
from pprint import pp

try:
    from . import skip_dirs
except (ImportError, ValueError):
    import skip_dirs

# OPTING OUT OF JUNK DIRECTORIES - Default anchor
SKIP_DIRS = ["temp", "temporary_files", "logs"]


def filter_skip_dirs(paths, skip_dirs=None):
    """Filter an iterable of Path items, opting out of junk directories.

    Contract:
    - Precondition: `set(item.parts).isdisjoint(skip_dirs)` (Line 72)
    - Output: List of pathlib.Path objects whose parts do not contain any excluded directory.
    - Preserves input order, shape, and does not mutate the input iterable.
    """
    if skip_dirs is None:
        skip_dirs = SKIP_DIRS
    skip_set = set(skip_dirs)
    return [item for item in paths if set(item.parts).isdisjoint(skip_set)]


def get_all_files(root="Desktop", pattern="*", skip_dirs=None):
    """Recursively list all items in root opting out of junk directories.

    Preserves supported behavior from Line 28 (.rglob("*")) and Line 72 (exclusion).
    """
    root_path = pathlib.Path(root)
    if not root_path.exists():
        return []
    return filter_skip_dirs(root_path.rglob(pattern), skip_dirs=skip_dirs)


def main():
    base_dir = pathlib.Path(__file__).resolve().parent
    desktop = base_dir / "Desktop"

    if desktop.exists():
        ############################################
        # GETTING A LIST OF FILES AND DIRECTORIES
        ############################################

        # Basic listing using .iterdir()
        pp(list(desktop.iterdir()))

        # Iteration to filter or process
        for item in desktop.iterdir():
            print(f"{item} - {'dir' if item.is_dir() else 'file'}")

        # Usage in a comprehension
        pp([item for item in desktop.iterdir() if item.is_dir()])

        ############################################
        # RECURSIVELY LIST WITH GLOBS
        ############################################

        # Recursively list with glob (both lines are equivalent)
        pp(list(desktop.rglob("*")))
        pp(list(desktop.glob("**/*")))

        ############################################
        # CONDITIONAL LISTING WITH GLOBS
        ############################################

        # Conditional listing using glob patterns
        pp(list(desktop.glob("*")))  # Does not recurse
        pp(list(desktop.glob("real*")))
        pp(list(desktop.glob("*.txt")))

        # Conditional recursive listing
        pp(list(desktop.rglob("*.py")))  # Equivalent to .glob("**/*.py")
        pp(list(desktop.glob("**/*.py")))  # Equivalent to .rglob("*.py")

        # More complex filtering

        # With a for loop
        for item in desktop.rglob("*"):
            if item.is_file():
                print(item)

        # With comprehensions
        pp([file for file in desktop.rglob("*") if file.suffix in [".py", ".md"]])
        pp([file for file in desktop.rglob("*") if file.is_dir()])

        # With the filter() function
        pp([list(filter(lambda item: item.is_file(), desktop.rglob("*")))])

    ############################################
    # OPTING OUT OF JUNK DIRECTORIES
    ############################################

    large_dir = base_dir / "large_dir"
    if large_dir.exists():
        # With a for loop
        for item in large_dir.rglob("*"):
            if set(item.parts).isdisjoint(SKIP_DIRS):
                print(item)

        # With a comprehension
        pp(
            [
                item
                for item in large_dir.rglob("*")
                if set(item.parts).isdisjoint(SKIP_DIRS)
            ]
        )

        # With filter()
        pp(
            list(
                filter(
                    lambda item: set(item.parts).isdisjoint(SKIP_DIRS),
                    large_dir.rglob("*"),
                )
            )
        )

        ############################################
        # RECURSIVE ITERDIR
        ############################################

        pp(list(skip_dirs.get_all_items(large_dir)))


if __name__ == "__main__":
    main()
