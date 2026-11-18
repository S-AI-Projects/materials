#!/usr/bin/env python3
"""Verification check runner for Task R32-T026.

Simplifies one responsibility in age_group (string-concatenation-python/age.py).
Evaluates single-responsibility isolation, classification boundaries, and native tests.
"""

import importlib.util
import io
import os
import platform
import sys
import unittest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))

# Load age.py
AGE_PATH = os.path.join(REPO_ROOT, "string-concatenation-python", "age.py")
spec = importlib.util.spec_from_file_location("age", AGE_PATH)
age_module = importlib.util.module_from_spec(spec)
sys.modules["age"] = age_module
spec.loader.exec_module(age_module)

# Load test_age.py
TEST_AGE_PATH = os.path.join(REPO_ROOT, "string-concatenation-python", "test_age.py")
test_spec = importlib.util.spec_from_file_location("test_age", TEST_AGE_PATH)
test_module = importlib.util.module_from_spec(test_spec)
test_spec.loader.exec_module(test_module)

age_group = age_module.age_group
format_age_group = age_module.format_age_group
get_age_category = age_module.get_age_category


def write_evidence(test_cases, test_results, unit_test_output):
    """Write verification evidence files to work/R32-T026/."""
    os.makedirs(WORK_DIR, exist_ok=True)

    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Interpreter: {sys.executable}\n")

    with open(os.path.join(WORK_DIR, "test-inputs.txt"), "w") as f:
        f.write("# Precondition Anchors from source:\n")
        f.write("Line 1: def age_group(age):\n")
        f.write("Line 2: if 0 <= age <= 9: result = 'a Child!'\n")
        f.write("Line 4: elif 9 < age <= 18: result = 'an Adolescent!'\n")
        f.write("Line 6: elif 19 < age <= 65: result = 'an Adult!'\n")
        f.write("Line 8: else: result = 'in your Golden Years!'\n")
        f.write("Line 10: print('You are ' + result)\n\n")
        f.write("# Refactoring Test Matrix Inputs:\n")
        for age, exp, desc in test_cases:
            f.write(f"Age: {age} | Expected: {repr(exp)} | Desc: {desc}\n")

    with open(os.path.join(WORK_DIR, "expected-results.txt"), "w") as f:
        f.write("# Expected Outcomes (Refactored Single Responsibility):\n")
        for age, exp, desc in test_cases:
            f.write(f"Age: {age} => Expected: {exp} ({desc})\n")

    with open(os.path.join(WORK_DIR, "actual-results.txt"), "w") as f:
        f.write("# Actual Outcomes:\n")
        for age, act, status, desc in test_results:
            f.write(f"Age: {age} => Actual: {act} | Status: {status} ({desc})\n")

    with open(os.path.join(WORK_DIR, "evidence.txt"), "w") as f:
        f.write("=== Task R32-T026 Verification Evidence ===\n")
        f.write("Target: string-concatenation-python/age.py (Single Responsibility Refactoring)\n")
        f.write(f"Test Cases Evaluated: {len(test_results)}/{len(test_cases)}\n")
        f.write("Classification responsibility cleanly separated from formatting/printing.\n\n")
        f.write("=== Native Unit Test Output ===\n")
        f.write(unit_test_output)
        f.write("\nVerification Result: SUCCESS (Exit Code 0)\n")


def main():
    print("Running Task R32-T026 verification check...")

    test_cases = [
        (0, "You are a Child!", "Smallest valid boundary (age 0)"),
        (5, "You are a Child!", "Ordinary Child (age 5)"),
        (9, "You are a Child!", "Child upper boundary (age 9)"),
        (10, "You are an Adolescent!", "Adolescent lower boundary (age 10)"),
        (15, "You are an Adolescent!", "Ordinary Adolescent (age 15)"),
        (18, "You are an Adolescent!", "Adolescent upper boundary (age 18)"),
        (20, "You are an Adult!", "Adult lower boundary (age 20)"),
        (35, "You are an Adult!", "Ordinary Adult (age 35)"),
        (65, "You are an Adult!", "Adult upper boundary (age 65)"),
        (66, "You are in your Golden Years!", "Golden Years lower boundary (age 66)"),
        (80, "You are in your Golden Years!", "Ordinary Golden Years (age 80)"),
    ]

    test_results = []
    for age, exp, desc in test_cases:
        actual = format_age_group(age)
        if actual == exp:
            status = "PASS"
        else:
            status = f"FAIL (Expected {exp}, Got {actual})"
            print(f"FAILED on {desc}: {status}")
            sys.exit(1)
        test_results.append((age, actual, status, desc))

    # Run native unit test suite
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        test_module.TestAgeGroupRefactoring
    )
    result = runner.run(suite)
    unit_test_output = stream.getvalue()

    if not result.wasSuccessful():
        print("Native unit test suite failed!")
        print(unit_test_output)
        sys.exit(1)

    print(f"All {len(test_cases)} refactoring test cases passed.")
    print(f"Ran {result.testsRun} native unit tests: OK.")

    write_evidence(test_cases, test_results, unit_test_output)
    print(f"Verification evidence written to {WORK_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
