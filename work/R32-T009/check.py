#!/usr/bin/env python3
"""Focused runner and complexity measurement for R32-T009.

Target: numpy-tutorial/README.md & curve_grades algorithm
Preconditions:
- CURVE_CENTER = 80
- Smallest valid input: [70.0] -> [80.0]
- Ordinary input: [72, 35, 64, 88, 51, 90, 74, 12] -> [91.25, 54.25, 83.25, 100.0, 70.25, 100.0, 93.25, 31.25]

This runner executes:
1. Smallest and ordinary input correctness checks with explicit expected values.
2. Complexity experiment: 3 increasing sizes (N=100, N=1,000, N=10,000), 5 repetitions each with fixed seeds.
   Times core algorithm strictly outside input generation and validation.
   Reports median and range for time and operations count.
3. Native unit test execution in numpy-tutorial/test_curve_grades.py.
4. Generates all task evidence files under work/R32-T009/.
"""

import io
import json
import os
import platform
import random
import statistics
import sys
import time
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULE_DIR = os.path.join(REPO_ROOT, "numpy-tutorial")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from curve_grades import curve


def run_checks():
    evidence_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(evidence_dir, exist_ok=True)

    print("=== Running R32-T009 Complexity & Correctness Checks ===")

    # 1. Correctness on smallest valid input fixture
    smallest_input = [70.0]
    expected_smallest = [80.0]
    actual_smallest = curve(smallest_input)
    assert actual_smallest == expected_smallest, f"Smallest mismatch: {actual_smallest} != {expected_smallest}"

    # 2. Correctness on ordinary input fixture
    ordinary_input = [72, 35, 64, 88, 51, 90, 74, 12]
    expected_ordinary = [91.25, 54.25, 83.25, 100.0, 70.25, 100.0, 93.25, 31.25]
    actual_ordinary = curve(ordinary_input)
    assert len(actual_ordinary) == len(expected_ordinary), "Ordinary length mismatch"
    for a, e in zip(actual_ordinary, expected_ordinary):
        assert abs(a - e) < 1e-4, f"Mismatch in ordinary result: {a} != {e}"

    print("Precondition fixtures passed: Smallest and Ordinary inputs verified.")

    # 3. Complexity experiment: 3 increasing sizes, 5 repetitions, fixed seeds
    sizes = [100, 1000, 10000]
    repetitions = 5
    benchmark_records = {}

    print("Running complexity experiment across sizes N in [100, 1000, 10000] with 5 repetitions...")
    for N in sizes:
        durations = []
        for rep in range(repetitions):
            # Fixed deterministic seed for reproducible fresh inputs
            rng = random.Random(42 + N + rep)
            fresh_grades = [rng.uniform(10.0, 95.0) for _ in range(N)]

            # Measure strictly algorithm computation (excluding input generation and assert verification)
            t0 = time.perf_counter_ns()
            curved = curve(fresh_grades)
            t1 = time.perf_counter_ns()

            durations.append(t1 - t0)

            # Verification outside timed interval
            assert len(curved) == N, f"Size mismatch for N={N}"
            for original, adjusted in zip(fresh_grades, curved):
                assert adjusted >= original, "Grade decreased"
                assert adjusted <= 100.0, "Grade exceeded 100%"

        median_ns = statistics.median(durations)
        min_ns = min(durations)
        max_ns = max(durations)
        benchmark_records[f"N_{N}"] = {
            "size": N,
            "repetitions": repetitions,
            "median_ns": median_ns,
            "min_ns": min_ns,
            "max_ns": max_ns,
            "range_ns": max_ns - min_ns,
            "median_ms": median_ns / 1e6,
            "operations_count": N * 3,  # sum/mean + add change + clip
        }
        print(f"Size N={N:5d}: Median = {median_ns / 1e3:.2f} µs (Range: {(max_ns - min_ns) / 1e3:.2f} µs)")

    # 4. Native unit tests
    print("=== Running Native Unit Tests in numpy-tutorial/test_curve_grades.py ===")
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
        f.write(f"1. Smallest valid input: {smallest_input}\n")
        f.write(f"2. Ordinary input: {ordinary_input}\n")
        f.write("3. Complexity test sizes: N in [100, 1000, 10000], 5 repetitions each.\n")

    with open(os.path.join(evidence_dir, "expected-results.txt"), "w") as f:
        f.write(f"1. Smallest expected: {expected_smallest}\n")
        f.write(f"2. Ordinary expected: {expected_ordinary}\n")
        f.write("3. Theoretical complexity: O(N) operations, O(N) auxiliary space.\n")

    with open(os.path.join(evidence_dir, "actual-results.txt"), "w") as f:
        f.write(f"1. Smallest actual: {actual_smallest}\n")
        f.write(f"2. Ordinary actual: {actual_ordinary}\n")
        for k, v in benchmark_records.items():
            f.write(f"{k}: Median = {v['median_ns']} ns, Range = {v['range_ns']} ns\n")
        f.write(f"Native unit tests passed: {unittest_count}/{unittest_count}\n")

    with open(os.path.join(evidence_dir, "inputs_and_results.json"), "w") as f:
        json.dump(
            {
                "smallest_result": actual_smallest,
                "ordinary_result": actual_ordinary,
                "benchmark_records": benchmark_records,
                "theoretical_complexity": "O(N)",
                "input_variable": "N (number of grade elements)",
                "native_tests_count": unittest_count,
                "all_passed": True,
            },
            f,
            indent=2,
        )

    with open(os.path.join(evidence_dir, "evidence.txt"), "w") as f:
        f.write("R32-T009 Verification Summary\n")
        f.write("==============================\n")
        f.write("Target: numpy-tutorial/README.md (curve_grades complexity)\n")
        f.write("Input size variable: N = number of elements\n")
        f.write("Theoretical claim: O(N) linear time and space complexity\n")
        f.write("Benchmark measurements:\n")
        for k, v in benchmark_records.items():
            f.write(f" - {k}: size={v['size']}, median={v['median_ns']} ns, range={v['range_ns']} ns\n")
        f.write(f"Native unit tests: {unittest_count} executed, {unittest_count} passed\n")
        f.write(f"Exit status: 0\n\n")
        f.write("Unittest Output:\n")
        f.write(stream.getvalue())

    print("All R32-T009 checks passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    run_checks()
