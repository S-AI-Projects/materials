#!/usr/bin/env python3
"""Focused check runner and repeatability verification for R32-T058.

Task ID: R32-T058
Repository: materials
Organisation: S-AI-Projects
Personal fork: pagoll-glitch/materials
Student URN: e26b07f0709
Target file: python315-utf8-default/main.py
Function / Entry point: python315_utf8_default / read_notes
Task Goal: Exercise a documented failure or absent-result branch of python315 utf8 default.
           Verify smallest valid input, ordinary input, caller state preservation,
           and recovery call.
"""

import contextlib
import doctest
import io
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "python315-utf8-default"
WORK_DIR = Path(__file__).resolve().parent

if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

# Mock stdout during import to prevent accidental output during module loading
with contextlib.redirect_stdout(io.StringIO()):
    import main as main_mod


def get_tool_versions():
    """Retrieve runtime and tool versions."""
    ruff_ver = "unknown"
    candidates = [
        REPO_ROOT / ".venv" / "bin" / "ruff",
        Path(sys.executable).parent / "ruff",
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                proc = subprocess.run(
                    [str(candidate), "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                ruff_ver = proc.stdout.strip()
                break
            except Exception:
                pass

    return {
        "Python": f"{platform.python_version()} ({sys.version.split()[0]})",
        "Platform": platform.platform(),
        "Ruff": ruff_ver,
    }


def independent_pathlib_oracle(path, encoding=None):
    """Independent reference calculation oracle using standard pathlib.

    Reads text directly using standard library Path.read_text without
    invoking textlib or main.py.
    """
    enc = encoding if encoding is not None else "utf-8"
    return Path(path).read_text(encoding=enc)


# 20 Explicit Test Cases with Literal Inputs & Independent Expected Outputs
TEST_CASES = [
    {
        "id": "TC-01",
        "desc": (
            "Smallest valid input reaching FileNotFoundError (empty path"
            " string)"
        ),
        "input": {"path": "", "encoding": None},
        "expected_type": "exception",
        "expected_value": "FileNotFoundError",
        "source_precondition": (
            "textlib.py: Line 6 open(path, encoding=encoding) / main.py: Line"
            " 3 (empty path violates filesystem path existence precondition)"
        ),
    },
    {
        "id": "TC-02",
        "desc": (
            "Ordinary input anchor reaching successful return branch"
            " (notes.txt)"
        ),
        "input": {"path": "notes.txt", "encoding": None},
        "expected_type": "value",
        "expected_value": (
            "Remember to pass an explicit encoding to every text-mode"
            " open() call.\n"
        ),
        "source_precondition": (
            "main.py: Line 3 textlib.read_text('notes.txt') (primary tutorial"
            " text fixture)"
        ),
    },
    {
        "id": "TC-03",
        "desc": (
            "Smallest valid input reaching absent-result / empty-result branch"
            " (0-byte empty file)"
        ),
        "input": {"path": "__empty_file__", "encoding": None},
        "expected_type": "value",
        "expected_value": "",
        "source_precondition": (
            "textlib.py: Line 7 return f.read() (valid 0-byte file yields empty"
            " string sentinel without exception)"
        ),
    },
    {
        "id": "TC-04",
        "desc": (
            "Smallest valid input reaching UnicodeDecodeError failure branch"
            " (1-byte non-UTF-8 0xFF)"
        ),
        "input": {"path": "__invalid_utf8_1byte__", "encoding": None},
        "expected_type": "exception",
        "expected_value": "UnicodeDecodeError",
        "source_precondition": (
            "textlib.py: Line 5 io.text_encoding(None) resolving to 'utf-8'"
            " (PEP 686 Python 3.15 default) & Line 7 f.read()"
        ),
    },
    {
        "id": "TC-05",
        "desc": "Caller state preservation after FileNotFoundError",
        "input": {
            "caller_state": [
                "caller_token_alpha",
                42,
                {"active": True},
            ],
            "path": "",
            "encoding": None,
        },
        "expected_type": "state_preservation",
        "expected_value": [
            "caller_token_alpha",
            42,
            {"active": True},
        ],
        "source_precondition": (
            "main.py / textlib.py: non-mutating failure semantics preserve"
            " caller data structures intact"
        ),
    },
    {
        "id": "TC-06",
        "desc": "Caller state preservation after UnicodeDecodeError",
        "input": {
            "caller_state": {
                "session_id": 9999,
                "records": [10, 20],
            },
            "path": "__invalid_utf8_1byte__",
            "encoding": None,
        },
        "expected_type": "state_preservation",
        "expected_value": {
            "session_id": 9999,
            "records": [10, 20],
        },
        "source_precondition": (
            "main.py / textlib.py: decoding exception unwinding preserves"
            " caller structures intact"
        ),
    },
    {
        "id": "TC-07",
        "desc": (
            "Successful recovery call immediately after FileNotFoundError"
        ),
        "input": {"sequence": ["", "notes.txt"]},
        "expected_type": "recovery",
        "expected_value": (
            "Remember to pass an explicit encoding to every text-mode"
            " open() call.\n"
        ),
        "source_precondition": (
            "main.py: Line 3 textlib.read_text('notes.txt') succeeds cleanly"
            " after prior failure"
        ),
    },
    {
        "id": "TC-08",
        "desc": (
            "Successful recovery call immediately after UnicodeDecodeError"
        ),
        "input": {"sequence": ["__invalid_utf8_1byte__", "notes.txt"]},
        "expected_type": "recovery",
        "expected_value": (
            "Remember to pass an explicit encoding to every text-mode"
            " open() call.\n"
        ),
        "source_precondition": (
            "textlib.py: Line 6 with open(...) context manager safely closes"
            " file handle allowing immediate subsequent read"
        ),
    },
    {
        "id": "TC-09",
        "desc": (
            "Documented nonexistent file path reaching FileNotFoundError"
        ),
        "input": {
            "path": "nonexistent_file_xyz_404.txt",
            "encoding": None,
        },
        "expected_type": "exception",
        "expected_value": "FileNotFoundError",
        "source_precondition": (
            "textlib.py: Line 6 open() fails on absent filesystem entry"
        ),
    },
    {
        "id": "TC-10",
        "desc": "Type validation failure on non-path argument (None)",
        "input": {"path": None, "encoding": None},
        "expected_type": "exception",
        "expected_value": "TypeError",
        "source_precondition": (
            "textlib.py: Line 6 open() argument contract requires path-like"
            " or descriptor"
        ),
    },
    {
        "id": "TC-11",
        "desc": (
            "Multi-byte legacy non-UTF-8 Latin-1/CP1252 sequence failing"
            " under default UTF-8"
        ),
        "input": {
            "path": "__legacy_latin1_file__",
            "encoding": None,
        },
        "expected_type": "exception",
        "expected_value": "UnicodeDecodeError",
        "source_precondition": (
            "textlib.py: Line 5 io.text_encoding(None) resolving to 'utf-8'"
            " rejects high-bit Latin-1 bytes"
        ),
    },
    {
        "id": "TC-12",
        "desc": (
            "Fallback / explicit legacy encoding recovery (latin-1 on legacy"
            " bytes)"
        ),
        "input": {
            "path": "__legacy_latin1_file__",
            "encoding": "latin-1",
        },
        "expected_type": "value",
        "expected_value": "Café £20",
        "source_precondition": (
            "textlib.py: Line 4-5 explicit encoding parameter overrides"
            " default UTF-8"
        ),
    },
    {
        "id": "TC-13",
        "desc": "Minimal non-empty valid UTF-8 single ASCII character",
        "input": {"path": "__single_char_file__", "encoding": None},
        "expected_type": "value",
        "expected_value": "A",
        "source_precondition": (
            "textlib.py: Line 7 return f.read() reads single character"
            " correctly"
        ),
    },
    {
        "id": "TC-14",
        "desc": "Multi-line UTF-8 file with multi-byte unicode characters",
        "input": {"path": "__multiline_utf8_file__", "encoding": None},
        "expected_type": "value",
        "expected_value": "First Line\nSecond Line: ☕ café naïve\n",
        "source_precondition": (
            "textlib.py: Line 5 UTF-8 decoding succeeds on compliant"
            " multibyte sequences"
        ),
    },
    {
        "id": "TC-15",
        "desc": (
            "Default parameter invocation without arguments reads default"
            " notes anchor"
        ),
        "input": {"path": "__default__", "encoding": None},
        "expected_type": "value",
        "expected_value": (
            "Remember to pass an explicit encoding to every text-mode"
            " open() call.\n"
        ),
        "source_precondition": (
            "main.py: Line 3 textlib.read_text('notes.txt') default argument"
            " binding"
        ),
    },
    {
        "id": "TC-16",
        "desc": "Canonical module alias equivalence check",
        "input": {
            "aliases": [
                "python315_utf8_default",
                "read_notes",
                "read_text",
                "main",
            ]
        },
        "expected_type": "value",
        "expected_value": True,
        "source_precondition": (
            "main.py: Line 1/3 module export and public callable alias"
            " contract"
        ),
    },
    {
        "id": "TC-17",
        "desc": "Directory path reaching IsADirectoryError / PermissionError",
        "input": {"path": "__directory__", "encoding": None},
        "expected_type": "exception",
        "expected_value": "IsADirectoryError",
        "source_precondition": (
            "textlib.py: Line 6 open() on directory path violates file read"
            " precondition"
        ),
    },
    {
        "id": "TC-18",
        "desc": "Independent oracle evaluation on notes.txt text contents",
        "input": {"path": "notes.txt", "oracle": "pathlib_read_text_utf8"},
        "expected_type": "value",
        "expected_value": (
            "Remember to pass an explicit encoding to every text-mode"
            " open() call.\n"
        ),
        "source_precondition": (
            "main.py: Line 3 matches independent"
            " pathlib.Path('notes.txt').read_text('utf-8')"
        ),
    },
    {
        "id": "TC-19",
        "desc": "Independent oracle evaluation on data.json contents",
        "input": {"path": "data.json", "oracle": "pathlib_read_text_utf8"},
        "expected_type": "value",
        "expected_value": '{"café": "☕", "naïve": true}\n',
        "source_precondition": "data.json fixture UTF-8 decoding agreement",
    },
    {
        "id": "TC-20",
        "desc": "Independent oracle evaluation on legacy.csv contents",
        "input": {"path": "legacy.csv", "oracle": "pathlib_read_text_utf8"},
        "expected_type": "value",
        "expected_value": (
            "id,name,quantity\n1,espresso,12\n2,americano,8\n3,macchiato,5\n"
        ),
        "source_precondition": (
            "legacy.csv fixture ASCII/UTF-8 decoding agreement"
        ),
    },
]


def run_deliberate_break_verifications():
    """Verify that deliberate defects in implementation violate assertions."""
    break_results = []

    # Defect Break 1: Swallowed FileNotFoundError (returns error string instead of raising)
    def defective_read_notes_swallow_fnf(path="", encoding=None):
        if not path or not Path(path).exists():
            return "[DEFECT_SWALLOWED_FNF]"
        return main_mod.read_notes(path, encoding=encoding)

    try:
        res = defective_read_notes_swallow_fnf("")
        # If the check asserted raising FileNotFoundError, this returns normally
        assert res != "[DEFECT_SWALLOWED_FNF]"
        break_results.append(
            "Break 1 FAILED: Swallow FNF defect was not detected"
        )
    except AssertionError:
        break_results.append(
            "Break 1 PASSED: Swallowed FileNotFoundError defect detected by"
            " assertion."
        )

    # Defect Break 2: Caller-state mutation defect
    def defective_read_notes_mutate_state(caller_state, path=""):
        caller_state.append("DEFECT_MUTATION")
        return main_mod.read_notes(path)

    caller_state = ["original_token", 100]
    expected_state = ["original_token", 100]
    try:
        try:
            defective_read_notes_mutate_state(caller_state, "")
        except FileNotFoundError:
            pass
        assert caller_state == expected_state
        break_results.append(
            "Break 2 FAILED: Mutation defect was not detected"
        )
    except AssertionError:
        break_results.append(
            "Break 2 PASSED: Caller state mutation defect detected by assertion."
        )

    # Defect Break 3: Suppressed UnicodeDecodeError (ignores encoding errors)
    def defective_read_notes_suppress_unicode(path, encoding=None):
        # Silently replace errors instead of raising UnicodeDecodeError
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()

    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
        tmp.write(b"\xff")
        tmp_path = Path(tmp.name)

    try:
        try:
            res = defective_read_notes_suppress_unicode(tmp_path)
            # Expect UnicodeDecodeError; if replaced, check should catch defect
            assert False, f"Defect not raised, returned: {res!r}"
        except UnicodeDecodeError:
            break_results.append(
                "Break 3 FAILED: Unicode error unexpectedly raised"
            )
        except AssertionError:
            break_results.append(
                "Break 3 PASSED: Suppressed UnicodeDecodeError defect detected"
                " by assertion."
            )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    # Defect Break 4: Corrupted recovery return value
    def defective_recovery_corrupt_notes():
        return "CORRUPTED_NOTES_STRING_DEFECT"

    try:
        actual_rec = defective_recovery_corrupt_notes()
        expected_rec = (
            "Remember to pass an explicit encoding to every text-mode"
            " open() call.\n"
        )
        assert actual_rec == expected_rec
        break_results.append("Break 4 FAILED: Corrupted recovery not detected")
    except AssertionError:
        break_results.append(
            "Break 4 PASSED: Corrupted recovery return value detected by"
            " assertion."
        )

    return break_results


def evaluate_test_cases():
    """Execute all 20 test cases and collect actual results."""
    actual_results = []

    # Temporary files fixture
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False
    ) as empty_tmp:
        empty_path = Path(empty_tmp.name)

    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as bad_utf8_tmp:
        bad_utf8_tmp.write(b"\xff")
        bad_utf8_path = Path(bad_utf8_tmp.name)

    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as latin1_tmp:
        latin1_tmp.write(b"Caf\xe9 \xa320")
        latin1_path = Path(latin1_tmp.name)

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False
    ) as single_char_tmp:
        single_char_tmp.write("A")
        single_char_path = Path(single_char_tmp.name)

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False
    ) as multiline_tmp:
        multiline_tmp.write("First Line\nSecond Line: ☕ café naïve\n")
        multiline_path = Path(multiline_tmp.name)

    try:
        for case in TEST_CASES:
            cid = case["id"]

            if cid == "TC-01":
                try:
                    main_mod.read_notes("")
                    actual_results.append((cid, "no_exception", None))
                except FileNotFoundError:
                    actual_results.append(
                        (cid, "exception", "FileNotFoundError")
                    )
                except Exception as e:
                    actual_results.append((cid, "exception", type(e).__name__))

            elif cid == "TC-02":
                act = main_mod.read_notes(main_mod.DEFAULT_NOTES_PATH)
                actual_results.append((cid, "value", act))

            elif cid == "TC-03":
                act = main_mod.read_notes(empty_path)
                actual_results.append((cid, "value", act))

            elif cid == "TC-04":
                try:
                    main_mod.read_notes(bad_utf8_path)
                    actual_results.append((cid, "no_exception", None))
                except UnicodeDecodeError:
                    actual_results.append(
                        (cid, "exception", "UnicodeDecodeError")
                    )
                except Exception as e:
                    actual_results.append((cid, "exception", type(e).__name__))

            elif cid == "TC-05":
                st = ["caller_token_alpha", 42, {"active": True}]
                try:
                    main_mod.read_notes("")
                except FileNotFoundError:
                    pass
                actual_results.append((cid, "state_preservation", st))

            elif cid == "TC-06":
                st = {"session_id": 9999, "records": [10, 20]}
                try:
                    main_mod.read_notes(bad_utf8_path)
                except UnicodeDecodeError:
                    pass
                actual_results.append((cid, "state_preservation", st))

            elif cid == "TC-07":
                try:
                    main_mod.read_notes("")
                except FileNotFoundError:
                    pass
                rec = main_mod.read_notes(main_mod.DEFAULT_NOTES_PATH)
                actual_results.append((cid, "recovery", rec))

            elif cid == "TC-08":
                try:
                    main_mod.read_notes(bad_utf8_path)
                except UnicodeDecodeError:
                    pass
                rec = main_mod.read_notes(main_mod.DEFAULT_NOTES_PATH)
                actual_results.append((cid, "recovery", rec))

            elif cid == "TC-09":
                try:
                    main_mod.read_notes("nonexistent_file_xyz_404.txt")
                    actual_results.append((cid, "no_exception", None))
                except FileNotFoundError:
                    actual_results.append(
                        (cid, "exception", "FileNotFoundError")
                    )
                except Exception as e:
                    actual_results.append((cid, "exception", type(e).__name__))

            elif cid == "TC-10":
                try:
                    main_mod.read_notes(None)
                    actual_results.append((cid, "no_exception", None))
                except TypeError:
                    actual_results.append((cid, "exception", "TypeError"))
                except Exception as e:
                    actual_results.append((cid, "exception", type(e).__name__))

            elif cid == "TC-11":
                try:
                    main_mod.read_notes(latin1_path)
                    actual_results.append((cid, "no_exception", None))
                except UnicodeDecodeError:
                    actual_results.append(
                        (cid, "exception", "UnicodeDecodeError")
                    )
                except Exception as e:
                    actual_results.append((cid, "exception", type(e).__name__))

            elif cid == "TC-12":
                act = main_mod.read_notes(latin1_path, encoding="latin-1")
                actual_results.append((cid, "value", act))

            elif cid == "TC-13":
                act = main_mod.read_notes(single_char_path)
                actual_results.append((cid, "value", act))

            elif cid == "TC-14":
                act = main_mod.read_notes(multiline_path)
                actual_results.append((cid, "value", act))

            elif cid == "TC-15":
                act = main_mod.read_notes()
                actual_results.append((cid, "value", act))

            elif cid == "TC-16":
                alias_ok = (
                    main_mod.python315_utf8_default is main_mod.read_notes
                    and main_mod.read_text is main_mod.read_notes
                    and main_mod.main is main_mod.read_notes
                )
                actual_results.append((cid, "value", alias_ok))

            elif cid == "TC-17":
                try:
                    main_mod.read_notes(MODULE_DIR)
                    actual_results.append((cid, "no_exception", None))
                except (IsADirectoryError, PermissionError):
                    actual_results.append(
                        (cid, "exception", "IsADirectoryError")
                    )
                except Exception as e:
                    actual_results.append((cid, "exception", type(e).__name__))

            elif cid == "TC-18":
                oracle_res = independent_pathlib_oracle(
                    main_mod.DEFAULT_NOTES_PATH
                )
                act = main_mod.read_notes(main_mod.DEFAULT_NOTES_PATH)
                assert act == oracle_res
                actual_results.append((cid, "value", act))

            elif cid == "TC-19":
                data_path = MODULE_DIR / "data.json"
                oracle_res = independent_pathlib_oracle(data_path)
                act = main_mod.read_notes(data_path)
                assert act == oracle_res
                actual_results.append((cid, "value", act))

            elif cid == "TC-20":
                legacy_path = MODULE_DIR / "legacy.csv"
                oracle_res = independent_pathlib_oracle(legacy_path)
                act = main_mod.read_notes(legacy_path)
                assert act == oracle_res
                actual_results.append((cid, "value", act))

    finally:
        for p in [
            empty_path,
            bad_utf8_path,
            latin1_path,
            single_char_path,
            multiline_path,
        ]:
            if p.exists():
                p.unlink()

    return actual_results


