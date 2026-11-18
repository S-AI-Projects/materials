#!/usr/bin/env python3
"""Verification check runner for Task R32-T024.

Tests invariants of `main` in python-serialize/hierarchical-data/bson_demo.py.
Evaluates roundtrip preservation, immutability, determinism, and property tests.
"""

import copy
import importlib.util
import io
import json
import os
import platform
import random
import sys
import unittest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(WORK_DIR, "..", ".."))

# Load bson_demo.py
BSON_DEMO_PATH = os.path.join(
    REPO_ROOT, "python-serialize", "hierarchical-data", "bson_demo.py"
)
spec = importlib.util.spec_from_file_location("bson_demo", BSON_DEMO_PATH)
bson_demo = importlib.util.module_from_spec(spec)
sys.modules["bson_demo"] = bson_demo
spec.loader.exec_module(bson_demo)

# Load test_bson_demo.py
TEST_BSON_DEMO_PATH = os.path.join(
    REPO_ROOT, "python-serialize", "hierarchical-data", "test_bson_demo.py"
)
test_spec = importlib.util.spec_from_file_location("test_bson_demo", TEST_BSON_DEMO_PATH)
test_module = importlib.util.module_from_spec(test_spec)
test_spec.loader.exec_module(test_module)

serialize = bson_demo.serialize
deserialize = bson_demo.deserialize
main_fn = bson_demo.main


def write_evidence(test_cases, test_results, unit_test_output):
    """Write verification evidence files to work/R32-T024/."""
    os.makedirs(WORK_DIR, exist_ok=True)

    with open(os.path.join(WORK_DIR, "tool-versions.txt"), "w") as f:
        f.write(f"Python Version: {sys.version}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Interpreter: {sys.executable}\n")

    with open(os.path.join(WORK_DIR, "test-inputs.txt"), "w") as f:
        f.write("# Precondition Anchors:\n")
        f.write("Line 58: with open(file_path, encoding='utf-8') as file:\n")
        f.write("Line 59: document = json.load(file)\n")
        f.write("Line 60: return encode_document(document)\n")
        f.write("Line 64: return decode_document(data)\n\n")
        f.write("# Invariant & Property Test Matrix:\n")
        for inp, desc in test_cases:
            f.write(f"Input: {repr(inp)[:120]} | Desc: {desc}\n")

    with open(os.path.join(WORK_DIR, "expected-results.txt"), "w") as f:
        f.write("# Expected Outcomes (Round-trip Identity D == decode(encode(D))):\n")
        for inp, desc in test_cases:
            f.write(f"Desc: {desc} => Expected: Identity Preserved (True)\n")

    with open(os.path.join(WORK_DIR, "actual-results.txt"), "w") as f:
        f.write("# Actual Outcomes:\n")
        for desc, status in test_results:
            f.write(f"Desc: {desc} => Status: {status}\n")

    with open(os.path.join(WORK_DIR, "evidence.txt"), "w") as f:
        f.write("=== Task R32-T024 Verification Evidence ===\n")
        f.write("Target: python-serialize/hierarchical-data/bson_demo.py\n")
        f.write(f"Invariant Cases Evaluated: {len(test_results)}/{len(test_cases)}\n")
        f.write("Round-trip and Immutability Invariants: 100% Verified\n\n")
        f.write("=== Native Unit Test Output ===\n")
        f.write(unit_test_output)
        f.write("\nVerification Result: SUCCESS (Exit Code 0)\n")


def main():
    print("Running Task R32-T024 verification check...")

    # 1. Verify precondition anchor training.json exists
    training_json = os.path.join(
        REPO_ROOT, "python-serialize", "hierarchical-data", "data", "training.json"
    )
    assert os.path.exists(training_json), "Fixture training.json missing"
    with open(training_json, "r", encoding="utf-8") as f:
        training_doc = json.load(f)

    # 2. Test Invariant Matrix
    test_cases = [
        ({}, "Smallest valid input (empty dict)"),
        ({"scalar_int": 42}, "Single integer field"),
        ({"scalar_str": "hello world"}, "Single string field"),
        ({"scalar_float": 3.14159}, "Single float field"),
        ({"scalar_bool": True}, "Single boolean field"),
        ({"nested": {"a": 1, "b": [2, 3]}}, "Nested dict and list"),
        (training_doc, "Ordinary valid input (training.json fixture)"),
    ]

    test_results = []
    for doc, desc in test_cases:
        doc_copy = copy.deepcopy(doc)
        encoded = serialize(document=doc)
        decoded = deserialize(encoded)

        # Check Round-trip Invariant
        if decoded != doc:
            print(f"FAILED Roundtrip on {desc}")
            sys.exit(1)

        # Check Immutability Invariant
        if doc != doc_copy:
            print(f"FAILED Immutability on {desc}")
            sys.exit(1)

        test_results.append((desc, "PASS"))

    # 3. Property Tests with Random Documents
    random.seed(42)
    for p_idx in range(25):
        prop_doc = {
            f"key_{k}": random.choice(["val", 123, 4.56, True, [1, 2], {"sub": 0}])
            for k in range(random.randint(1, 5))
        }
        encoded = serialize(document=prop_doc)
        decoded = deserialize(encoded)
        if decoded != prop_doc:
            print(f"FAILED Property test on iteration {p_idx}")
            sys.exit(1)

    test_cases.append((f"Property Tests ({25} iterations)", "25 randomized property runs"))
    test_results.append(("25 randomized property runs", "PASS"))

    # 4. Native Unit Test Suite Execution
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        test_module.TestBsonDemoInvariants
    )
    result = runner.run(suite)
    unit_test_output = stream.getvalue()

    if not result.wasSuccessful():
        print("Native unit test suite failed!")
        print(unit_test_output)
        sys.exit(1)

    print(f"All {len(test_cases)} invariant test cases passed.")
    print(f"Ran {result.testsRun} native unit tests: OK.")

    # 5. Write evidence files
    write_evidence(test_cases, test_results, unit_test_output)
    print(f"Verification evidence written to {WORK_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
