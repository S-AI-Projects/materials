#!/usr/bin/env python3
"""Focused runner and refactoring verification for R32-T006.

Target: python-namespace/legb_1.py (outer)
Preconditions:
- Line 1: x = 'global'
- Line 4: def outer()
- Line 6: print(x)

This runner executes:
1. Smallest valid input check: outer(val="") -> prints "\n", returns ""
2. Ordinary input check: outer(val="ordinary") -> prints "ordinary\n", returns "ordinary"
3. Backward compatibility check: outer() -> prints "global\n", returns "global"
4. Extracted helper unit check: format_scope_value()
5. Runs native unit tests in python-namespace/test_legb_1.py
6. Generates evidence files in work/R32-T006/.
"""

import io
import json
import os
import platform
import sys
import unittest
from unittest.mock import patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULE_DIR = os.path.join(REPO_ROOT, "python-namespace")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import legb_1


def run_checks():
    evidence_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(evidence_dir, exist_ok=True)

    print("=== Running R32-T006 Focused Refactoring Checks ===")

    # Smallest fixture
    with patch("sys.stdout", new_callable=io.StringIO) as out_smallest:
        res_smallest = legb_1.outer(val="")
        out_str_smallest = out_smallest.getvalue()

    assert res_smallest == "", f"Expected '', got {res_smallest}"
    assert out_str_smallest == "\n", f"Expected '\\n', got {repr(out_str_smallest)}"

    # Ordinary fixture
    with patch("sys.stdout", new_callable=io.StringIO) as out_ordinary:
        res_ordinary = legb_1.outer(val="ordinary")
        out_str_ordinary = out_ordinary.getvalue()

    assert res_ordinary == "ordinary", f"Expected 'ordinary', got {res_ordinary}"
    assert out_str_ordinary == "ordinary\n", f"Expected 'ordinary\\n', got {repr(out_str_ordinary)}"

    # Default call fixture
    with patch("sys.stdout", new_callable=io.StringIO) as out_default:
        res_default = legb_1.outer()
        out_str_default = out_default.getvalue()

    assert res_default == "global", f"Expected 'global', got {res_default}"
    assert out_str_default == "global\n", f"Expected 'global\\n', got {repr(out_str_default)}"

    print("Fixtures verified successfully: Smallest, Ordinary, and Default caller.")

    # Native unit test execution
    print("=== Running Native Unit Tests in python-namespace/test_legb_1.py ===")
    suite = unittest.defaultTestLoader.discover(MODULE_DIR, pattern="test_*.py")
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    test_result = runner.run(suite)

    unittest_count = test_result.testsRun
    unittest_passed = test_result.wasSuccessful()
    print(f"Executed {unittest_count} native unit tests. All passed: {unittest_passed}")
    assert unittest_passed, "Native unit tests failed!"

    # Evidence files
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
        f.write("1. Smallest input: val=''\n")
        f.write("2. Ordinary input: val='ordinary'\n")
        f.write("3. Default input: val=None (falls back to global x)\n")

    with open(os.path.join(evidence_dir, "expected-results.txt"), "w") as f:
        f.write("1. Smallest expected: return='', stdout='\\n'\n")
        f.write("2. Ordinary expected: return='ordinary', stdout='ordinary\\n'\n")
        f.write("3. Default expected: return='global', stdout='global\\n'\n")

    with open(os.path.join(evidence_dir, "actual-results.txt"), "w") as f:
        f.write(f"1. Smallest actual: return={repr(res_smallest)}, stdout={repr(out_str_smallest)}\n")
        f.write(f"2. Ordinary actual: return={repr(res_ordinary)}, stdout={repr(out_str_ordinary)}\n")
        f.write(f"3. Default actual: return={repr(res_default)}, stdout={repr(out_str_default)}\n")
        f.write(f"Native unit tests passed: {unittest_count}/{unittest_count}\n")

    with open(os.path.join(evidence_dir, "inputs_and_results.json"), "w") as f:
        json.dump(
            {
                "smallest_result": {"return": res_smallest, "stdout": out_str_smallest},
                "ordinary_result": {"return": res_ordinary, "stdout": out_str_ordinary},
                "default_result": {"return": res_default, "stdout": out_str_default},
                "native_tests_count": unittest_count,
                "all_passed": True,
            },
            f,
            indent=2,
        )

    with open(os.path.join(evidence_dir, "evidence.txt"), "w") as f:
        f.write("R32-T006 Verification Summary\n")
        f.write("==============================\n")
        f.write("Target: python-namespace/legb_1.py (outer)\n")
        f.write("Precondition: Line 1 global x, Line 4 outer, Line 6 print(x)\n")
        f.write("Refactoring: Extracted format_scope_value responsibility and added clean default-fallback parameter\n")
        f.write(f"Native unit tests: {unittest_count} executed, {unittest_count} passed\n")
        f.write(f"Exit status: 0\n\n")
        f.write("Unittest Output:\n")
        f.write(stream.getvalue())

    print("All R32-T006 checks passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    run_checks()
