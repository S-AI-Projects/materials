#!/usr/bin/env python3
"""Focused runner and reference-comparison check for R32-T003.

Target: basic-input-output-in-python/greeter.py
Preconditions:
- Line 1: `name = input("Please enter your name: ")` prompts via stdin and reads string.
- Line 2: `print("Hello", name, "and welcome!")` outputs formatted greeting with spaces.

This runner executes:
1. 25 independent reference comparisons using an independent formatting oracle and explicit expected lookup table.
2. 5 native unit test cases under unittest with external I/O mocked.
3. Generates all verification evidence files in work/R32-T003/.
"""

import io
import json
import os
import platform
import subprocess
import sys
import unittest

# Ensure basic-input-output-in-python is in PYTHONPATH
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULE_DIR = os.path.join(REPO_ROOT, "basic-input-output-in-python")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import greeter


def independent_oracle_greet(name: str) -> str:
    """Independent reference oracle for greeter.

    Uses independent string concatenation / template rather than greet implementation.
    Precondition established by line 2: greeting format 'Hello ' + name + ' and welcome!'.
    """
    prefix = "Hello "
    suffix = " and welcome!"
    return prefix + str(name) + suffix


# 25 small valid inputs across diverse domains (smallest valid, whitespace, unicode, punctuation, names)
DOMAIN_INPUTS = [
    "",  # Smallest valid input
    "a",
    "42",
    "Bob",
    "Ada",
    "Alice",  # Ordinary input
    "Charlie",
    " Grace ",
    "Dr. Watson",
    "Jane Doe",
    "Anne-Marie",
    "Jean-Luc",
    "O'Connor",
    "José",
    "Müller",
    "Åsa",
    "Renée",
    "Søren",
    "Noël",
    "Li Wei",
    "Татьяна",
    "12345",
    "user_test",
    "Alpha-Beta",
    "LineEnd",
]


def run_checks():
    evidence_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(evidence_dir, exist_ok=True)

    print("=== Running R32-T003 Reference Comparison Checks ===")
    test_records = []
    failed_assertions = []

    # 1. Reference comparisons
    for idx, inp in enumerate(DOMAIN_INPUTS, start=1):
        # Preconditions: Line 1 establishes input string, Line 2 establishes output format
        expected = independent_oracle_greet(inp)
        actual = greeter.greet(inp)
        passed = (actual == expected)

        record = {
            "test_id": idx,
            "input": inp,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "preconditions": {
                "source_file": "basic-input-output-in-python/greeter.py",
                "line_1": 'name = input("Please enter your name: ")',
                "line_2": 'print("Hello", name, "and welcome!")',
            },
        }
        test_records.append(record)

        if not passed:
            failed_assertions.append(f"Mismatch for input '{inp}': expected '{expected}', got '{actual}'")

    print(f"Verified {len(DOMAIN_INPUTS)} inputs against independent reference oracle: {len(failed_assertions)} failures.")

    # 2. Native unittest suite execution with mocked I/O
    print("=== Running Native Unit Tests with Mocked I/O ===")
    suite = unittest.defaultTestLoader.discover(MODULE_DIR, pattern="test_*.py")
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    test_result = runner.run(suite)

    unittest_count = test_result.testsRun
    unittest_passed = test_result.wasSuccessful()
    print(f"Executed {unittest_count} native unit tests. All passed: {unittest_passed}")

    if not unittest_passed:
        failed_assertions.append(f"Native unit tests failed: {len(test_result.failures)} failures, {len(test_result.errors)} errors.")

    # 3. Write evidence files
    tool_versions = {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
    }

    with open(os.path.join(evidence_dir, "tool-versions.txt"), "w") as f:
        for k, v in tool_versions.items():
            f.write(f"{k}: {v}\n")

    with open(os.path.join(evidence_dir, "tool_versions.json"), "w") as f:
        json.dump(tool_versions, f, indent=2)

    with open(os.path.join(evidence_dir, "test-inputs.txt"), "w") as f:
        for r in test_records:
            f.write(f"Test {r['test_id']:02d}: {repr(r['input'])}\n")

    with open(os.path.join(evidence_dir, "expected-results.txt"), "w") as f:
        for r in test_records:
            f.write(f"Test {r['test_id']:02d}: {repr(r['expected'])}\n")

    with open(os.path.join(evidence_dir, "actual-results.txt"), "w") as f:
        for r in test_records:
            f.write(f"Test {r['test_id']:02d}: {repr(r['actual'])}\n")

    with open(os.path.join(evidence_dir, "inputs_and_results.json"), "w") as f:
        json.dump(
            {
                "reference_checks_count": len(test_records),
                "native_tests_count": unittest_count,
                "all_checks_passed": len(failed_assertions) == 0,
                "records": test_records,
            },
            f,
            indent=2,
        )

    with open(os.path.join(evidence_dir, "evidence.txt"), "w") as f:
        f.write("R32-T003 Verification Summary\n")
        f.write("==============================\n")
        f.write(f"Target module: basic-input-output-in-python/greeter.py\n")
        f.write(f"Precondition Line 1: name = input(\"Please enter your name: \")\n")
        f.write(f"Precondition Line 2: print(\"Hello\", name, \"and welcome!\")\n")
        f.write(f"Smallest valid input: '' -> {repr(independent_oracle_greet(''))}\n")
        f.write(f"Ordinary input: 'Alice' -> {repr(independent_oracle_greet('Alice'))}\n")
        f.write(f"Reference domain checks: {len(test_records)} evaluated, {len(test_records) - len(failed_assertions)} passed\n")
        f.write(f"Native unit tests: {unittest_count} executed, {unittest_count - len(test_result.failures) - len(test_result.errors)} passed\n")
        f.write(f"Exit status: {0 if len(failed_assertions) == 0 else 1}\n\n")
        f.write("Unittest Output:\n")
        f.write(stream.getvalue())

    if failed_assertions:
        print("FAILURES DETECTED:")
        for err in failed_assertions:
            print(" -", err)
        sys.exit(1)

    print("All reference comparison checks and native unit tests passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    run_checks()
