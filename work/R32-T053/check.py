#!/usr/bin/env python3
"""Independent test runner and verification check for R32-T053.

Target: ipython-console/employee.py
Domain: IPython console employee representation and inspection
"""

import copy
import io
import json
import platform
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "ipython-console"
WORK_DIR = Path(__file__).resolve().parent

if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

# Import target function and module
from employee import (  # noqa: E402
    department as MOD_DEPT,
    first_name as MOD_FIRST_NAME,
    ipython_console,
    last_name as MOD_LAST_NAME,
    salary as MOD_SALARY,
)


def independent_oracle(*args, **kwargs):
    """Independent reference implementation (oracle) for employee inspection.

    Derives expected employee dictionary independently without calling
    ipython_console. Uses separate string construction and dictionary
    instantiation mechanisms.
    """
    if args and isinstance(args[0], dict) and len(args) == 1 and not kwargs:
        d = args[0]
        fn = d.get("first_name", "")
        ln = d.get("last_name", "")
        dept = d.get("department", "")
        sal = d.get("salary", 0)
    elif (
        args
        and isinstance(args[0], (list, tuple))
        and len(args) == 1
        and not kwargs
    ):
        seq = args[0]
        fn = seq[0] if len(seq) > 0 else ""
        ln = seq[1] if len(seq) > 1 else ""
        dept = seq[2] if len(seq) > 2 else ""
        sal = seq[3] if len(seq) > 3 else 0
    elif args or kwargs:
        fn = kwargs.get("first_name", args[0] if len(args) > 0 else "Han")
        ln = kwargs.get("last_name", args[1] if len(args) > 1 else "Solo")
        dept = kwargs.get(
            "department", args[2] if len(args) > 2 else "Accounts"
        )
        sal = kwargs.get("salary", args[3] if len(args) > 3 else 1000)
    else:
        # Preconditions established by lines 1-4
        fn, ln, dept, sal = "Han", "Solo", "Accounts", 1000

    # Independently derive full_name using formatting without list join
    if fn and ln:
        expected_full_name = f"{fn} {ln}"
    elif fn:
        expected_full_name = f"{fn}"
    elif ln:
        expected_full_name = f"{ln}"
    else:
        expected_full_name = ""

    # Construct result using dict constructor over zipped pairs
    keys = ("first_name", "last_name", "department", "salary", "full_name")
    vals = (fn, ln, dept, sal, expected_full_name)
    return dict(zip(keys, vals))


