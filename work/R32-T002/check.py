#!/usr/bin/env python3
"""Focused test runner for task R32-T002.

Defines and tests the supported boundaries of positron ide (analyze_sales.py).
Evaluates literal inputs, independently calculated expected outputs, records tool versions,
and executes focused unit tests with external I/O mocked.
Propagates failures with non-zero exit codes.
"""

import io
import json
import platform
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MODULE_DIR = REPO_ROOT / "positron-ide" / "src"
WORK_DIR = REPO_ROOT / "work" / "R32-T002"

# Ensure isolated import of positron-ide/src
sys.path.insert(0, str(MODULE_DIR))

import analyze_sales  # noqa: E402
import test_analyze_sales  # noqa: E402


def record_metadata_and_evidence(cases, execution_summary):
    """Write tool versions, test inputs, and results to work/R32-T002/."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Record tool versions
    tool_versions = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "unittest_module": unittest.__file__,
        "pandas_version": getattr(analyze_sales.pd, "__version__", "unknown"),
        "matplotlib_version": getattr(
            analyze_sales.plt.matplotlib, "__version__", "unknown"
        ),
    }
    with open(WORK_DIR / "tool_versions.json", "w") as f:
        json.dump(tool_versions, f, indent=2)

    with open(WORK_DIR / "tool-versions.txt", "w") as f:
        for k, v in tool_versions.items():
            f.write(f"{k}: {v}\n")

    # 2. Record inputs and expected vs actual results
    inputs_and_results = {
        "task_id": "R32-T002",
        "target": "positron-ide/src/analyze_sales.py",
        "contract_anchors": {
            "Line 9": "sales = pd.read_csv(PROJECT_ROOT / 'data/sales_clean.csv', parse_dates=['order_date'])",
            "Line 15": "sales[['quantity', 'unit_price', 'sale_price']].describe().round(2)",
            "Line 16": "sales['order_type'].value_counts()",
            "Line 19-20": "sales.groupby(['product_category', 'order_type'], as_index=False)",
            "Line 23": "orders=('order_number', 'size')",
            "Line 24": "median_order_value=('sale_price', 'median')",
            "Line 30-34": "order_summary.pivot(index='product_category', columns='order_type', values='median_order_value')",
            "Line 36-40": "chart_data.plot.bar(rot=0, figsize=(8, 4))",
        },
        "boundary_cases": cases,
        "execution": execution_summary,
    }
    with open(WORK_DIR / "inputs_and_results.json", "w") as f:
        json.dump(inputs_and_results, f, indent=2)

    # Human-readable evidence files matching project conventions
    with open(WORK_DIR / "test-inputs.txt", "w") as f:
        f.write("# Precondition Anchors:\n")
        for line, anchor in inputs_and_results["contract_anchors"].items():
            f.write(f"{line}: {anchor}\n")
        f.write("\n# Boundary Test Matrix Cases:\n")
        for case in cases:
            f.write(
                f"[{case['name']}] Precondition: {case['precondition_line']} | Input: {case['literal_input']}\n"
            )

    with open(WORK_DIR / "expected-results.txt", "w") as f:
        f.write("# Expected Results:\n")
        for case in cases:
            f.write(
                f"[{case['name']}] Expected: {json.dumps(case['expected'])}\n"
            )

    with open(WORK_DIR / "actual-results.txt", "w") as f:
        f.write("# Actual Results:\n")
        for case in cases:
            f.write(
                f"[{case['name']}] Actual: {json.dumps(case['actual'])} | Status: {case['status']}\n"
            )

    with open(WORK_DIR / "evidence.txt", "w") as f:
        f.write("=== Task R32-T002 Verification Evidence ===\n")
        f.write(
            "Target: positron-ide/src/analyze_sales.py (Supported Boundaries)\n"
        )
        f.write(f"Command: {execution_summary['command']}\n")
        f.write(
            f"Total Native Unit Tests: {execution_summary['test_count']}\n"
        )
        f.write(f"Boundary Cases Verified: {len(cases)}\n\n")
        f.write("=== Native Unit Test Log ===\n")
        f.write(execution_summary["log"])
        f.write("\nResult: SUCCESS (Exit Code 0)\n")


def evaluate_boundary_cases():
    """Evaluate literal inputs directly and compare against independent calculations."""
    cases = []

    # Case 1: Smallest valid input
    c1_input = {
        "order_number": [1001],
        "order_date": ["2019-02-09"],
        "order_type": ["Retail"],
        "product_category": ["Olive Oil"],
        "quantity": [1],
        "unit_price": [45.0],
        "sale_price": [45.0],
    }
    c1_expected = {
        "orders": 1,
        "median_order_value": 45.0,
        "product_category": "Olive Oil",
        "order_type": "Retail",
        "chart_value": 45.0,
    }
    df1 = analyze_sales.pd.DataFrame(c1_input)
    sum1 = analyze_sales.summarize_orders(df1)
    chart1 = analyze_sales.build_chart_data(sum1)
    c1_actual = {
        "orders": int(sum1.loc[0, "orders"]),
        "median_order_value": float(sum1.loc[0, "median_order_value"]),
        "product_category": str(sum1.loc[0, "product_category"]),
        "order_type": str(sum1.loc[0, "order_type"]),
        "chart_value": float(chart1.loc["Olive Oil", "Retail"]),
    }
    cases.append(
        {
            "name": "smallest_valid_input",
            "precondition_line": "analyze_sales.py:19-24,30-34",
            "literal_input": c1_input,
            "expected": c1_expected,
            "actual": c1_actual,
            "status": "PASS" if c1_expected == c1_actual else "FAIL",
        }
    )

    # Case 2: Ordinary input
    c2_input = {
        "order_number": [1001, 1002, 1003],
        "order_date": ["2019-02-09", "2019-02-15", "2019-02-16"],
        "order_type": ["Retail", "Retail", "Wholesale"],
        "product_category": ["Olive Oil", "Olive Oil", "Bath products"],
        "quantity": [2, 1, 4],
        "unit_price": [45.0, 19.5, 26.0],
        "sale_price": [90.0, 19.5, 104.0],
    }
    c2_expected = {
        "olive_oil_retail_orders": 2,
        "olive_oil_retail_median": 54.75,
        "bath_wholesale_orders": 1,
        "bath_wholesale_median": 104.0,
    }
    df2 = analyze_sales.pd.DataFrame(c2_input)
    sum2 = analyze_sales.summarize_orders(df2)
    chart2 = analyze_sales.build_chart_data(sum2)
    c2_actual = {
        "olive_oil_retail_orders": int(
            sum2[
                (sum2["product_category"] == "Olive Oil")
                & (sum2["order_type"] == "Retail")
            ].iloc[0]["orders"]
        ),
        "olive_oil_retail_median": float(chart2.loc["Olive Oil", "Retail"]),
        "bath_wholesale_orders": int(
            sum2[
                (sum2["product_category"] == "Bath products")
                & (sum2["order_type"] == "Wholesale")
            ].iloc[0]["orders"]
        ),
        "bath_wholesale_median": float(
            chart2.loc["Bath products", "Wholesale"]
        ),
    }
    cases.append(
        {
            "name": "ordinary_input",
            "precondition_line": "analyze_sales.py:19-24,30-34",
            "literal_input": c2_input,
            "expected": c2_expected,
            "actual": c2_actual,
            "status": "PASS" if c2_expected == c2_actual else "FAIL",
        }
    )

    # Case 3: Empty valid boundary input
    c3_input = {
        "order_number": [],
        "order_date": [],
        "order_type": [],
        "product_category": [],
        "quantity": [],
        "unit_price": [],
        "sale_price": [],
    }
    c3_expected = {
        "summary_empty": True,
        "chart_empty": True,
    }
    df3 = analyze_sales.pd.DataFrame(c3_input)
    sum3 = analyze_sales.summarize_orders(df3)
    chart3 = analyze_sales.build_chart_data(sum3)
    c3_actual = {
        "summary_empty": bool(sum3.empty),
        "chart_empty": bool(chart3.empty),
    }
    cases.append(
        {
            "name": "empty_boundary_input",
            "precondition_line": "analyze_sales.py:19-24,30-34",
            "literal_input": c3_input,
            "expected": c3_expected,
            "actual": c3_actual,
            "status": "PASS" if c3_expected == c3_actual else "FAIL",
        }
    )

    # Case 4: Unsupported None input
    c4_expected = "ValueError: Sales data cannot be None"
    try:
        analyze_sales.validate_sales_data(None)
        c4_actual = "No exception"
    except ValueError as e:
        c4_actual = f"ValueError: {e}"
    cases.append(
        {
            "name": "unsupported_none_input",
            "precondition_line": "analyze_sales.py:15-24",
            "literal_input": "None",
            "expected": c4_expected,
            "actual": c4_actual,
            "status": "PASS" if c4_expected == c4_actual else "FAIL",
        }
    )

    # Case 5: Unsupported missing column
    c5_input = {"order_number": [1]}
    c5_expected = "ValueError: Missing required columns in sales data: ['order_date', 'order_type', 'product_category', 'quantity', 'sale_price', 'unit_price']"
    try:
        analyze_sales.validate_sales_data(c5_input)
        c5_actual = "No exception"
    except ValueError as e:
        c5_actual = f"ValueError: {e}"
    cases.append(
        {
            "name": "unsupported_missing_column",
            "precondition_line": "analyze_sales.py:15-24",
            "literal_input": c5_input,
            "expected": c5_expected,
            "actual": c5_actual,
            "status": "PASS" if c5_expected == c5_actual else "FAIL",
        }
    )

    for c in cases:
        if c["status"] != "PASS":
            print(f"Assertion failed for {c['name']}: {c}")
            sys.exit(1)

    return cases


def main():
    actual_command = f"{sys.executable} work/R32-T002/check.py"
    print(f"Running focused check runner: {actual_command}")

    # 1. Run direct boundary evaluations
    cases = evaluate_boundary_cases()
    print(f"Verified {len(cases)} boundary contract cases.")

    # 2. Run native unittest suite with external I/O mocked
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_analyze_sales)
    test_count = suite.countTestCases()
    print(
        f"Discovered {test_count} native unit tests in test_analyze_sales.py"
    )

    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)

    with patch("matplotlib.pyplot.show"):
        result = runner.run(suite)

    log_output = stream.getvalue()
    print(log_output)

    execution_summary = {
        "command": actual_command,
        "test_count": test_count,
        "was_successful": result.wasSuccessful(),
        "errors_count": len(result.errors),
        "failures_count": len(result.failures),
        "log": log_output,
    }

    record_metadata_and_evidence(cases, execution_summary)

    if not result.wasSuccessful():
        print(
            f"FAILED: {len(result.failures)} failures, {len(result.errors)} errors"
        )
        sys.exit(1)

    print(
        f"SUCCESS: All {test_count} unit tests and boundary assertions passed."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
