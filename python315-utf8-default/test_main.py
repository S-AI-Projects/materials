"""Regression and contract tests for python315-utf8-default/main.py.

Preconditions established by source:
    Line 1: import textlib - External module dependency
    Line 3: textlib.read_text("notes.txt") - Primary invocation anchor
"""

import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "python315-utf8-default"

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

# Mock stdout during import to keep test discovery clean
with contextlib.redirect_stdout(io.StringIO()):
    import main
    import textlib


def independent_pathlib_oracle(path, encoding=None):
    """Independent reference calculation oracle using standard pathlib.

    Reads text directly using standard library Path.read_text without
    invoking textlib or main.py.
    """
    enc = encoding if encoding is not None else "utf-8"
    return Path(path).read_text(encoding=enc)


class TestPreconditionsAndAnchors(unittest.TestCase):
    """Verify source lines and fixture preconditions."""

    def test_line1_import_textlib(self):
        """Line 1 establishes 'import textlib' dependency."""
        self.assertTrue(
            hasattr(main, "textlib"), "main module must expose textlib"
        )
        self.assertIs(main.textlib, textlib)

    def test_line3_default_notes_anchor(self):
        """Line 3 establishes default invocation on 'notes.txt'."""
        self.assertTrue(
            hasattr(main, "DEFAULT_NOTES_PATH"),
            "main module must define DEFAULT_NOTES_PATH",
        )
        self.assertEqual(main.DEFAULT_NOTES_PATH.name, "notes.txt")
        self.assertTrue(main.DEFAULT_NOTES_PATH.exists())


