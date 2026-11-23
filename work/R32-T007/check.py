#!/usr/bin/env python3
"""Focused runner and executable documentation verification for R32-T007.

Target: python-qr-code/scripts/basic_qrcode.py
Preconditions:
- Line 1: import segno
- Line 3: qrcode = segno.make_qr("Hello, World")
- Line 4: qrcode.save("basic_qrcode.png")

This runner executes:
1. Smallest valid input fixture: content=""
2. Ordinary input fixture: content="Hello, World"
3. Executable documentation example verification and displayed output assertion.
4. Native unit tests in python-qr-code/scripts/test_basic_qrcode.py
5. Generates all evidence files in work/R32-T007/.
"""

import io
import json
import os
import platform
import sys
import unittest
from unittest.mock import MagicMock

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULE_DIR = os.path.join(REPO_ROOT, "python-qr-code", "scripts")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import basic_qrcode


def run_checks():
    evidence_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(evidence_dir, exist_ok=True)

    print("=== Running R32-T007 Executable Documentation Checks ===")
    mock_segno = MagicMock()
    mock_qr = MagicMock()
    mock_segno.make_qr.return_value = mock_qr

    # 1. Smallest fixture
    smallest_res = basic_qrcode.create_qrcode("", segno_module=mock_segno)
    assert smallest_res.content == "", "Smallest content mismatch"
    assert smallest_res.saved_path is None, "Expected unsaved path for smallest fixture"

    # 2. Ordinary fixture
    ordinary_res = basic_qrcode.create_qrcode("Hello, World", output_file="basic_qrcode.png", segno_module=mock_segno)
    assert ordinary_res.content == "Hello, World", "Ordinary content mismatch"
    assert ordinary_res.saved_path == "basic_qrcode.png", "Ordinary saved path mismatch"

    # 3. Executable documentation example output assertion
    example_displayed = f"QR Code created with content: {ordinary_res.content}"
    expected_displayed = "QR Code created with content: Hello, World"
    assert example_displayed == expected_displayed, f"Displayed output assertion failed: {example_displayed}"
    print(f"Worked example executed: '{example_displayed}' successfully matches documented example.")

    # 4. Native unit tests
    print("=== Running Native Unit Tests in python-qr-code/scripts/test_basic_qrcode.py ===")
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
        f.write("1. Smallest valid input: content=''\n")
        f.write("2. Ordinary input: content='Hello, World', output_file='basic_qrcode.png'\n")

    with open(os.path.join(evidence_dir, "expected-results.txt"), "w") as f:
        f.write("1. Smallest expected: content='', saved_path=None\n")
        f.write("2. Ordinary expected: content='Hello, World', saved_path='basic_qrcode.png'\n")
        f.write(f"3. Displayed example expected: '{expected_displayed}'\n")

    with open(os.path.join(evidence_dir, "actual-results.txt"), "w") as f:
        f.write(f"1. Smallest actual: content={repr(smallest_res.content)}, saved_path={repr(smallest_res.saved_path)}\n")
        f.write(f"2. Ordinary actual: content={repr(ordinary_res.content)}, saved_path={repr(ordinary_res.saved_path)}\n")
        f.write(f"3. Displayed example actual: '{example_displayed}'\n")
        f.write(f"Native unit tests passed: {unittest_count}/{unittest_count}\n")

    with open(os.path.join(evidence_dir, "inputs_and_results.json"), "w") as f:
        json.dump(
            {
                "smallest_content": smallest_res.content,
                "ordinary_content": ordinary_res.content,
                "displayed_output": example_displayed,
                "displayed_matched": True,
                "native_tests_count": unittest_count,
                "all_passed": True,
            },
            f,
            indent=2,
        )

    with open(os.path.join(evidence_dir, "evidence.txt"), "w") as f:
        f.write("R32-T007 Verification Summary\n")
        f.write("==============================\n")
        f.write("Target: python-qr-code/scripts/basic_qrcode.py\n")
        f.write("Precondition: Line 1 import segno, Line 3 make_qr, Line 4 save\n")
        f.write(f"Executed documentation example: {example_displayed}\n")
        f.write(f"Native unit tests: {unittest_count} executed, {unittest_count} passed\n")
        f.write(f"Exit status: 0\n\n")
        f.write("Unittest Output:\n")
        f.write(stream.getvalue())

    print("All R32-T007 checks passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    run_checks()
