#!/usr/bin/env python3
"""
Focused runner and independent invariant checker for R32-T034.
Runs property‑based invariant checks (100+ bounded cases, fixed seed),
executes the project pytest suite, and verifies that intentional mutants are detected
via real filesystem copies.
"""

import copy
import random
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
import shutil
import tempfile
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
BOOKSTORE_DIR = ROOT / "ai-python-test-generation" / "bookstore-project"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python3"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

# Make sure the original bookstore package is importable for the baseline tests
if str(BOOKSTORE_DIR) not in sys.path:
    sys.path.insert(0, str(BOOKSTORE_DIR))

from bookstore.inventory import Inventory  # noqa: E402
from bookstore.pricing import volume_discount  # noqa: E402

FIXED_SEED = 42


def run_invariant_property_checks(custom_inventory_cls=Inventory):
    """Run 100+ bounded property test cases against Inventory and Pricing.
    Returns (passed: bool, cases_verified: int, error_message: str).
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
            ret = inv.reserve(isbn, q)
            if not isinstance(ret, int):
                return False, cases_verified, f"reserve returned non‑int: {type(ret)}"
            cases_verified += 1
        elif op == "release" and held > 0:
            q = rng.randint(1, min(held, 10))
            ret = inv.release(isbn, q)
            if not isinstance(ret, int):
                return False, cases_verified, f"release returned non‑int: {type(ret)}"
            cases_verified += 1
        elif op == "commit" and held > 0:
            q = rng.randint(1, min(held, 10))
            ret = inv.commit(isbn, q)
            if not isinstance(ret, int):
                return False, cases_verified, f"commit returned non‑int: {type(ret)}"
            cases_verified += 1

        for k in isbns:
            on_h = inv.on_hand(k)
            res = inv.reserved(k)
            av = inv.available(k)
            if av != on_h - res:
                return False, cases_verified, f"Invariant violated for {k}: available ({av}) != on_hand ({on_h}) - reserved ({res})"
            if not (0 <= res <= on_h and 0 <= av <= on_h):
                return False, cases_verified, f"Bounds violated for {k}: on_hand={on_h}, reserved={res}, available={av}"
        if initial_stock != stock_copy:
            return False, cases_verified, "Input stock dictionary was mutated by Inventory operations"

    # Volume‑discount monotonicity (100 checks)
    rng_p = random.Random(FIXED_SEED + 3)
    for _ in range(100):
        q1 = rng_p.randint(1, 100)
        q2 = rng_p.randint(q1, 150)
        d1 = volume_discount(q1)
        d2 = volume_discount(q2)
        if not (isinstance(d1, Decimal) and isinstance(d2, Decimal) and d1 <= d2):
            return False, cases_verified, f"Monotonicity invariant violated: q1={q1}->{d1}, q2={q2}->{d2}"

    return True, cases_verified, ""


def run_check_with_copy(project_path: Path, mutate_type: str) -> bool:
    """Load the mutated Inventory implementation from *project_path* and run the
    invariant checks against it. Returns True if the mutant is correctly detected
    (i.e., the checks FAIL).
    """
    inventory_file = project_path / "bookstore" / "inventory.py"
    # Ensure a fresh import
    if 'bookstore.inventory' in sys.modules:
        del sys.modules['bookstore.inventory']
    spec = importlib.util.spec_from_file_location("bookstore.inventory", str(inventory_file))
    if spec is None or spec.loader is None:
        print(f"Failed to load Inventory module from {inventory_file}")
        return False
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    TestInventory = getattr(module, "Inventory")
    ok, _, err = run_invariant_property_checks(custom_inventory_cls=TestInventory)
    if ok:
        print(f"UNEXPECTED PASS for mutant {mutate_type}")
        return False
    else:
        print(f"EXPECTED FAIL for mutant {mutate_type}: {err}")
        return True


def verify_detection_on_broken_copy() -> bool:
    """Create temporary copies of the bookstore project, inject bugs, and verify
    that the invariant checker detects them.
    """
    # 1. Broken available method – always returns 0
    with tempfile.TemporaryDirectory() as td1:
        project_copy = Path(td1) / "bookstore-project"
        shutil.copytree(str(BOOKSTORE_DIR), str(project_copy))
        inv_file = project_copy / "bookstore" / "inventory.py"
        lines = inv_file.read_text().splitlines()
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.lstrip().startswith('def available(self, isbn):'):
                new_lines.append('    def available(self, isbn):')
                new_lines.append('        """Bugged: always returns 0"""')
                new_lines.append('        return 0')
                i += 1
                while i < len(lines) and not lines[i].lstrip().startswith('def '):
                    i += 1
                continue
            new_lines.append(line)
            i += 1
        inv_file.write_text('\n'.join(new_lines) + '\n')
        if not run_check_with_copy(project_copy, 'available'):
            print('ERROR: Defect detection failed for broken available implementation.')
            return False
        print('Verified mutation detection: broken available implementation caught.')

    # 2. Mutating __init__ – mutates caller's stock dict
    with tempfile.TemporaryDirectory() as td2:
        project_copy2 = Path(td2) / "bookstore-project"
        shutil.copytree(str(BOOKSTORE_DIR), str(project_copy2))
        inv_file2 = project_copy2 / "bookstore" / "inventory.py"
        lines2 = inv_file2.read_text().splitlines()
        new_lines2 = []
        i = 0
        while i < len(lines2):
            line = lines2[i]
            if line.lstrip().startswith('def __init__(self, stock=None):'):
                # Replace the whole __init__ method with a buggy version
                new_lines2.append('    def __init__(self, stock=None):')
                new_lines2.append('        # BUG: mutate caller stock dictionary')
                new_lines2.append('        if stock:')
                new_lines2.append('            first_key = next(iter(stock))')
                new_lines2.append('            stock[first_key] = 999999')
                new_lines2.append('        self._on_hand = dict(stock or {})')
                new_lines2.append('        self._reserved = {}')
                # Skip original method body
                i += 1
                while i < len(lines2) and not lines2[i].lstrip().startswith('def '):
                    i += 1
                continue
            new_lines2.append(line)
            i += 1
        inv_file2.write_text('\n'.join(new_lines2) + '\n')
        if not run_check_with_copy(project_copy2, 'init'):
            print('ERROR: Defect detection failed for mutating __init__ implementation.')
            return False
        print('Verified mutation detection: mutating __init__ implementation caught.')
    return True


def run_native_pytest_suite() -> bool:
    """Run the native pytest suite in the bookstore‑project directory."""
    print("Running native pytest suite in bookstore-project...")
    cmd = [PYTHON, "-m", "pytest", "-v", "tests/"]
    result = subprocess.run(cmd, cwd=BOOKSTORE_DIR)
    return result.returncode == 0


def main():
    print("=== Running R32-T034 Check Suite ===")
    print(f"Python: {PYTHON}")
    print(f"Directory: {BOOKSTORE_DIR}")

    # Step 1 – property checks
    print("\n[Step 1] Running 100+ bounded invariant property checks...")
    ok, count, msg = run_invariant_property_checks()
    if not ok:
        print(f"FAILED: {msg}")
        sys.exit(1)
    print(f"PASS: {count} valid bounded operations verified against all invariants.")

    # Step 2 – mutation detection
    print("\n[Step 2] Verifying defect detection on deliberate mutants...")
    if not verify_detection_on_broken_copy():
        print("FAILED: Defect detection verification failed.")
        sys.exit(1)
    print("PASS: Defect detection verified.")

    # Step 3 – native pytest suite
    print("\n[Step 3] Running native project test suite...")
    if not run_native_pytest_suite():
        print("FAILED: Native pytest suite failed.")
        sys.exit(1)
    print("PASS: Native test suite passed.")

    print("\nALL R32-T034 CHECKS PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    main()
