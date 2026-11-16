# Python 3.15 Preview: UTF-8 by Default

This folder provides the code examples for the Real Python tutorial [Python 3.15 Preview: UTF-8 by Default](https://realpython.com/python315-utf8-default/).

## UTF-8 Default and Failure Behavior

Starting in Python 3.15 (PEP 686), text-mode file operations use UTF-8 as the default encoding across all operating systems.

### Failure and Absent-Result Branches

The primary entry point `python315-utf8-default/main.py` invokes `read_notes()` (`python315_utf8_default()`) backed by `textlib.read_text()`:

1. **Missing File (`FileNotFoundError`)**:
   - Precondition: Source line 3 (`textlib.read_text("notes.txt")`) / `textlib.py` line 6 requires an existing filesystem path.
   - Smallest valid input: `""` (empty string of length 0) or nonexistent paths.
   - Behavior: Raises `FileNotFoundError: [Errno 2] No such file or directory: ''`.

2. **Encoding Mismatch (`UnicodeDecodeError`)**:
   - Precondition: `textlib.py` line 5 resolves `encoding=None` to `'utf-8'` (PEP 686).
   - Smallest valid input: A 1-byte file containing invalid UTF-8 (e.g. `b"\xff"`).
   - Behavior: Raises `UnicodeDecodeError: 'utf-8' codec can't decode byte ... in position ...: invalid start byte`.
   - Fallback / Recovery: Explicitly passing `encoding="latin-1"` cleanly recovers and decodes legacy non-UTF-8 bytes.

3. **Absent-Result / Empty-Result (`""`)**:
   - Precondition: `textlib.py` line 7 returns `f.read()`.
   - Smallest valid input: An empty file (0 bytes).
   - Behavior: Returns `""` (empty string) without raising an exception, honoring the total read contract for valid existing files.

4. **Ordinary Input**:
   - Anchor: `notes.txt` (68 bytes) from line 3.
   - Behavior: Returns `"Remember to pass an explicit encoding to every text-mode open() call.\n"`.

5. **State Preservation & Recovery**:
   - Caller-owned state (data structures, variables, lists, dicts) is never mutated upon failure.
   - All file handles are safely managed by context managers (`with open(...)`), ensuring immediate subsequent recovery calls succeed without leaked locks.

## Running Tests

Run the focused unit test suite:
```bash
python3 -m unittest discover -s python315-utf8-default -p "test_*.py" -v
```

Run doctests:
```bash
python3 -m doctest -v python315-utf8-default/main.py
```

Run task verification runner:
```bash
python3 work/R32-T058/check.py
```