TEST_CASES = [
    {
        "id": "TC-01",
        "name": "Smallest valid input (empty strings, zero salary)",
        "precondition": "employee.py lines 1-4 string/numeric domain lower bounds",
        "args": ("", "", "", 0),
        "kwargs": {},
        "expected": {
            "first_name": "",
            "last_name": "",
            "department": "",
            "salary": 0,
            "full_name": "",
        },
    },
    {
        "id": "TC-02",
        "name": "Ordinary input (Han Solo from employee.py lines 1-4)",
        "precondition": "employee.py lines 1-4 standard employee fixture",
        "args": ("Han", "Solo", "Accounts", 1000),
        "kwargs": {},
        "expected": {
            "first_name": "Han",
            "last_name": "Solo",
            "department": "Accounts",
            "salary": 1000,
            "full_name": "Han Solo",
        },
    },
    {
        "id": "TC-03",
        "name": "Default invocation with empty arguments",
        "precondition": "employee.py lines 1-4 default module constants",
        "args": (),
        "kwargs": {},
        "expected": {
            "first_name": "Han",
            "last_name": "Solo",
            "department": "Accounts",
            "salary": 1000,
            "full_name": "Han Solo",
        },
    },
    {
        "id": "TC-04",
        "name": "Single character names",
        "precondition": "employee.py lines 1-2 minimal non-empty string length",
        "args": ("A", "B", "R&D", 500),
        "kwargs": {},
        "expected": {
            "first_name": "A",
            "last_name": "B",
            "department": "R&D",
            "salary": 500,
            "full_name": "A B",
        },
    },
    {
        "id": "TC-05",
        "name": "Alphanumeric identifiers in name fields",
        "precondition": "employee.py lines 1-2 string representation",
        "args": ("User1", "Test2", "IT", 2500),
        "kwargs": {},
        "expected": {
            "first_name": "User1",
            "last_name": "Test2",
            "department": "IT",
            "salary": 2500,
            "full_name": "User1 Test2",
        },
    },
    {
        "id": "TC-06",
        "name": "Hyphenated last name",
        "precondition": "employee.py line 2 hyphenated string token",
        "args": ("Leia", "Organa-Solo", "Executive", 5000),
        "kwargs": {},
        "expected": {
            "first_name": "Leia",
            "last_name": "Organa-Solo",
            "department": "Executive",
            "salary": 5000,
            "full_name": "Leia Organa-Solo",
        },
    },
    {
        "id": "TC-07",
        "name": "Multi-word first name containing spaces",
        "precondition": "employee.py line 1 compound string token",
        "args": ("Mary Jane", "Watson", "Editorial", 3200),
        "kwargs": {},
        "expected": {
            "first_name": "Mary Jane",
            "last_name": "Watson",
            "department": "Editorial",
            "salary": 3200,
            "full_name": "Mary Jane Watson",
        },
    },
    {
        "id": "TC-08",
        "name": "First name only (empty last name)",
        "precondition": "employee.py line 2 empty string boundary",
        "args": ("Chewbacca", "", "Co-Pilot", 800),
        "kwargs": {},
        "expected": {
            "first_name": "Chewbacca",
            "last_name": "",
            "department": "Co-Pilot",
            "salary": 800,
            "full_name": "Chewbacca",
        },
    },
    {
        "id": "TC-09",
        "name": "Last name only (empty first name)",
        "precondition": "employee.py line 1 empty string boundary",
        "args": ("", "Yoda", "Jedi Council", 0),
        "kwargs": {},
        "expected": {
            "first_name": "",
            "last_name": "Yoda",
            "department": "Jedi Council",
            "salary": 0,
            "full_name": "Yoda",
        },
    },
    {
        "id": "TC-10",
        "name": "Zero salary boundary with named employee",
        "precondition": "employee.py line 4 zero salary threshold",
        "args": ("Luke", "Skywalker", "Jedi", 0),
        "kwargs": {},
        "expected": {
            "first_name": "Luke",
            "last_name": "Skywalker",
            "department": "Jedi",
            "salary": 0,
            "full_name": "Luke Skywalker",
        },
    },
    {
        "id": "TC-11",
        "name": "Negative salary boundary (accounting deduction)",
        "precondition": "employee.py line 4 signed numeric domain",
        "args": ("Lando", "Calrissian", "Operations", -500),
        "kwargs": {},
        "expected": {
            "first_name": "Lando",
            "last_name": "Calrissian",
            "department": "Operations",
            "salary": -500,
            "full_name": "Lando Calrissian",
        },
    },
    {
        "id": "TC-12",
        "name": "Floating point salary with fractional cents",
        "precondition": "employee.py line 4 float numeric support",
        "args": ("Wedge", "Antilles", "Flight", 1250.75),
        "kwargs": {},
        "expected": {
            "first_name": "Wedge",
            "last_name": "Antilles",
            "department": "Flight",
            "salary": 1250.75,
            "full_name": "Wedge Antilles",
        },
    },
    {
        "id": "TC-13",
        "name": "Large integer salary",
        "precondition": "employee.py line 4 high-magnitude integer",
        "args": ("Palpatine", "Emperor", "Administration", 1000000),
        "kwargs": {},
        "expected": {
            "first_name": "Palpatine",
            "last_name": "Emperor",
            "department": "Administration",
            "salary": 1000000,
            "full_name": "Palpatine Emperor",
        },
    },
    {
        "id": "TC-14",
        "name": "Unicode accented string attributes",
        "precondition": "employee.py lines 1-3 UTF-8 unicode encoding",
        "args": ("Amélie", "Poulain", "Café", 1800),
        "kwargs": {},
        "expected": {
            "first_name": "Amélie",
            "last_name": "Poulain",
            "department": "Café",
            "salary": 1800,
            "full_name": "Amélie Poulain",
        },
    },
    {
        "id": "TC-15",
        "name": "Non-ASCII CJK string attributes",
        "precondition": "employee.py lines 1-3 multi-byte character support",
        "args": ("太郎", "山田", "Engineering", 4500),
        "kwargs": {},
        "expected": {
            "first_name": "太郎",
            "last_name": "山田",
            "department": "Engineering",
            "salary": 4500,
            "full_name": "太郎 山田",
        },
    },
    {
        "id": "TC-16",
        "name": "Special punctuation characters in department",
        "precondition": "employee.py line 3 punctuation symbol support",
        "args": ("C-3PO", "Droid", "Protocol & Translation", 150),
        "kwargs": {},
        "expected": {
            "first_name": "C-3PO",
            "last_name": "Droid",
            "department": "Protocol & Translation",
            "salary": 150,
            "full_name": "C-3PO Droid",
        },
    },
    {
        "id": "TC-17",
        "name": "Multi-word spaced department name",
        "precondition": "employee.py line 3 spaced string token",
        "args": ("R2-D2", "Astromech", "Starship Maintenance", 200),
        "kwargs": {},
        "expected": {
            "first_name": "R2-D2",
            "last_name": "Astromech",
            "department": "Starship Maintenance",
            "salary": 200,
            "full_name": "R2-D2 Astromech",
        },
    },
    {
        "id": "TC-18",
        "name": "All lowercase string values",
        "precondition": "employee.py lines 1-3 case variance",
        "args": ("obi-wan", "kenobi", "general", 3000),
        "kwargs": {},
        "expected": {
            "first_name": "obi-wan",
            "last_name": "kenobi",
            "department": "general",
            "salary": 3000,
            "full_name": "obi-wan kenobi",
        },
    },
    {
        "id": "TC-19",
        "name": "All uppercase string values",
        "precondition": "employee.py lines 1-3 case variance",
        "args": ("BOBA", "FETT", "BOUNTY", 7500),
        "kwargs": {},
        "expected": {
            "first_name": "BOBA",
            "last_name": "FETT",
            "department": "BOUNTY",
            "salary": 7500,
            "full_name": "BOBA FETT",
        },
    },
    {
        "id": "TC-20",
        "name": "Long department description string",
        "precondition": "employee.py line 3 long string support",
        "args": (
            "Ahsoka",
            "Tano",
            "Department of Outer Rim Exploration and Peacekeeping Operations",
            3800,
        ),
        "kwargs": {},
        "expected": {
            "first_name": "Ahsoka",
            "last_name": "Tano",
            "department": "Department of Outer Rim Exploration and Peacekeeping Operations",
            "salary": 3800,
            "full_name": "Ahsoka Tano",
        },
    },
    {
        "id": "TC-21",
        "name": "Sub-dollar fractional salary",
        "precondition": "employee.py line 4 decimal fraction support",
        "args": ("Wicket", "Ewok", "Scouting", 0.99),
        "kwargs": {},
        "expected": {
            "first_name": "Wicket",
            "last_name": "Ewok",
            "department": "Scouting",
            "salary": 0.99,
            "full_name": "Wicket Ewok",
        },
    },
    {
        "id": "TC-22",
        "name": "High-precision float salary",
        "precondition": "employee.py line 4 float precision handling",
        "args": ("Bail", "Organa", "Senate", 9999.999),
        "kwargs": {},
        "expected": {
            "first_name": "Bail",
            "last_name": "Organa",
            "department": "Senate",
            "salary": 9999.999,
            "full_name": "Bail Organa",
        },
    },
    {
        "id": "TC-23",
        "name": "Dictionary input mapping",
        "precondition": "employee.py lines 1-4 dictionary record support",
        "args": (
            {
                "first_name": "Cassian",
                "last_name": "Andor",
                "department": "Intelligence",
                "salary": 2800,
            },
        ),
        "kwargs": {},
        "expected": {
            "first_name": "Cassian",
            "last_name": "Andor",
            "department": "Intelligence",
            "salary": 2800,
            "full_name": "Cassian Andor",
        },
    },
    {
        "id": "TC-24",
        "name": "Tuple input sequence",
        "precondition": "employee.py lines 1-4 sequence record support",
        "args": (("Jyn", "Erso", "Special Ops", 2100),),
        "kwargs": {},
        "expected": {
            "first_name": "Jyn",
            "last_name": "Erso",
            "department": "Special Ops",
            "salary": 2100,
            "full_name": "Jyn Erso",
        },
    },
]


