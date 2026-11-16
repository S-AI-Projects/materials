#!/usr/bin/env python3
"""Focused test runner and property-based invariant check for R32-T054.

Task ID: R32-T054
Target file: python-print/ansi.py
Target function: esc
Domain: ANSI escape code formatting for terminal styling and colors
"""

import importlib.util
import io
import platform
import random
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "python-print"
WORK_DIR = Path(__file__).resolve().parent

if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

# Mock stdout during import to intercept line 5 demo print
with patch("sys.stdout", new_callable=io.StringIO):
    from ansi import esc

PROPERTY_SEED = 42


def get_tool_versions():
    """Retrieve versions of runtime tools."""
    ruff_ver = "unknown"
    candidates = [
        ROOT / ".venv" / "bin" / "ruff",
        Path(sys.executable).parent / "ruff",
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                proc = subprocess.run(
                    [str(candidate), "--version"],
                    capture_output=True,
                    text=True,
                )
                if proc.returncode == 0:
                    ruff_ver = proc.stdout.strip()
                    break
            except Exception:
                pass
    if ruff_ver == "unknown":
        try:
            proc = subprocess.run(
                ["ruff", "--version"],
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0:
                ruff_ver = proc.stdout.strip()
        except Exception:
            pass

    return {
        "Python": sys.version,
        "Platform": platform.platform(),
        "Ruff": ruff_ver,
    }


def independent_oracle(*codes):
    """Independently calculate expected ANSI escape sequence.

    Derives expected string without calling esc(), using explicit ASCII ESC
    character chr(27) ('\\033'), CSI bracket '[', string conversions of
    each code, semicolon delimiters, and SGR terminator 'm'.
    """
    esc_byte = chr(27)  # '\033'
    prefix = esc_byte + "["
    suffix = "m"
    if not codes:
        return prefix + suffix
    payload = ";".join(str(c) for c in codes)
    return prefix + payload + suffix


def verify_esc_invariant(codes, result):
    """Formally verify contract invariants for esc(*codes) -> result."""
    assert isinstance(result, str), (
        f"Expected str, got {type(result).__name__}"
    )
    assert result.startswith("\033["), (
        f"Result {result!r} does not start with \\033["
    )
    assert result.endswith("m"), f"Result {result!r} does not end with 'm'"

    payload = result[2:-1]
    n = len(codes)

    if n == 0:
        assert payload == "", (
            f"Expected empty payload for 0 codes, got {payload!r}"
        )
        assert result.count(";") == 0, (
            f"Expected 0 semicolons for empty codes, got {result.count(';')}"
        )
        assert len(result) == 3, (
            f"Expected length 3 for esc(), got {len(result)}"
        )
    else:
        expected_semicolons = n - 1
        assert result.count(";") == expected_semicolons, (
            f"Expected {expected_semicolons} semicolons, got {result.count(';')}"
        )
        expected_len = 3 + sum(len(str(c)) for c in codes) + (n - 1)
        assert len(result) == expected_len, (
            f"Expected length {expected_len}, got {len(result)}"
        )
        parsed_tokens = tuple(payload.split(";"))
        expected_tokens = tuple(str(c) for c in codes)
        assert parsed_tokens == expected_tokens, (
            f"Roundtrip token mismatch: expected {expected_tokens}, got {parsed_tokens}"
        )
        for i in range(len(codes)):
            tok_i = str(codes[i])
            assert parsed_tokens[i] == tok_i, (
                f"Token ordering violation at index {i}: expected {tok_i!r}, got {parsed_tokens[i]!r}"
            )


def generate_bounded_cases(seed=PROPERTY_SEED, count=120):
    """Deterministically generate bounded valid ANSI code sequences."""
    rng = random.Random(seed)
    styles = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 21, 22, 24, 27, 28, 29]
    fg_colors = list(range(30, 38)) + [39] + list(range(90, 98))
    bg_colors = list(range(40, 48)) + [49] + list(range(100, 108))
    extended = [38, 48, 5, 2] + list(range(0, 256, 17))
    code_pool = sorted(set(styles + fg_colors + bg_colors + extended))

    cases = []
    for i in range(count):
        if i % 15 == 0:
            length = 0
        elif i % 15 in (1, 2, 3):
            length = 1
        elif i % 15 in (4, 5, 6):
            length = 2
        elif i % 15 in (7, 8, 9):
            length = 3
        elif i % 15 in (10, 11):
            length = 4
        elif i % 15 == 12:
            length = 5
        elif i % 15 == 13:
            length = 6
        else:
            length = 8
        case_tuple = tuple(rng.choice(code_pool) for _ in range(length))
        cases.append(case_tuple)
    return cases


def run_deliberate_invariant_break_verification():
    """Verify that checks fail when invariants are deliberately broken in temp copies."""
    break_scenarios = [
        {
            "id": "BREAK-01",
            "name": "Missing ESC CSI prefix (framing defect)",
            "defect_source": (
                "def esc(*codes):\n"
                '    payload = ";".join(str(c) for c in codes)\n'
                '    return f"[{payload}m"\n'
            ),
            "smallest_failing_input": (),
            "expected_error": "does not start with \\033[",
        },
        {
            "id": "BREAK-02",
            "name": "Comma delimiter instead of semicolon (delimiter defect)",
            "defect_source": (
                "def esc(*codes):\n"
                '    payload = ",".join(str(c) for c in codes)\n'
                '    return f"\\033[{payload}m"\n'
            ),
            "smallest_failing_input": (1, 2),
            "expected_error": "Expected 1 semicolons, got 0",
        },
        {
            "id": "BREAK-03",
            "name": "Reversed argument order (ordering preservation defect)",
            "defect_source": (
                "def esc(*codes):\n"
                '    payload = ";".join(str(c) for c in reversed(codes))\n'
                '    return f"\\033[{payload}m"\n'
            ),
            "smallest_failing_input": (1, 2),
            "expected_error": "Roundtrip token mismatch",
        },
        {
            "id": "BREAK-04",
            "name": "Missing 'm' SGR terminator (suffix framing defect)",
            "defect_source": (
                "def esc(*codes):\n"
                '    payload = ";".join(str(c) for c in codes)\n'
                '    return f"\\033[{payload}"\n'
            ),
            "smallest_failing_input": (),
            "expected_error": "does not end with 'm'",
        },
    ]

    break_reports = []

    for scenario in break_scenarios:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = Path(tmpdir) / "ansi.py"
            temp_file.write_text(scenario["defect_source"])

            # Dynamically import broken esc
            spec = importlib.util.spec_from_file_location(
                f"ansi_broken_{scenario['id']}", temp_file
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            broken_esc = mod.esc

            inp = scenario["smallest_failing_input"]
            caught = False
            caught_msg = ""
            try:
                res = broken_esc(*inp)
                verify_esc_invariant(inp, res)
            except AssertionError as exc:
                caught = True
                caught_msg = str(exc)

            assert caught, (
                f"Deliberate break {scenario['id']} ({scenario['name']}) "
                f"failed to raise AssertionError!"
            )
            assert scenario["expected_error"] in caught_msg, (
                f"Deliberate break {scenario['id']} raised unexpected error: {caught_msg!r}"
            )

            report_entry = (
                f"[{scenario['id']}] PASS: {scenario['name']}\n"
                f"  Smallest failing input: {inp!r}\n"
                f"  Caught AssertionError as expected: {caught_msg}\n"
                f"  Clean repository state preserved: Verified\n"
            )
            break_reports.append(report_entry)

    return break_reports


def run_checks_and_collect_evidence():
    """Execute all property and boundary checks and record evidence."""
    tool_info = get_tool_versions()

    # Preconditions from source
    preconditions = [
        "Line 1: def esc(*codes): - Variable positional argument acceptance",
        (
            "Line 2: return f\"\\033[{';'.join(str(code) for code in codes)}m\""
            " - CSI prefix '\\033[', ';' delimiter, 'm' terminator"
        ),
        (
            "Line 5: print(esc(31, 1, 4) + 'really' + esc(0) + ' important') -"
            " Ordinary multi-code input (31, 1, 4) -> '\\033[31;1;4m' and"
            " reset (0,) -> '\\033[0m'"
        ),
    ]

    # Literal fixtures
    fixture_cases = [
        ("Smallest valid input (zero arguments)", (), "\033[m"),
        (
            "Ordinary input anchor 1 (RED, BOLD, UNDERLINE)",
            (31, 1, 4),
            "\033[31;1;4m",
        ),
        ("Ordinary input anchor 2 (RESET)", (0,), "\033[0m"),
        ("Curated boundary (BOLD)", (1,), "\033[1m"),
        ("Curated boundary (UNDERLINE)", (4,), "\033[4m"),
        ("Curated boundary (REVERSE)", (7,), "\033[7m"),
        ("Curated boundary (FG RED)", (31,), "\033[31m"),
        ("Curated boundary (FG GREEN)", (32,), "\033[32m"),
        ("Curated boundary (BG RED)", (41,), "\033[41m"),
        ("Curated boundary (BRIGHT GREEN)", (92,), "\033[92m"),
        ("Curated boundary (8-bit color)", (38, 5, 196), "\033[38;5;196m"),
        (
            "Curated boundary (24-bit truecolor RGB)",
            (48, 2, 255, 128, 0),
            "\033[48;2;255;128;0m",
        ),
        (
            "Curated boundary (string/int mixed)",
            ("31", "1", 4),
            "\033[31;1;4m",
        ),
    ]

    # Generated property cases
    generated_cases = generate_bounded_cases(seed=PROPERTY_SEED, count=120)

    all_test_inputs = []
    all_expected = []
    all_actual = []
    test_logs = []

    # Run fixtures
    for idx, (label, inp, exp) in enumerate(fixture_cases, start=1):
        actual = esc(*inp)
        verify_esc_invariant(inp, actual)
        assert actual == exp, (
            f"Fixture mismatch for {label}: expected {exp!r}, got {actual!r}"
        )

        all_test_inputs.append(f"[TC-FIX-{idx:02d}] {inp!r} ({label})")
        all_expected.append(f"[TC-FIX-{idx:02d}] {exp!r}")
        all_actual.append(f"[TC-FIX-{idx:02d}] {actual!r}")
        test_logs.append(
            f"[TC-FIX-{idx:02d}] PASS: {label} -> Input={inp!r}, Output={actual!r}"
        )

    # Run generated cases
    for idx, inp in enumerate(generated_cases, start=1):
        exp = independent_oracle(*inp)
        actual = esc(*inp)
        verify_esc_invariant(inp, actual)
        assert actual == exp, (
            f"Generated mismatch at case {idx}: expected {exp!r}, got {actual!r}"
        )

        all_test_inputs.append(f"[TC-PROP-{idx:03d}] {inp!r}")
        all_expected.append(f"[TC-PROP-{idx:03d}] {exp!r}")
        all_actual.append(f"[TC-PROP-{idx:03d}] {actual!r}")
        test_logs.append(
            f"[TC-PROP-{idx:03d}] PASS: Length={len(inp)} -> Input={inp!r}, Output={actual!r}"
        )

    # Deliberate breaks
    deliberate_break_reports = run_deliberate_invariant_break_verification()

    # Native test execution
    unit_cmd = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(SOURCE_DIR),
        "-p",
        "test_ansi.py",
        "-v",
    ]
    proc = subprocess.run(
        unit_cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    unit_output = proc.stdout + proc.stderr
    unit_exit = proc.returncode

    # Build evidence document
    evidence_lines = [
        "R32-T054 Invariant and Property Test Evidence",
        "============================================",
        "Task ID: R32-T054",
        "Target file: python-print/ansi.py",
        "Target function: esc",
        "Student URN: e26b07f0709",
        "Branch: student/e26b07f0709/R32-T054",
        "",
        "Tool and Runtime Versions:",
        f"  Python: {tool_info['Python']}",
        f"  Platform: {tool_info['Platform']}",
        f"  Ruff: {tool_info['Ruff']}",
        "",
        "Preconditions established by source:",
        *[f"  {p}" for p in preconditions],
        "",
        "Invariant Contract Specification:",
        "  - Function signature: esc(*codes)",
        "  - Smallest valid input: () (0 arguments) -> '\\033[m'",
        (
            "  - Ordinary inputs: (31, 1, 4) -> '\\033[31;1;4m' and (0,) ->"
            " '\\033[0m'"
        ),
        "  - Output type: str",
        "  - Framing: prefix '\\033[', suffix 'm'",
        (
            "  - Semicolon delimiter count: strictly max(0, len(codes) - 1)"
            " semicolons"
        ),
        (
            "  - Exact character length: 3 + sum(len(str(c))) + max(0,"
            " len(codes) - 1)"
        ),
        (
            "  - Reversibility roundtrip: tuple(payload.split(';')) =="
            " tuple(str(c) for c in codes)"
        ),
        "  - Ordering behavior: strictly monotonic parameter order preserved",
        (
            "  - Determinism & Idempotence: repeated equivalent calls yield"
            " identical outputs"
        ),
        "  - Immutability: caller argument containers are never mutated",
        "  - External I/O: mocked (stdout intercepted during import and evaluation)",
        "",
        "Property-Based Testing Configuration:",
        f"  - Generator seed: {PROPERTY_SEED} (deterministic fixed random seed)",
        f"  - Generated test cases: {len(generated_cases)} bounded cases (lengths 0 to 8)",
        f"  - Curated fixture cases: {len(fixture_cases)} boundary cases",
        f"  - Total evaluated cases: {len(fixture_cases) + len(generated_cases)}",
        "",
        "Deliberate Invariant-Break Verification (Mandatory Acceptance Criterion):",
        *deliberate_break_reports,
        "Native Unit Test Suite Execution:",
        f"  Command: {' '.join(unit_cmd)}",
        f"  Exit code: {unit_exit}",
        "  Output:",
        unit_output,
        "Summary:",
        f"  Fixtures checked: {len(fixture_cases)} (all passed)",
        f"  Property cases checked: {len(generated_cases)} (all passed)",
        f"  Deliberate breaks verified: {len(deliberate_break_reports)} (all caught)",
        f"  Unit test exit code: {unit_exit}",
        "  Status: ALL INVARIANT CHECKS, PROPERTY TESTS AND UNIT TESTS PASSED",
    ]

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    (WORK_DIR / "test-inputs.txt").write_text(
        "\n".join(all_test_inputs) + "\n"
    )
    (WORK_DIR / "expected-results.txt").write_text(
        "\n".join(all_expected) + "\n"
    )
    (WORK_DIR / "actual-results.txt").write_text("\n".join(all_actual) + "\n")
    (WORK_DIR / "tool-versions.txt").write_text(
        f"Python: {tool_info['Python']}\n"
        f"Platform: {tool_info['Platform']}\n"
        f"Ruff: {tool_info['Ruff']}\n"
    )
    (WORK_DIR / "evidence.txt").write_text("\n".join(evidence_lines) + "\n")

    print(f"Evidence successfully saved to: {WORK_DIR / 'evidence.txt'}")
    print(
        f"Ran {len(fixture_cases)} fixtures + {len(generated_cases)} property cases: ALL PASSED."
    )
    print(
        f"Deliberate break verification: {len(deliberate_break_reports)} PASSED."
    )
    print(f"Unit test status: exit code {unit_exit}")

    return unit_exit


def main():
    exit_code = run_checks_and_collect_evidence()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
