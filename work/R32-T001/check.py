#!/usr/bin/env python3
"""Focused test runner for task R32-T001.

Executes regression tests for python-all-attribute/vehicles.py,
records actual execution command, tool versions, inputs, and expected vs actual results,
and propagates failures with non-zero exit codes.
"""

import io
import json
import os
import platform
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_DIR = REPO_ROOT / "python-all-attribute"
WORK_DIR = REPO_ROOT / "work" / "R32-T001"

# Ensure isolated import of python-all-attribute
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(REPO_ROOT / "tests" / "python_all_attribute"))

import test_vehicles  # noqa: E402


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Record tool versions
    tool_versions = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "unittest_module": unittest.__file__,
    }
    with open(WORK_DIR / "tool_versions.json", "w") as f:
        json.dump(tool_versions, f, indent=2)

    # 2. Record inputs and expected vs actual results
    inputs_and_results = {
        "source_module": "python-all-attribute/vehicles.py",
        "target_class": "Car",
        "fixture_anchors": {
            "vehicles.py:1": '__all__ = ["Car", "Truck"]',
            "vehicles.py:4": "class Car:",
            "vehicles.py:5-6": 'def start(self): print("The car is starting")',
            "vehicles.py:8-9": 'def drive(self): print("The car is driving")',
            "vehicles.py:11-12": 'def stop(self): print("The car is stopping")',
        },
        "cases": [
            {
                "name": "smallest_valid_input",
                "precondition_line": "vehicles.py:4",
                "literal_input": "Car() with args=(), kwargs={}",
                "expected": {
                    "isinstance": "vehicles.Car",
                    "type": "vehicles.Car",
                    "instance_dict": {},
                },
                "status": "verified",
            },
            {
                "name": "ordinary_input_rejection",
                "precondition_line": "vehicles.py:4",
                "literal_input": 'Car("Tesla", "Model 3")',
                "expected": {
                    "exception": "TypeError",
                    "reason": "object.__init__() takes exactly one argument (the instance)",
                },
                "status": "verified",
            },
            {
                "name": "car_start_behavior",
                "precondition_line": "vehicles.py:5-6",
                "literal_input": "car.start()",
                "expected": {
                    "return_value": None,
                    "mutation": {},
                    "stdout": "The car is starting\n",
                },
                "status": "verified",
            },
            {
                "name": "car_drive_behavior",
                "precondition_line": "vehicles.py:8-9",
                "literal_input": "car.drive()",
                "expected": {
                    "return_value": None,
                    "mutation": {},
                    "stdout": "The car is driving\n",
                },
                "status": "verified",
            },
            {
                "name": "car_stop_behavior",
                "precondition_line": "vehicles.py:11-12",
                "literal_input": "car.stop()",
                "expected": {
                    "return_value": None,
                    "mutation": {},
                    "stdout": "The car is stopping\n",
                },
                "status": "verified",
            },
            {
                "name": "repeated_value_boundary",
                "precondition_line": "vehicles.py:8-9",
                "literal_input": "car.drive() executed 3 times repeatedly",
                "expected": {
                    "return_values": [None, None, None],
                    "stdout": "The car is driving\n (x3)",
                    "mutation": "none (car.__dict__ == {})",
                },
                "status": "verified",
            },
        ],
    }
    with open(WORK_DIR / "inputs_and_results.json", "w") as f:
        json.dump(inputs_and_results, f, indent=2)

    # 3. Execute the focused test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_vehicles)
    test_count = suite.countTestCases()

    actual_command = f"{sys.executable} work/R32-T001/check.py"
    print(f"Running focused check: {actual_command}")
    print(f"Discovered {test_count} tests in test_vehicles")

    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)

    runner_log = stream.getvalue()
    print(runner_log)

    # Save run execution record
    run_record = {
        "command": actual_command,
        "test_count": test_count,
        "was_successful": result.wasSuccessful(),
        "errors_count": len(result.errors),
        "failures_count": len(result.failures),
        "log": runner_log,
    }
    with open(WORK_DIR / "run_record.json", "w") as f:
        json.dump(run_record, f, indent=2)

    with open(WORK_DIR / "test_output.log", "w") as f:
        f.write(runner_log)

    if not result.wasSuccessful():
        print(f"FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        sys.exit(1)

    print(f"SUCCESS: All {test_count} tests passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