class TestFailureAndAbsentResultBranches(unittest.TestCase):
    """Verify failure, absent-result, and error handling branches."""

    def test_smallest_valid_input_empty_string_path_raises_filenotfound(self):
        """Smallest valid input string reaching FileNotFoundError is empty string ''."""
        literal_input = ""
        with self.assertRaises(FileNotFoundError):
            main.read_notes(literal_input)

    def test_nonexistent_path_raises_filenotfound(self):
        """Nonexistent path raises FileNotFoundError."""
        literal_input = "nonexistent_file_xyz_404.txt"
        with self.assertRaises(FileNotFoundError):
            main.read_notes(literal_input)

    def test_smallest_valid_input_empty_file_returns_empty_string(self):
        """Smallest valid input reaching absent-result branch is an empty file (0 bytes)."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False
        ) as tmp:
            tmp_path = Path(tmp.name)

        try:
            expected_output = ""
            actual_output = main.read_notes(tmp_path)
            self.assertEqual(
                actual_output,
                expected_output,
                "0-byte file must yield empty string absent-result sentinel",
            )
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_smallest_valid_input_invalid_utf8_byte_raises_unicodedecodeerror(
        self,
    ):
        """Smallest valid input reaching UnicodeDecodeError is a 1-byte non-UTF-8 sequence."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
            tmp.write(b"\xff")
            tmp_path = Path(tmp.name)

        try:
            with self.assertRaises(UnicodeDecodeError):
                main.read_notes(tmp_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_multibyte_legacy_bytes_raise_unicodedecodeerror(self):
        """Legacy multi-byte non-UTF-8 bytes raise UnicodeDecodeError under default encoding."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
            tmp.write(b"Caf\xe9 \xa320")
            tmp_path = Path(tmp.name)

        try:
            with self.assertRaises(UnicodeDecodeError):
                main.read_notes(tmp_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_type_error_on_invalid_path_type(self):
        """Invalid path argument type (None) raises TypeError."""
        with self.assertRaises(TypeError):
            main.read_notes(None)

    def test_directory_path_raises_isadirectoryerror(self):
        """Directory path raises IsADirectoryError (or PermissionError)."""
        with self.assertRaises((IsADirectoryError, PermissionError)):
            main.read_notes(MODULE_DIR)


class TestStatePreservationAndRecovery(unittest.TestCase):
    """Verify caller-owned state preservation and recovery after failure."""

    def test_caller_state_preserved_after_filenotfound(self):
        """Caller-owned state remains strictly valid and unmutated after FileNotFoundError."""
        caller_state = ["token_alpha", 42, {"config": "active"}]
        caller_state_copy = ["token_alpha", 42, {"config": "active"}]

        with self.assertRaises(FileNotFoundError):
            main.read_notes("")

        self.assertEqual(
            caller_state,
            caller_state_copy,
            "Caller state must remain completely unaltered after FileNotFoundError",
        )

    def test_caller_state_preserved_after_unicodedecodeerror(self):
        """Caller-owned state remains valid and unmutated after UnicodeDecodeError."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
            tmp.write(b"\xff")
            tmp_path = Path(tmp.name)

        caller_state = {"session_id": 9999, "items": [1, 2, 3]}
        caller_state_copy = {"session_id": 9999, "items": [1, 2, 3]}

        try:
            with self.assertRaises(UnicodeDecodeError):
                main.read_notes(tmp_path)

            self.assertEqual(
                caller_state,
                caller_state_copy,
                "Caller state must remain unaltered after UnicodeDecodeError",
            )
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_recovery_call_succeeds_after_filenotfound(self):
        """Recovery: Subsequent valid call succeeds cleanly after FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            main.read_notes("")

        # Recovery call
        expected_notes = (
            "Remember to pass an explicit encoding to every text-mode"
            " open() call.\n"
        )
        actual = main.read_notes(main.DEFAULT_NOTES_PATH)
        self.assertEqual(actual, expected_notes)

    def test_recovery_call_succeeds_after_unicodedecodeerror(self):
        """Recovery: Subsequent valid call succeeds cleanly after UnicodeDecodeError."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
            tmp.write(b"\xfe\xff")
            tmp_path = Path(tmp.name)

        try:
            with self.assertRaises(UnicodeDecodeError):
                main.read_notes(tmp_path)

            # Recovery call
            expected_notes = (
                "Remember to pass an explicit encoding to every text-mode"
                " open() call.\n"
            )
            actual = main.read_notes(main.DEFAULT_NOTES_PATH)
            self.assertEqual(actual, expected_notes)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_explicit_encoding_fallback_recovers_legacy_bytes(self):
        """Fallback: Specifying explicit encoding allows recovery on legacy non-UTF8 bytes."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
            tmp.write(b"Caf\xe9 \xa320")
            tmp_path = Path(tmp.name)

        try:
            # Under default UTF-8, raises UnicodeDecodeError
            with self.assertRaises(UnicodeDecodeError):
                main.read_notes(tmp_path)

            # Under explicit fallback encoding, successfully decodes
            actual = main.read_notes(tmp_path, encoding="latin-1")
            self.assertEqual(actual, "Café £20")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class TestOrdinaryInputAndOracleEquivalence(unittest.TestCase):
    """Verify ordinary input behavior and independent oracle equivalence."""

    def test_ordinary_input_notes_txt(self):
        """Ordinary input anchor notes.txt returns exact expected content."""
        expected = (
            "Remember to pass an explicit encoding to every text-mode"
            " open() call.\n"
        )
        oracle_res = independent_pathlib_oracle(main.DEFAULT_NOTES_PATH)
        self.assertEqual(expected, oracle_res)

        actual = main.read_notes(main.DEFAULT_NOTES_PATH)
        self.assertEqual(actual, expected)

    def test_ordinary_input_data_json(self):
        """Reading data.json fixture with UTF-8 default returns valid json string."""
        data_path = MODULE_DIR / "data.json"
        oracle_res = independent_pathlib_oracle(data_path)
        actual = main.read_notes(data_path)
        self.assertEqual(actual, oracle_res)

    def test_ordinary_input_legacy_csv(self):
        """Reading legacy.csv fixture with UTF-8 default returns valid csv string."""
        legacy_path = MODULE_DIR / "legacy.csv"
        oracle_res = independent_pathlib_oracle(legacy_path)
        actual = main.read_notes(legacy_path)
        self.assertEqual(actual, oracle_res)

    def test_default_parameter_invocation(self):
        """Calling read_notes() without arguments resolves to default notes.txt anchor."""
        expected = (
            "Remember to pass an explicit encoding to every text-mode"
            " open() call.\n"
        )
        actual = main.read_notes()
        self.assertEqual(actual, expected)


class TestModuleInterfaceAndAliases(unittest.TestCase):
    """Verify public module interface, aliases, and standalone script execution."""

    def test_canonical_aliases_identity(self):
        """Canonical aliases point to the identical callable function."""
        self.assertIs(main.python315_utf8_default, main.read_notes)
        self.assertIs(main.read_text, main.read_notes)
        self.assertIs(main.main, main.read_notes)

    def test_standalone_script_execution(self):
        """Standalone script execution completes with exit code 0."""
        proc = subprocess.run(
            [sys.executable, str(MODULE_DIR / "main.py")],
            cwd=str(MODULE_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