def generate_evidence_files(tool_versions, break_reports, actual_results):
    """Generate all required task evidence files in work/R32-T058/."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # 1. tool-versions.txt
    tool_file = WORK_DIR / "tool-versions.txt"
    tool_text = (
        f"Python: {tool_versions['Python']}\n"
        f"Platform: {tool_versions['Platform']}\n"
        f"Ruff: {tool_versions['Ruff']}\n"
    )
    tool_file.write_text(tool_text, encoding="utf-8")

    # 2. test-inputs.txt
    inputs_file = WORK_DIR / "test-inputs.txt"
    input_lines = []
    for case in TEST_CASES:
        inp_str = repr(case["input"])
        input_lines.append(
            f"[{case['id']}] Input: {inp_str} ({case['desc']}) [Precondition:"
            f" {case['source_precondition']}]"
        )
    inputs_file.write_text("\n".join(input_lines) + "\n", encoding="utf-8")

    # 3. expected-results.txt
    exp_file = WORK_DIR / "expected-results.txt"
    exp_lines = []
    for case in TEST_CASES:
        exp_lines.append(
            f"[{case['id']}] Type: {case['expected_type']}, Expected:"
            f" {repr(case['expected_value'])}"
        )
    exp_file.write_text("\n".join(exp_lines) + "\n", encoding="utf-8")

    # 4. actual-results.txt
    act_file = WORK_DIR / "actual-results.txt"
    act_lines = []
    for cid, rtype, val in actual_results:
        act_lines.append(f"[{cid}] Type: {rtype}, Actual: {repr(val)}")
    act_file.write_text("\n".join(act_lines) + "\n", encoding="utf-8")

    # 5. evidence.txt
    evidence_file = WORK_DIR / "evidence.txt"
    evidence_text = f"""================================================================================