def get_tool_versions():
    """Retrieve versions of relevant tooling."""
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
        "Python": sys.version.replace("\n", " "),
        "Platform": platform.platform(),
        "Ruff": ruff_ver,
    }


def run_independent_checks():
    """Execute all test cases against independent oracle and explicit expected results."""
    # Preconditions check
    assert MOD_FIRST_NAME == "Han", (
        f"Precondition line 1 failure: {MOD_FIRST_NAME!r}"
    )
    assert MOD_LAST_NAME == "Solo", (
        f"Precondition line 2 failure: {MOD_LAST_NAME!r}"
    )
    assert MOD_DEPT == "Accounts", f"Precondition line 3 failure: {MOD_DEPT!r}"
    assert MOD_SALARY == 1000, f"Precondition line 4 failure: {MOD_SALARY!r}"

    results = []
    inputs_record = []
    expected_record = []
    actual_record = []
    failures = []

    for tc in TEST_CASES:
        tc_id = tc["id"]
        tc_name = tc["name"]
        precond = tc["precondition"]
        args = tc["args"]
        kwargs = tc["kwargs"]
        expected = tc["expected"]

        # Preserve deep copies to verify mutation behavior
        args_copy = copy.deepcopy(args)
        kwargs_copy = copy.deepcopy(kwargs)

        # 1. Independently calculated expected result via Oracle
        oracle_res = independent_oracle(*args, **kwargs)

        # 2. Actual result under controlled external state (mocked I/O)
        with patch("sys.stdout", new_callable=io.StringIO):
            actual = ipython_console(*args, **kwargs)

        # Check return type
        if not isinstance(actual, dict):
            msg = f"Return type mismatch: expected dict, got {type(actual)}"
            failures.append((tc_id, tc_name, msg))
            continue

        # Check output shape
        expected_keys = [
            "first_name",
            "last_name",
            "department",
            "salary",
            "full_name",
        ]
        if list(actual.keys()) != expected_keys:
            msg = f"Key ordering/shape mismatch: expected {expected_keys}, got {list(actual.keys())}"
            failures.append((tc_id, tc_name, msg))
            continue

        # Check explicit expected value
        if actual != expected:
            msg = f"Mismatch with explicit expected: expected {expected}, got {actual}"
            failures.append((tc_id, tc_name, msg))
            continue

        # Check independent oracle equivalence
        if actual != oracle_res:
            msg = f"Mismatch with oracle: oracle {oracle_res}, got {actual}"
            failures.append((tc_id, tc_name, msg))
            continue

        # Check mutation
        if args != args_copy:
            msg = "Positional arguments were mutated during execution"
            failures.append((tc_id, tc_name, msg))
            continue
        if kwargs != kwargs_copy:
            msg = "Keyword arguments were mutated during execution"
            failures.append((tc_id, tc_name, msg))
            continue

        inputs_record.append(
            f"[{tc_id}] Args={args!r} Kwargs={kwargs!r} Precondition={precond}"
        )
        expected_record.append(f"[{tc_id}] Expected={json.dumps(expected)}")
        actual_record.append(f"[{tc_id}] Actual={json.dumps(actual)}")

        results.append(
            f"[{tc_id}] PASS: {tc_name} -> Return=dict, Shape=5, Mutation=None, "
            f"Matches Oracle=True"
        )

    return failures, results, inputs_record, expected_record, actual_record


