"""Python 3.15 UTF-8 Default Demonstration Module.

Demonstrates UTF-8 as the default text encoding under Python 3.15 (PEP 686).
Exercises both documented failure behaviors (FileNotFoundError, UnicodeDecodeError)
and absent-result/empty-result behaviors when reading text files with textlib.

Preconditions established by source:
    Line 1: import textlib
    Line 3: textlib.read_text("notes.txt")
"""

from pathlib import Path
import textlib

# Module path anchor established from line 3 ("notes.txt")
DEFAULT_NOTES_PATH = Path(__file__).resolve().parent / "notes.txt"


def read_notes(path=DEFAULT_NOTES_PATH, encoding=None):
    """Read text from file using textlib with Python 3.15 UTF-8 default encoding.

    Preconditions established by source:
        Line 1: import textlib - External module dependency.
        Line 3: textlib.read_text("notes.txt") - Primary invocation anchor.

    Failure & absent-result behaviors:
        - FileNotFoundError: When `path` is missing or empty (e.g. `""`).
        - UnicodeDecodeError: When `path` contains non-UTF-8 bytes under default encoding.
        - Empty result (""): When `path` points to an empty file (0 bytes).

    Representative examples:
        >>> res = read_notes()
        >>> res.startswith("Remember to pass an explicit encoding")
        True
        >>> try:
        ...     read_notes("")
        ... except FileNotFoundError:
        ...     "Caught FileNotFoundError"
        'Caught FileNotFoundError'

    Args:
        path: Path-like or string pointing to the target file. Defaults to DEFAULT_NOTES_PATH.
        encoding: Text encoding name, or None for Python 3.15 default (UTF-8).

    Returns:
        str: Decoded content of the file.
    """
    return textlib.read_text(path, encoding=encoding)


# Canonical aliases
python315_utf8_default = read_notes
read_text = read_notes
main = read_notes

if __name__ == "__main__":
    # Preserve original script execution behavior: reads notes.txt via textlib
    read_notes(
        "notes.txt" if Path("notes.txt").exists() else DEFAULT_NOTES_PATH
    )