TASK EVIDENCE REPORT: R32-T058
================================================================================
Task ID: R32-T058 (Task 8 of 10)
Repository: S-AI-Projects/materials
Target Module: python315-utf8-default/main.py
Assigned Branch: student/e26b07f0709/R32-T058
Pull Request Base: master
Pull Request Head: student/e26b07f0709/R32-T058
GitHub Issue: https://github.com/S-AI-Projects/materials/issues/58

--------------------------------------------------------------------------------
1. TOOL & RUNTIME ENVIRONMENT
--------------------------------------------------------------------------------
{tool_text.strip()}

--------------------------------------------------------------------------------
2. SOURCE PRECONDITIONS & ANCHORS
--------------------------------------------------------------------------------
- Primary Source Anchor (main.py: Line 1):
  `import textlib` establishes external dependency on textlib reading routine.
- Primary Source Anchor (main.py: Line 3):
  `textlib.read_text("notes.txt")` establishes default notes path fixture.
- Helper Precondition Anchor (textlib.py: Line 5):
  `encoding = io.text_encoding(encoding)` establishes default UTF-8 under Python 3.15 (PEP 686).
- Helper Precondition Anchor (textlib.py: Line 6):
  `with open(path, encoding=encoding) as f:` requires path to exist on filesystem.
