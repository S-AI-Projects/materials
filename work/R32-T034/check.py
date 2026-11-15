#!/usr/bin/env python3
"""
Focused runner and independent invariant checker for R32-T034.
Runs property-based invariant checks (100+ bounded cases, fixed seed),
executes the project pytest suite, and verifies failure detection on mutated behavior.
"""

import copy
import random
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOKSTORE_DIR = ROOT / "ai-python-test-generation" / "bookstore-project"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python3"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

# Ensure bookstore package is importable
if str(BOOKSTORE_DIR) not in sys.path:
    sys.path.insert(0, str(BOOKSTORE_DIR))

from bookstore.inventory import Inventory  # noqa: E402
from bookstore.pricing import volume_discount  # noqa: E402

FIXED_SEED = 42


def run_invariant_property_checks(custom_inventory_cls=Inventory):
    """
    Run 100+ bounded property test cases against Inventory and Pricing.
    Returns (passed, total_cases, error_message).
    """
    rng = random.Random(FIXED_SEED)
    initial_stock = {f"ISBN-{i}": rng.randint(20, 100) for i in range(1, 6)}
    stock_copy = copy.deepcopy(initial_stock)

    inv = custom_inventory_cls(initial_stock)
    isbns = list(initial_stock.keys())
    cases_verified = 0

    for _ in range(120):
        isbn = rng.choice(isbns)
        avail = inv.available(isbn)
        held = inv.reserved(isbn)
        op = rng.choice(["reserve", "release", "commit"])

        if op == "reserve" and avail > 0:
            q = rng.randint(1, min(avail, 10))
            returned = inv.reserve(isbn, q)
            if not isinstance(returned, int):
                return (
                    False,
                    cases_verified,
                    f"reserve returned non-int: {type(returned)}",
                )
            cases_verified += 1
        elif op == "release" and held > 0:
            q = rng.randint(1, min(held, 10))
            returned = inv.release(isbn, q)
            if not isinstance(returned, int):
                return (
                    False,
                    cases_verified,
                    f"release returned non-int: {type(returned)}",
                )
            cases_verified += 1
        elif op == "commit" and held > 0:
            q = rng.randint(1, min(held, 10))
            returned = inv.commit(isbn, q)
            if not isinstance(returned, int):
                return (
                    False,
                    cases_verified,
                    f"commit returned non-int: {type(returned)}",
                )
            cases_verified += 1

        for k in isbns:
            on_h = inv.on_hand(k)
            res = inv.reserved(k)
            av = inv.available(k)

            # Invariant 1: availability equation
            if av != on_h - res:
                return (
                    False,
                    cases_verified,
                    f"Invariant violated for {k}: available ({av}) != on_hand ({on_h}) - reserved ({res})",
                )

            # Invariant 2: stock boundedness
            if not (0 <= res <= on_h and 0 <= av <= on_h):
                return (
                    False,
                    cases_verified,
                    f"Bounds violated for {k}: on_hand={on_h}, reserved={res}, available={av}",
                )

        # Invariant 3: caller stock dictionary immutability
        if initial_stock != stock_copy:
            return (
                False,
                cases_verified,
                "Input stock dictionary was mutated by Inventory operations",
            )

    # Volume discount monotonicity (100 checks)
    rng_p = random.Random(FIXED_SEED + 3)
    for _ in range(100):
        q1 = rng_p.randint(1, 100)
        q2 = rng_p.randint(q1, 150)
        d1 = volume_discount(q1)
        d2 = volume_discount(q2)
        if not (
            isinstance(d1, Decimal) and isinstance(d2, Decimal) and d1 <= d2
        ):
            return (
                False,
                cases_verified,
                f"Monotonicity invariant violated: q1={q1}->{d1}, q2={q2}->{d2}",
            )

    return True, cases_verified, ""


def verify_detection_on_broken_copy():
    """Verify that checks detect deliberately broken behavior in a temporary copy."""

    class BrokenAvailableInventory(Inventory):
        def available(self, isbn):
            # Deliberately breaks availability equation invariant
            return super().available(isbn) + 1

    passed, _, err = run_invariant_property_checks(BrokenAvailableInventory)
    if passed:
        print(
            "ERROR: Invariant check failed to detect broken available() implementation!"
        )
        return False
    print(
        f"Verified mutation detection: broken copy caught correctly ({err})."
    )

    class MutatingStockInventory(Inventory):
        def __init__(self, stock=None):
            super().__init__(stock)
            if stock:
                # Deliberately mutates caller stock
                first_key = next(iter(stock))
                stock[first_key] = 999999

    passed_mut, _, err_mut = run_invariant_property_checks(
        MutatingStockInventory
    )
    if passed_mut:
        print(
            "ERROR: Invariant check failed to detect input dictionary mutation!"
        )
        return False
    print(
        f"Verified mutation detection: mutating copy caught correctly ({err_mut})."
    )

    return True


def run_native_pytest_suite():
    """Run native pytest suite in bookstore-project using project configuration."""
    print("Running native pytest suite in bookstore-project...")
    cmd = [PYTHON, "-m", "pytest", "-v", "tests/"]
    result = subprocess.run(cmd, cwd=BOOKSTORE_DIR)
    return result.returncode == 0


def main():
    print("=== Running R32-T034 Check Suite ===")
    print(f"Python: {PYTHON}")
    print(f"Directory: {BOOKSTORE_DIR}")

    # 1. Run property invariant checks
    print("\n[Step 1] Running 100+ bounded invariant property checks...")
    ok, count, msg = run_invariant_property_checks()
    if not ok:
        print(f"FAILED: {msg}")
        sys.exit(1)
    print(
        f"PASS: {count} valid bounded operations verified against all invariants."
    )

    # 2. Verify defect detection on temporary broken copy
    print("\n[Step 2] Verifying defect detection on deliberate mutants...")
    if not verify_detection_on_broken_copy():
        print("FAILED: Defect detection verification failed.")
        sys.exit(1)
    print("PASS: Defect detection verified.")

    # 3. Run native pytest suite
    print("\n[Step 3] Running native project test suite...")
    if not run_native_pytest_suite():
        print("FAILED: Native pytest suite failed.")
        sys.exit(1)
    print("PASS: Native test suite passed.")

    print("\nALL R32-T034 CHECKS PASSED.")
    sys.exit(0)


if __name__ == "__main__":
    main()
