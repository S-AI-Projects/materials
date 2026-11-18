#!/usr/bin/env python3
"""Verification check runner for Task R32-T028.

Covers the failure behavior and absent-result branches of python recursion (names.py).
Evaluates terminal search conditions, empty boundaries, TypeError branches, and native tests.
"""

import importlib.util
import io
import os
import platform
import sys
import unittest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))

# Load names.py
NAMES_PATH = os.path.join(REPO_ROOT, "python-recursion", "names.py")
spec = importlib.util.spec_from_file_location("names", NAMES_PATH)
names_module = importlib.util.module_from_spec(spec)
sys.modules["names"] = names_module
spec.loader.exec_module(names_module)

# Load test_names.py
TEST_NAMES_PATH = os.path.join(REPO_ROOT, "python-recursion", "test_names.py")
test_spec = importlib.util.spec_from_file_location("test_names", TEST_NAMES_PATH)
test_module = importlib.util.module_from_spec(test_spec)
test_spec.loader.exec_module(test_module)

ABSENT_SENTINEL = names_module.ABSENT_SENTINEL
count_names = names_module.count_names
find_name = names_module.find_name
names = names_module.names


def write_evidence(test_cases, test_results, unit_test_output):
    """Write verification evidence files to work/R32-T028/."""
    os.makedirs(WORK_DIR, exist_ok=True)

    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Interpreter: {sys.executable}\n")

    with open(os.path.join(WORK_DIR, "test-inputs.txt"), "w") as f:
        f.write("# Precondition Anchors from source:\n")
        f.write("Line 14: names = [...] nested hierarchy definition\n")
        f.write("Line 15: 'Adam' (first top-level leaf item)\n")
        f.write("Line 17: 'Bob' (nested list lead item)\n")
        f.write("Line 19: 'Chet', 'Cat' (deeply nested leaves)\n\n")
        f.write("# Failure & Absent-Result Test Inputs:\n")
        for target, tree, exp, desc in test_cases:
            f.write(
                f"Target: {repr(target)} | Tree: {repr(tree)[:60]} | Desc: {desc}\n"
            )

    with open(os.path.join(WORK_DIR, "expected-results.txt"), "w") as f:
        f.write("# Expected Outcomes (Failure, Sentinel, or Found Value):\n")
        for target, tree, exp, desc in test_cases:
            f.write(f"Desc: {desc} => Expected: {exp}\n")

    with open(os.path.join(WORK_DIR, "actual-results.txt"), "w") as f:
        f.write("# Actual Outcomes:\n")
        for desc, act, status in test_results:
            f.write(f"Desc: {desc} => Actual: {act} | Status: {status}\n")

    with open(os.path.join(WORK_DIR, "evidence.txt"), "w") as f:
        f.write("=== Task R32-T028 Verification Evidence ===\n")
        f.write("Target: python-recursion/names.py (Failure & Sentinel Coverage)\n")
        f.write(f"Test Cases Evaluated: {len(test_results)}/{len(test_cases)}\n")
        f.write("Absent-result sentinel None and TypeError failure branches verified.\n\n")
        f.write("=== Native Unit Test Output ===\n")
        f.write(unit_test_output)
        f.write("\nVerification Result: SUCCESS (Exit Code 0)\n")


def main():
    print("Running Task R32-T028 verification check...")

    test_cases = [
        ("Adam", [], "ABSENT_SENTINEL (None)", "Smallest valid boundary (empty tree)"),
        ("Adam", names, "Adam", "Ordinary valid input (found top-level leaf)"),
        ("Chet", names, "Chet", "Ordinary valid input (found deep nested leaf)"),
        (
            "Zelda",
            names,
            "ABSENT_SENTINEL (None)",
            "Documented absent-result sentinel path",
        ),
        (
            "",
            names,
            "ABSENT_SENTINEL (None)",
            "Empty string absent-result sentinel path",
        ),
        ("Adam", 12345, "TypeError", "Failure branch: invalid tree type (int)"),
        (12345, names, "TypeError", "Failure branch: invalid target type (int)"),
    ]

    test_results = []
    for target, tree, exp, desc in test_cases:
        try:
            res = find_name(target, tree)
            if res is ABSENT_SENTINEL:
                act = "ABSENT_SENTINEL (None)"
            else:
                act = str(res)
            if act == exp:
                status = "PASS"
            else:
                status = f"FAIL (Expected {exp}, Got {act})"
                print(f"FAILED on {desc}: {status}")
                sys.exit(1)
        except TypeError as e:
            act = "TypeError"
            if act == exp:
                status = "PASS"
            else:
                status = f"FAIL (Expected {exp}, Got {act})"
                print(f"FAILED on {desc}: {status}")
                sys.exit(1)
        except Exception as e:
            act = f"Unexpected Error: {e}"
            status = "FAIL"
            print(f"ERROR on {desc}: {act}")
            sys.exit(1)

        test_results.append((desc, act, status))

    # Run native unit test suite
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        test_module.TestNamesRecursionFailureBehavior
    )
    result = runner.run(suite)
    unit_test_output = stream.getvalue()

    if not result.wasSuccessful():
        print("Native unit test suite failed!")
        print(unit_test_output)
        sys.exit(1)

    print(f"All {len(test_cases)} failure/sentinel test cases passed.")
    print(f"Ran {result.testsRun} native unit tests: OK.")

    write_evidence(test_cases, test_results, unit_test_output)
    print(f"Verification evidence written to {WORK_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())

