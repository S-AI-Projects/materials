#!/usr/bin/env python3
"""Focused runner and invariant/property test for R32-T004.

Target: queue/src/graph.py (City and Queue invariants)
Preconditions:
- Line 11: City NamedTuple in queue/src/graph.py
- Queues FIFO order, size agreement after each operation, and instance isolation.

This runner executes:
1. Canonical fixture check: Enqueue A, B, C; remove twice; insert D; drain. Removal order must be A, B, C, D.
2. Empty-state behavior check: len == 0, dequeue raises IndexError.
3. 100 bounded valid property-based random operation sequences with deterministic seed (42).
4. Deliberately broken invariant check (mutated queue implementation fails assertions).
5. Native unit test suite (5 tests in queue/src/test_graph.py).
6. Writes comprehensive evidence files in work/R32-T004/.
"""

import copy
import io
import json
import os
import platform
import random
import sys
import unittest
from collections import deque
from unittest.mock import MagicMock

# Setup path and mocks
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODULE_DIR = os.path.join(REPO_ROOT, "queue", "src")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

if "networkx" not in sys.modules:
    sys.modules["networkx"] = MagicMock()

import graph
from graph import City
from queues import Queue


# Broken queue implementation to verify failure detection when invariant is violated
class BrokenLIFOQueue(Queue):
    """Deliberately breaks FIFO invariant by acting as LIFO (Stack)."""
    def dequeue(self):
        return self._elements.pop()


class BrokenSizeQueue(Queue):
    """Deliberately breaks size invariant by returning desynchronized length."""
    def __len__(self):
        return len(self._elements) + 1


# City pool for deterministic generator
CITY_POOL = [
    City(name="Athens", country="Greece", year=-800, latitude=37.98, longitude=23.72),
    City(name="Berlin", country="Germany", year=1237, latitude=52.52, longitude=13.40),
    City(name="Cairo", country="Egypt", year=969, latitude=30.04, longitude=31.23),
    City(name="Dublin", country="Ireland", year=841, latitude=53.34, longitude=-6.26),
    City(name="Edinburgh", country="UK", year=1124, latitude=55.95, longitude=-3.18),
    City(name="Florence", country="Italy", year=-59, latitude=43.76, longitude=11.25),
    City(name="Geneva", country="Switzerland", year=121, latitude=46.20, longitude=6.14),
    City(name="Helsinki", country="Finland", year=1550, latitude=60.16, longitude=24.93),
    City(name="Istanbul", country="Turkey", year=-667, latitude=41.00, longitude=28.97),
    City(name="Kyoto", country="Japan", year=794, latitude=35.01, longitude=135.76),
]


def test_canonical_fixture(queue_cls=Queue):
    """Executes the canonical fixture:
    Enqueue A, B, C; dequeue 2; enqueue D; drain.
    Expected removals: [A, B, C, D]
    """
    q = queue_cls()
    expected_order = [CITY_POOL[0], CITY_POOL[1], CITY_POOL[2], CITY_POOL[3]]
    actual_removals = []

    # Enqueue A, B, C
    q.enqueue(CITY_POOL[0])
    assert len(q) == 1, f"Expected size 1, got {len(q)}"
    q.enqueue(CITY_POOL[1])
    assert len(q) == 2, f"Expected size 2, got {len(q)}"
    q.enqueue(CITY_POOL[2])
    assert len(q) == 3, f"Expected size 3, got {len(q)}"

    # Remove twice
    actual_removals.append(q.dequeue())
    assert len(q) == 2, f"Expected size 2, got {len(q)}"
    actual_removals.append(q.dequeue())
    assert len(q) == 1, f"Expected size 1, got {len(q)}"

    # Insert D
    q.enqueue(CITY_POOL[3])
    assert len(q) == 2, f"Expected size 2, got {len(q)}"

    # Drain queue
    while len(q) > 0:
        actual_removals.append(q.dequeue())

    assert len(q) == 0, f"Expected size 0, got {len(q)}"
    assert actual_removals == expected_order, f"Expected {expected_order}, got {actual_removals}"
    return actual_removals


def run_property_simulation(seed: int, num_cases: int = 100, queue_cls=Queue):
    """Runs `num_cases` bounded property tests with a deterministic seed."""
    rng = random.Random(seed)
    records = []

    for case_id in range(1, num_cases + 1):
        q = queue_cls()
        model_queue = deque()
        operations_count = rng.randint(10, 30)
        ops_log = []

        for op_idx in range(operations_count):
            # If queue is empty, must enqueue
            can_dequeue = (len(model_queue) > 0)
            op = "enqueue" if not can_dequeue else rng.choice(["enqueue", "enqueue", "dequeue"])

            if op == "enqueue":
                city = rng.choice(CITY_POOL)
                q.enqueue(city)
                model_queue.append(city)
                ops_log.append(f"enqueue({city.name})")
            else:
                expected_city = model_queue.popleft()
                actual_city = q.dequeue()
                assert actual_city == expected_city, (
                    f"Case {case_id} FIFO violation: expected {expected_city.name}, got {actual_city.name}"
                )
                ops_log.append(f"dequeue()->{actual_city.name}")

            # Check invariant: size agreement after each operation
            assert len(q) == len(model_queue), (
                f"Case {case_id} size desync: q has {len(q)}, expected {len(model_queue)}"
            )

        # Drain the rest of the queue
        drain_removals = []
        while len(model_queue) > 0:
            expected_city = model_queue.popleft()
            actual_city = q.dequeue()
            assert actual_city == expected_city, (
                f"Case {case_id} drain FIFO violation: expected {expected_city.name}, got {actual_city.name}"
            )
            assert len(q) == len(model_queue), (
                f"Case {case_id} drain size desync: q has {len(q)}, expected {len(model_queue)}"
            )
            drain_removals.append(actual_city.name)

        # Empty state check
        assert len(q) == 0, f"Case {case_id} expected empty queue"
        try:
            q.dequeue()
            raised_index_error = False
        except IndexError:
            raised_index_error = True
        assert raised_index_error, f"Case {case_id} dequeue on empty did not raise IndexError"

        records.append({
            "case_id": case_id,
            "operations_count": operations_count,
            "ops": ops_log[:5],  # sample
            "passed": True,
        })

    return records