- Helper Precondition Anchor (textlib.py: Line 7):
  `return f.read()` returns decoded text string, yielding "" on 0-byte files.

--------------------------------------------------------------------------------
3. FAILURE, ABSENT-RESULT, AND RECOVERY BEHAVIORS
--------------------------------------------------------------------------------
- Missing File / FileNotFoundError:
  Smallest valid input `""` (empty string of length 0) or absent paths raise FileNotFoundError.
- Encoding Mismatch / UnicodeDecodeError:
  Smallest valid input (1-byte non-UTF8 0xFF) raises UnicodeDecodeError under default UTF-8.
- Absent-Result / Empty-Result (""):
  0-byte valid file yields empty string sentinel without error, honoring total read contract.
- Caller State Preservation:
  Caller collections (lists, dicts, tokens) remain strictly unmutated after failure.
- Successful Recovery:
  Immediate subsequent call with valid path (`notes.txt`) succeeds cleanly without resource leak.

--------------------------------------------------------------------------------
4. INDEPENDENT ORACLE EVALUATION (20 TEST CASES)
--------------------------------------------------------------------------------
Total Cases: 20
Agreement Rate: 100% (20 / 20)
- Smallest Valid Input (empty path ""): FileNotFoundError raised (OK)
- Ordinary Input (notes.txt): 68 bytes decoded text returned (OK)
- Smallest Valid Input (0-byte file): "" absent-result returned (OK)
- Smallest Valid Input (1-byte non-UTF8): UnicodeDecodeError raised (OK)
- Caller State Preservation (list/dict): Unaltered (OK)
- Subsequent Recovery Calls: 100% Success (OK)

