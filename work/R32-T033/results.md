# R32-T033 — Test Results

## Execution Commands

### 1. Independent Checker
Command:
```sh
python3 work/R32-T033/check.py
```
Output:
```text
=== Running R32-T033 Independent Checker ===
Python executable: /Library/Developer/CommandLineTools/usr/bin/python3
Python version: 3.9.6
Testing target: live_table.make_table
Total test cases: 22

[CASE-01] PASS: Empty input boundary (rows=0)
[CASE-02] PASS: Neutral percentage (0.0%) (rows=1)
[CASE-03] PASS: Positive threshold boundary (5.0%) (rows=1)
[CASE-04] PASS: Positive threshold crossed (5.1%) (rows=1)
[CASE-05] PASS: Ordinary strong positive gain (12.4%) (rows=1)
[CASE-06] PASS: Negative threshold boundary (-5.0%) (rows=1)
[CASE-07] PASS: Negative threshold crossed (-5.1%) (rows=1)
[CASE-08] PASS: Large negative loss (-35.8%) (rows=1)
[CASE-09] PASS: Zero volume and int 0 percent (rows=1)
[CASE-10] PASS: Large integer volume (rows=1)
[CASE-11] PASS: Tuple input (iterable protocol) (rows=1)
[CASE-12] PASS: Sequential ordering (A, B, C) (rows=3)
[CASE-13] PASS: Reversed ordering (C, B, A) (rows=3)
[CASE-14] PASS: Input mutation check (rows=1)
[CASE-15] PASS: Positive interior (+4.9%) (rows=1)
[CASE-16] PASS: Negative interior (-4.9%) (rows=1)
[CASE-17] PASS: Large positive gain over 100% (+150.5%) (rows=1)
[CASE-18] PASS: Extreme loss near 100% (-99.9%) (rows=1)
[CASE-19] PASS: High precision volume rounding (rows=1)
[CASE-20] PASS: Unicode / non-ASCII coin name (rows=1)
[CASE-21] PASS: Micro-price string representation (rows=1)
[CASE-22] PASS: Realistic 5-coin streaming batch (rows=5)

Summary: 22/22 passed.
ALL INDEPENDENT REFERENCE CHECKS PASSED.
```

### 2. Native Unit Tests
Command:
```sh
python3 python-rich-package/test_live_table.py
```
Output:
```text
.......................
----------------------------------------------------------------------
Ran 23 tests in 0.003s

OK
```

### 3. Pytest Execution
Command:
```sh
.venv/bin/pytest -v python-rich-package/test_live_table.py
```
Output:
```text
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /Users/shreyasahi/materials-1/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/shreyasahi/materials-1
configfile: pyproject.toml
collecting ... collected 23 items

python-rich-package/test_live_table.py::TestMakeTable::test_case_01_empty_input PASSED [  4%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_02_neutral_percentage PASSED [  8%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_03_positive_boundary_exact_5 PASSED [ 13%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_04_positive_threshold_above_5_1 PASSED [ 17%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_05_ordinary_positive_gain PASSED [ 21%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_06_negative_boundary_exact_minus_5 PASSED [ 26%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_07_negative_threshold_below_minus_5_1 PASSED [ 30%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_08_large_negative_loss PASSED [ 34%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_09_zero_volume_and_integer_percent PASSED [ 39%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_10_integer_volume PASSED [ 43%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_11_tuple_input PASSED [ 47%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_12_sequential_ordering PASSED [ 52%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_13_reversed_ordering PASSED [ 56%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_14_input_mutation_check PASSED [ 60%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_15_positive_interior_4_9 PASSED [ 65%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_16_negative_interior_minus_4_9 PASSED [ 69%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_17_large_gain_over_100 PASSED [ 73%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_18_extreme_loss_near_100 PASSED [ 78%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_19_high_precision_volume_rounding PASSED [ 82%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_20_unicode_name PASSED [ 86%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_21_micro_price_string PASSED [ 91%]
python-rich-package/test_live_table.py::TestMakeTable::test_case_22_realistic_multi_coin_mix PASSED [ 95%]
python-rich-package/test_live_table.py::TestMakeTable::test_table_structure_and_styles PASSED [100%]

============================== 23 passed in 0.05s ==============================
```

---

## Results Summary

| Case ID | Case Description | Rows Expected | Rows Actual | Return Type | Ordering | Mutation | Status |
|---|---|---|---|---|---|---|---|
| CASE-01 | Empty input boundary | 0 | 0 | `Table` | OK | Unmutated | PASS |
| CASE-02 | Neutral percentage (0.0%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-03 | Positive threshold boundary (5.0%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-04 | Positive threshold crossed (5.1%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-05 | Ordinary strong positive gain (12.4%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-06 | Negative threshold boundary (-5.0%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-07 | Negative threshold crossed (-5.1%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-08 | Large negative loss (-35.8%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-09 | Zero volume and int 0 percent | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-10 | Large integer volume | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-11 | Tuple input (iterable protocol) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-12 | Sequential ordering (A, B, C) | 3 | 3 | `Table` | OK | Unmutated | PASS |
| CASE-13 | Reversed ordering (C, B, A) | 3 | 3 | `Table` | OK | Unmutated | PASS |
| CASE-14 | Input mutation check | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-15 | Positive interior (+4.9%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-16 | Negative interior (-4.9%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-17 | Large positive gain over 100% (+150.5%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-18 | Extreme loss near 100% (-99.9%) | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-19 | High precision volume rounding | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-20 | Unicode / non-ASCII coin name | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-21 | Micro-price string representation | 1 | 1 | `Table` | OK | Unmutated | PASS |
| CASE-22 | Realistic 5-coin streaming batch | 5 | 5 | `Table` | OK | Unmutated | PASS |

- **Total Test Cases**: 22 independent checker cases, 23 unit tests.
- **Failures / Warnings**: 0 failures, 0 warnings.
- **External I/O**: File reading of `crypto_data.json` at module import and `time.asctime()` system calls were mocked in all test environments.