def run_checks():
    evidence_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(evidence_dir, exist_ok=True)

    print("=== Running R32-T004 Invariant and Property Checks ===")

    # 1. Canonical fixture check
    print("Testing canonical fixture (A, B, C -> dequeue 2 -> D -> drain)...")
    fixture_removals = test_canonical_fixture(Queue)
    fixture_names = [c.name for c in fixture_removals]
    print(f"Canonical fixture passed: removals = {fixture_names}")
    assert fixture_names == ["Athens", "Berlin", "Cairo", "Dublin"]

    # 2. Bounded property tests (100 deterministic cases)
    print("Running 100 bounded valid property cases (seed=42)...")
    prop_records = run_property_simulation(seed=42, num_cases=100, queue_cls=Queue)
    print(f"Completed {len(prop_records)} property test sequences successfully.")

    # 3. Deliberately broken invariant check (must fail when invariant is broken)
    print("Testing deliberate invariant violations on mutated copies...")
    lifo_failed = False
    try:
        test_canonical_fixture(BrokenLIFOQueue)
    except AssertionError as e:
        lifo_failed = True
        smallest_fifo_failure = str(e)

    assert lifo_failed, "BrokenLIFOQueue unexpectedly passed fixture!"

    size_failed = False
    try:
        test_canonical_fixture(BrokenSizeQueue)
    except AssertionError as e:
        size_failed = True
        smallest_size_failure = str(e)

    assert size_failed, "BrokenSizeQueue unexpectedly passed fixture!"
    print(f"Deliberate violations correctly detected and failed as expected:")
    print(f" - FIFO violation error: {smallest_fifo_failure}")
    print(f" - Size violation error: {smallest_size_failure}")

    # 4. Run native unit tests
    print("=== Running Native Unit Tests in queue/src/test_graph.py ===")
    suite = unittest.defaultTestLoader.discover(MODULE_DIR, pattern="test_*.py")
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    test_result = runner.run(suite)

    unittest_count = test_result.testsRun
    unittest_passed = test_result.wasSuccessful()
    print(f"Executed {unittest_count} native unit tests. All passed: {unittest_passed}")
    assert unittest_passed, "Native unit tests failed!"

    # 5. Write evidence files
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
        f.write("Canonical Fixture Input Sequence:\n")
        f.write("1. enqueue(City(Athens))\n2. enqueue(City(Berlin))\n3. enqueue(City(Cairo))\n")
        f.write("4. dequeue() -> Athens\n5. dequeue() -> Berlin\n6. enqueue(City(Dublin))\n7. drain\n\n")
        f.write(f"Property test cases: 100 deterministic pseudo-random sequences (seed=42)\n")
        for r in prop_records[:10]:
            f.write(f"Case {r['case_id']:03d}: {r['operations_count']} operations. Sample: {r['ops']}\n")

    with open(os.path.join(evidence_dir, "expected-results.txt"), "w") as f:
        f.write("Canonical Fixture Expected Removals: ['Athens', 'Berlin', 'Cairo', 'Dublin']\n")
        f.write("Empty-state expected: len == 0, dequeue() raises IndexError\n")
        f.write("Property invariants: FIFO order and len(queue) == len(model) after every op\n")
        f.write(f"Deliberate violation expectation: BrokenLIFOQueue and BrokenSizeQueue fail with AssertionError\n")

    with open(os.path.join(evidence_dir, "actual-results.txt"), "w") as f:
        f.write(f"Canonical Fixture Actual Removals: {fixture_names}\n")
        f.write(f"Property test sequences passed: 100/100\n")
        f.write(f"Deliberate FIFO violation captured: {smallest_fifo_failure}\n")
        f.write(f"Deliberate Size violation captured: {smallest_size_failure}\n")
        f.write(f"Native unit tests passed: {unittest_count}/{unittest_count}\n")

    with open(os.path.join(evidence_dir, "inputs_and_results.json"), "w") as f:
        json.dump(
            {
                "fixture_names": fixture_names,
                "property_cases_count": len(prop_records),
                "property_seed": 42,
                "deliberate_violations_detected": True,
                "smallest_fifo_failure": smallest_fifo_failure,
                "smallest_size_failure": smallest_size_failure,
                "native_tests_count": unittest_count,
                "all_checks_passed": True,
            },
            f,
            indent=2,
        )

    with open(os.path.join(evidence_dir, "evidence.txt"), "w") as f:
        f.write("R32-T004 Verification Summary\n")
        f.write("==============================\n")
        f.write("Target module: queue/src/graph.py (City NamedTuple and Queue invariants)\n")
        f.write("Precondition citation: Line 11 City definition & Line 23 from_dict\n")
        f.write(f"Canonical fixture: {fixture_names} (matched exactly [Athens, Berlin, Cairo, Dublin])\n")
        f.write(f"Property tests: 100 bounded cases with seed=42 verified\n")
        f.write(f"Deliberate invariant breakage: correctly caught and documented\n")
        f.write(f"Native unit tests: {unittest_count} executed, {unittest_count} passed\n")
        f.write(f"Exit status: 0\n\n")
        f.write("Unittest Output:\n")
        f.write(stream.getvalue())

    print("All R32-T004 invariant checks and native tests passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    run_checks()