def main():
    tool_info = get_tool_versions()

    print("=== Running R32-T053 Focused Test Runner ===")
    print(f"Python: {tool_info['Python']}")
    print(f"Platform: {tool_info['Platform']}")
    print(f"Ruff: {tool_info['Ruff']}")
    print("Target: ipython-console/employee.py (ipython_console)\n")

    failures, results, inputs_rec, expected_rec, actual_rec = (
        run_independent_checks()
    )

    for r in results:
        print(r)

    if failures:
        print(f"\nFAILURE: {len(failures)} independent checks failed!")
        for fid, fname, fmsg in failures:
            print(f"[{fid}] {fname}: {fmsg}")
        sys.exit(1)

    print(
        f"\nAll {len(results)} independent reference checks passed successfully!"
    )

    # Native project unit test invocation
    native_command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(SOURCE_DIR),
        "-p",
        "test_employee.py",
        "-v",
    ]
    print(f"\nRunning native test command: {' '.join(native_command)}")
    unit_res = subprocess.run(
        native_command,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    print(unit_res.stdout)
    print(unit_res.stderr)

    if unit_res.returncode != 0:
        print(f"Native unit tests failed with code {unit_res.returncode}")
        sys.exit(unit_res.returncode)

    # Save evidence files to work/R32-T053/
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    (WORK_DIR / "test-inputs.txt").write_text("\n".join(inputs_rec) + "\n")
    (WORK_DIR / "expected-results.txt").write_text(
        "\n".join(expected_rec) + "\n"
    )
    (WORK_DIR / "actual-results.txt").write_text("\n".join(actual_rec) + "\n")
    (WORK_DIR / "tool-versions.txt").write_text(
        f"Python: {tool_info['Python']}\n"
        f"Platform: {tool_info['Platform']}\n"
        f"Ruff: {tool_info['Ruff']}\n"
    )

    evidence = [
        "R32-T053 Independent Reference Comparison Evidence",
        "==================================================",
        "Task ID: R32-T053",
        "Target file: ipython-console/employee.py",
        "Target function: ipython_console",
        "Student URN: e26b07f0709",
        "Branch: student/e26b07f0709/R32-T053",
        "",
        "Tool and Runtime Versions:",
        f"  Python: {tool_info['Python']}",
        f"  Platform: {tool_info['Platform']}",
        f"  Ruff: {tool_info['Ruff']}",
        "",
        "Preconditions established by source:",
        "  Line 1: first_name = 'Han'",
        "  Line 2: last_name = 'Solo'",
        "  Line 3: department = 'Accounts'",
        "  Line 4: salary = 1000",
        "",
        "Contract Specification:",
        "  - Function: ipython_console(first_name=MOD_FIRST_NAME, last_name=MOD_LAST_NAME, department=MOD_DEPT, salary=MOD_SALARY)",
        "  - Smallest valid input: ('', '', '', 0)",
        "  - Ordinary input: ('Han', 'Solo', 'Accounts', 1000)",
        "  - Output type: dict",
        "  - Output shape: 5 keys ('first_name', 'last_name', 'department', 'salary', 'full_name')",
        "  - Ordering: Deterministic key insertion order",
        "  - Mutation behavior: Non-mutating; inputs preserved unchanged",
        "  - External I/O: Mocked (stdout patched with io.StringIO)",
        "",
        f"Independent Oracle Results ({len(results)} inputs tested):",
        *results,
        "",
        "Native Unit Test Execution:",
        f"Command: {' '.join(native_command)}",
        f"Exit Code: {unit_res.returncode}",
        "Output:",
        unit_res.stdout,
        unit_res.stderr,
        "Status: ALL 24 INDEPENDENT REFERENCE CHECKS AND UNIT TESTS PASSED",
    ]

    evidence_file = WORK_DIR / "evidence.txt"
    evidence_file.write_text("\n".join(evidence) + "\n")
    print(f"\nSaved evidence files to: {WORK_DIR}")
    print("  - evidence.txt")
    print("  - test-inputs.txt")
    print("  - expected-results.txt")
    print("  - actual-results.txt")
    print("  - tool-versions.txt")

    sys.exit(0)


if __name__ == "__main__":
    main()
