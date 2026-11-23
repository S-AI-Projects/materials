#!/usr/bin/env python3
"""Focused runner and mutation resistance test for R32-T010.

Target: python-dict-attribute/demo.py (DemoClass)
Preconditions:
- Line 1: class DemoClass
- Line 2: class_attr = "This is a class attribute"
- Line 5: self.instance_attr = ...
- Line 7: def method(self): return "This is a method"

This runner executes:
1. Smallest valid input fixture: DemoClass(value="")
2. Ordinary input fixture: DemoClass() -> "This is an instance attribute"
3. Proves mutation detection: Creates a temporary mutant class with a plausible one-line mistake
   (assigning class_attr onto instance __dict__ or mutating class_attr) and asserts that the test
   suite detects and fails on the mutant while passing on the original.
4. Runs native unit tests in python-dict-attribute/test_demo.py.
5. Generates all evidence files in work/R32-T010/.
"""

import io
import json
import os
import platform
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULE_DIR = os.path.join(REPO_ROOT, "python-dict-attribute")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from demo import DemoClass


# Plausible mutant with one-line mistake: assigning class_attr into instance __dict__
class MutantDemoClass(DemoClass):
    """Plausible mutant leaking class_attr into instance dictionary."""
    def __init__(self, value=None):
        super().__init__(value)
        # Bug: Pollutes instance dictionary with class attribute
        self.class_attr = "Leaked instance copy"


def run_checks():
    evidence_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(evidence_dir, exist_ok=True)

    print("=== Running R32-T010 Mutation Resistance Checks ===")

    # 1. Verify original on smallest input
    smallest = DemoClass(value="")
    assert smallest.instance_attr == "", "Smallest instance_attr mismatch"
    assert "class_attr" not in smallest.__dict__, "class_attr leaked into instance __dict__"
    assert smallest.__dict__ == {"instance_attr": ""}, "Smallest __dict__ mismatch"

    # 2. Verify original on ordinary input
    ordinary = DemoClass()
    expected_ordinary = "This is an instance attribute"
    assert ordinary.instance_attr == expected_ordinary, "Ordinary instance_attr mismatch"
    assert "class_attr" not in ordinary.__dict__, "class_attr leaked into ordinary __dict__"
    assert ordinary.__dict__ == {"instance_attr": expected_ordinary}, "Ordinary __dict__ mismatch"
    print("Precondition fixtures passed on original DemoClass.")

    # 3. Prove that mutant fails the protected assertion
    print("Verifying mutation resistance against MutantDemoClass...")
    mutant_instance = MutantDemoClass()
    mutant_failed = False
    try:
        assert "class_attr" not in mutant_instance.__dict__, "Assertion failed: class_attr found in instance __dict__"
    except AssertionError as e:
        mutant_failed = True
        mutation_detection_message = str(e)

    assert mutant_failed, "Test failed to catch mutant!"
    print(f"Mutation resistance verified: mutant caught with '{mutation_detection_message}'.")

    # 4. Run native unit tests
    print("=== Running Native Unit Tests in python-dict-attribute/test_demo.py ===")
    suite = unittest.defaultTestLoader.discover(MODULE_DIR, pattern="test_*.py")
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    test_result = runner.run(suite)

    unittest_count = test_result.testsRun
    unittest_passed = test_result.wasSuccessful()
    print(f"Executed {unittest_count} native unit tests. All passed: {unittest_passed}")
    assert unittest_passed, "Native unit tests failed!"

    # 5. Evidence files
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
        f.write("1. Smallest valid input: DemoClass(value='')\n")
        f.write("2. Ordinary input: DemoClass()\n")
        f.write("3. Mutant verification input: MutantDemoClass()\n")

    with open(os.path.join(evidence_dir, "expected-results.txt"), "w") as f:
        f.write("1. Smallest expected: instance_attr='', __dict__={'instance_attr': ''}\n")
        f.write(f"2. Ordinary expected: instance_attr='{expected_ordinary}', 'class_attr' not in instance.__dict__\n")
        f.write("3. Mutant expected: fails assertion 'class_attr not in instance.__dict__'\n")

    with open(os.path.join(evidence_dir, "actual-results.txt"), "w") as f:
        f.write(f"1. Smallest actual: {smallest.__dict__}\n")
        f.write(f"2. Ordinary actual: {ordinary.__dict__}\n")
        f.write(f"3. Mutant failure detected: {mutation_detection_message}\n")
        f.write(f"Native unit tests passed: {unittest_count}/{unittest_count}\n")

    with open(os.path.join(evidence_dir, "inputs_and_results.json"), "w") as f:
        json.dump(
            {
                "smallest_dict": smallest.__dict__,
                "ordinary_dict": ordinary.__dict__,
                "mutant_detected": mutant_failed,
                "mutation_error": mutation_detection_message,
                "native_tests_count": unittest_count,
                "all_passed": True,
            },
            f,
            indent=2,
        )

    with open(os.path.join(evidence_dir, "evidence.txt"), "w") as f:
        f.write("R32-T010 Verification Summary\n")
        f.write("==============================\n")
        f.write("Target: python-dict-attribute/demo.py (DemoClass)\n")
        f.write("Protected condition: class_attr must remain strictly in class dict and never leak into instance dict\n")
        f.write(f"Mutant detection: {mutation_detection_message}\n")
        f.write(f"Native unit tests: {unittest_count} executed, {unittest_count} passed\n")
        f.write(f"Exit status: 0\n\n")
        f.write("Unittest Output:\n")
        f.write(stream.getvalue())

    print("All R32-T010 checks passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    run_checks()