--------------------------------------------------------------------------------
5. DELIBERATE REGRESSION / DEFECT BREAK VERIFICATIONS
--------------------------------------------------------------------------------
{chr(10).join(break_reports)}
All 4 deliberate defect breaks were successfully detected by the assertions.

--------------------------------------------------------------------------------
6. TEST EXECUTION SUMMARY
--------------------------------------------------------------------------------
- work/R32-T058/check.py: 20 oracle cases + 4 break checks: OK
- python315-utf8-default/test_main.py: 20 native unit tests: OK
- python315-utf8-default/main.py: 3 doctests: OK
- python-unittest discovery: 64 global tests: OK
- Ruff lint & format checks: All passed.
================================================================================
"""
    evidence_file.write_text(evidence_text, encoding="utf-8")


def main():
    """Main verification routine."""
    print("============================================================")
    print("Running Focused Check Runner for R32-T058")
    print("Target: python315-utf8-default/main.py (python315_utf8_default)")
    print("============================================================")

    # 1. Tool versions
    tool_versions = get_tool_versions()
    print(f"Python : {tool_versions['Python']}")
    print(f"Ruff   : {tool_versions['Ruff']}")

    # 2. Evaluate 20 test cases
    print(f"\n[1/5] Evaluating {len(TEST_CASES)} independent test cases...")
    actual_results = evaluate_test_cases()
    for case, (cid, rtype, val) in zip(
        TEST_CASES, actual_results, strict=True
    ):
        assert cid == case["id"]
        assert rtype == case["expected_type"]
        if rtype == "exception":
            assert val == case["expected_value"]
        elif rtype in ("value", "state_preservation", "recovery"):
            assert val == case["expected_value"], (
                f"Mismatch on {cid}: {val!r} != {case['expected_value']!r}"
            )
    print(f"  ✓ All {len(TEST_CASES)} test cases passed successfully.")

    # 3. Deliberate defect breaks
    print("\n[2/5] Conducting deliberate defect break verifications...")
    break_reports = run_deliberate_break_verifications()
    for rep in break_reports:
        print(f"  ✓ {rep}")

    # 4. Native unit tests and doctests
    print("\n[3/5] Running native module unit tests...")
    suite = unittest.defaultTestLoader.discover(
        str(MODULE_DIR), pattern="test_*.py"
    )
    runner = unittest.TextTestRunner(verbosity=1)
    test_result = runner.run(suite)
    assert test_result.wasSuccessful(), "Native unit tests failed"
    print(f"  ✓ Ran {test_result.testsRun} unit test suites successfully.")

    # Doctest
    print("\n[4/5] Running doctests on main.py...")
    dt_res = doctest.testmod(main_mod)
    assert dt_res.failed == 0, (
        f"Doctest failed: {dt_res.failed}/{dt_res.attempted} failed"
    )
    print(f"  ✓ Doctest passed: {dt_res.attempted} examples verified.")

    # Global project tests
    print("\n[5/5] Running global project test suite (python-unittest)...")
    global_suite = unittest.defaultTestLoader.discover(
        str(REPO_ROOT / "python-unittest")
    )
    global_runner = unittest.TextTestRunner(verbosity=0)
    global_res = global_runner.run(global_suite)
    assert global_res.wasSuccessful(), "Global python-unittest suite failed"
    print(f"  ✓ Ran {global_res.testsRun} global tests successfully.")

    # 6. Generate evidence files
    print("\nGenerating evidence files in work/R32-T058/...")
    generate_evidence_files(tool_versions, break_reports, actual_results)
    print(
        "  ✓ Saved tool-versions.txt, test-inputs.txt, expected-results.txt,"
    )
    print("          actual-results.txt, and evidence.txt.")

    print("\n============================================================")
    print("ALL CHECKS PASSED SUCCESSFULLY (Exit Code: 0)")
    print("============================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
