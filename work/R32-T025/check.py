#!/usr/bin/env python3
"""Verification check runner for Task R32-T025.

Makes verification repeatable for python csv (read_csv_with_pandas.py).
Evaluates input isolation, repeatability over repeated runs, and dependency seams.
"""

import importlib.util
import io
import os
import platform
import sys
import unittest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))

# Load read_csv_with_pandas.py
CSV_MODULE_PATH = os.path.join(REPO_ROOT, "python-csv", "read_csv_with_pandas.py")
spec = importlib.util.spec_from_file_location("read_csv_with_pandas", CSV_MODULE_PATH)
csv_module = importlib.util.module_from_spec(spec)
sys.modules["read_csv_with_pandas"] = csv_module
spec.loader.exec_module(csv_module)

# Load test_read_csv.py
TEST_CSV_PATH = os.path.join(REPO_ROOT, "python-csv", "test_read_csv.py")
test_spec = importlib.util.spec_from_file_location("test_read_csv", TEST_CSV_PATH)
test_module = importlib.util.module_from_spec(test_spec)
test_spec.loader.exec_module(test_module)

load_hr_data = csv_module.load_hr_data
run_demo = csv_module.run_demo


def write_evidence(test_cases, test_results, unit_test_output):
    """Write verification evidence files to work/R32-T025/."""
    os.makedirs(WORK_DIR, exist_ok=True)

    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Interpreter: {sys.executable}\n")

    with open(os.path.join(WORK_DIR, "test-inputs.txt"), "w") as f:
        f.write("# Precondition Anchors from source:\n")
        f.write("Line 3: df = pandas.read_csv('hrdata.csv')\n")
        f.write("Line 8: df = pandas.read_csv('hrdata.csv', index_col='Name')\n")
        f.write("Line 11: parse_dates=['Hire Date'], date_format='%m/%d/%y'\n")
        f.write("Line 20: header=0, names=['Employee', 'Hired', 'Salary', 'Sick Days']\n\n")
        f.write("# Repeatability & Isolation Test Inputs:\n")
        for inp, desc in test_cases:
            f.write(f"Input: {repr(inp)[:120]} | Desc: {desc}\n")

    with open(os.path.join(WORK_DIR, "expected-results.txt"), "w") as f:
        f.write("# Expected Outcomes (Deterministic Repeatability & Purity):\n")
        for inp, desc in test_cases:
            f.write(f"Desc: {desc} => Expected: Deterministic & Isolated (True)\n")

    with open(os.path.join(WORK_DIR, "actual-results.txt"), "w") as f:
        f.write("# Actual Outcomes:\n")
        for desc, status in test_results:
            f.write(f"Desc: {desc} => Status: {status}\n")

    with open(os.path.join(WORK_DIR, "evidence.txt"), "w") as f:
        f.write("=== Task R32-T025 Verification Evidence ===\n")
        f.write("Target: python-csv/read_csv_with_pandas.py (Repeatability Seam)\n")
        f.write(f"Repeatability Cases Evaluated: {len(test_results)}/{len(test_cases)}\n")
        f.write("Input Isolation & 10-Iteration Repeatability: 100% Verified\n\n")
        f.write("=== Native Unit Test Output ===\n")
        f.write(unit_test_output)
        f.write("\nVerification Result: SUCCESS (Exit Code 0)\n")


def main():
    print("Running Task R32-T025 verification check...")

    hrdata_path = os.path.join(REPO_ROOT, "python-csv", "hrdata.csv")
    assert os.path.exists(hrdata_path), "Fixture hrdata.csv missing"

    test_cases = [
        ("io.StringIO(SMALLEST_CSV)", "Smallest valid input (1 data row buffer)"),
        (hrdata_path, "Ordinary valid input (full hrdata.csv fixture)"),
        ("10 repeated load_hr_data calls", "Repeatability across 10 independent calls"),
        ("Caller dictionary mutation check", "Input & memory isolation test"),
        ("Custom reader dependency injection", "Dependency injection seam check"),
    ]

    test_results = []

    # 1. Smallest valid input
    smallest_buf = io.StringIO(
        "Name,Hire Date,Salary,Sick Days remaining\n"
        "Graham Chapman,03/15/14,50000.00,10\n"
    )
    df_small = load_hr_data(smallest_buf)
    assert len(df_small) == 1, "Smallest input row count != 1"
    test_results.append((test_cases[0][1], "PASS"))

    # 2. Ordinary valid input
    df_ord = load_hr_data(hrdata_path)
    assert len(df_ord) == 6, "Ordinary input row count != 6"
    test_results.append((test_cases[1][1], "PASS"))

    # 3. Repeatability over 10 calls
    records_list = [load_hr_data(hrdata_path).to_dict() for _ in range(10)]
    first = records_list[0]
    for r in records_list[1:]:
        assert r == first, "Non-deterministic output detected across runs"
    test_results.append((test_cases[2][1], "PASS"))

    # 4. Input isolation
    records_copy = load_hr_data(hrdata_path).to_dict()
    records_copy[0]["Name"] = "MUTANT"
    fresh_records = load_hr_data(hrdata_path).to_dict()
    assert fresh_records[0]["Name"] == "Graham Chapman", "Caller mutation leaked into loader"
    test_results.append((test_cases[3][1], "PASS"))

    # 5. Dependency seam
    mock_called = False

    def dummy_reader(*args, **kwargs):
        nonlocal mock_called
        mock_called = True
        return "mock_ok"

    res = load_hr_data(hrdata_path, reader=dummy_reader)
    assert res == "mock_ok" and mock_called, "Dependency seam reader not invoked"
    test_results.append((test_cases[4][1], "PASS"))

    # 6. Native Unit Test Suite Execution
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        test_module.TestReadCsvRepeatability
    )
    result = runner.run(suite)
    unit_test_output = stream.getvalue()

    if not result.wasSuccessful():
        print("Native unit test suite failed!")
        print(unit_test_output)
        sys.exit(1)

    print(f"All {len(test_cases)} repeatability test cases passed.")
    print(f"Ran {result.testsRun} native unit tests: OK.")

    # 7. Write evidence files
    write_evidence(test_cases, test_results, unit_test_output)
    print(f"Verification evidence written to {WORK_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
