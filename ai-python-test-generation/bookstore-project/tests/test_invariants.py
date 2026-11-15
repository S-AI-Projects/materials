"""Property and invariant tests for the bookstore package.

Validates core system invariants across at least 100 bounded valid cases
using deterministic fixed-seed generation (seed=42).
"""

import copy
import random
from decimal import Decimal

from bookstore.catalog import Catalog
from bookstore.inventory import Inventory
from bookstore.pricing import volume_discount

FIXED_SEED = 42


def test_inventory_invariants_across_100_bounded_operations():
    """Verify inventory availability, conservation, boundedness, and immutability.

    Core invariant: for any ISBN at any time, available == on_hand - reserved,
    with 0 <= reserved <= on_hand and available >= 0.
    Caller stock dictionary must never be mutated.
    """
    rng = random.Random(FIXED_SEED)
    initial_stock = {f"ISBN-{i}": rng.randint(20, 100) for i in range(1, 6)}
    stock_copy = copy.deepcopy(initial_stock)

    inv = Inventory(initial_stock)

    # Verify input immutability immediately after construction
    assert initial_stock == stock_copy

    isbns = list(initial_stock.keys())
    cases_verified = 0

    for _ in range(120):  # 120 iterations (> 100 bounded valid cases)
        isbn = rng.choice(isbns)
        avail = inv.available(isbn)
        held = inv.reserved(isbn)

        # Decide on operation: reserve, release, or commit
        op = rng.choice(["reserve", "release", "commit"])

        if op == "reserve" and avail > 0:
            q = rng.randint(1, min(avail, 10))
            returned = inv.reserve(isbn, q)
            assert isinstance(returned, int)
            cases_verified += 1
        elif op == "release" and held > 0:
            q = rng.randint(1, min(held, 10))
            returned = inv.release(isbn, q)
            assert isinstance(returned, int)
            cases_verified += 1
        elif op == "commit" and held > 0:
            q = rng.randint(1, min(held, 10))
            returned = inv.commit(isbn, q)
            assert isinstance(returned, int)
            cases_verified += 1

        # Check invariants for all ISBNs after each operation
        for k in isbns:
            on_h = inv.on_hand(k)
            res = inv.reserved(k)
            av = inv.available(k)

            # Invariant 1: exact availability formula
            assert av == on_h - res

            # Invariant 2: stock conservation & bounds
            assert 0 <= res <= on_h
            assert 0 <= av <= on_h

        # Invariant 3: caller stock dictionary remains completely unmutated
        assert initial_stock == stock_copy

    assert cases_verified >= 100


def test_roundtrip_reserve_release_invariant_100_cases():
    """Verify that reserving q copies followed by releasing q copies is an identity operation."""
    rng = random.Random(FIXED_SEED + 1)

    for _ in range(100):
        initial_on_hand = rng.randint(10, 100)
        already_held = rng.randint(0, initial_on_hand - 5)
        inv = Inventory({"TEST-ISBN": initial_on_hand})
        if already_held > 0:
            inv.reserve("TEST-ISBN", already_held)

        state_before = (
            inv.on_hand("TEST-ISBN"),
            inv.reserved("TEST-ISBN"),
            inv.available("TEST-ISBN"),
        )
        avail = state_before[2]
        assert avail >= 5

        # Reserve q copies
        q = rng.randint(1, avail)
        inv.reserve("TEST-ISBN", q)

        # Immediately release q copies
        inv.release("TEST-ISBN", q)

        state_after = (
            inv.on_hand("TEST-ISBN"),
            inv.reserved("TEST-ISBN"),
            inv.available("TEST-ISBN"),
        )
        assert state_after == state_before


def test_commit_preserves_available_invariant_100_cases():
    """Verify that committing reserved copies never alters available count."""
    rng = random.Random(FIXED_SEED + 2)

    for _ in range(100):
        on_hand = rng.randint(20, 100)
        inv = Inventory({"COMMIT-ISBN": on_hand})
        held = rng.randint(5, on_hand)
        inv.reserve("COMMIT-ISBN", held)

        avail_before = inv.available("COMMIT-ISBN")
        commit_q = rng.randint(1, held)
        inv.commit("COMMIT-ISBN", commit_q)
        avail_after = inv.available("COMMIT-ISBN")

        assert avail_after == avail_before
        assert inv.reserved("COMMIT-ISBN") == held - commit_q
        assert inv.on_hand("COMMIT-ISBN") == on_hand - commit_q


def test_volume_discount_monotonicity_invariant_100_cases():
    """Verify that volume_discount is monotonically non-decreasing for all quantities."""
    rng = random.Random(FIXED_SEED + 3)

    for _ in range(100):
        q1 = rng.randint(1, 100)
        q2 = rng.randint(q1, 150)
        d1 = volume_discount(q1)
        d2 = volume_discount(q2)

        assert isinstance(d1, Decimal)
        assert isinstance(d2, Decimal)
        assert d1 <= d2


def test_catalog_ordering_and_immutability(tmp_path):
    """Verify Catalog.by_author preserves file sequence order and does not mutate books."""
    import json

    catalog_file = tmp_path / "test_catalog.json"
    records = [
        {
            "isbn": "1",
            "title": "Book 1",
            "author": "Author A",
            "price": "10.00",
        },
        {
            "isbn": "2",
            "title": "Book 2",
            "author": "Author B",
            "price": "20.00",
        },
        {
            "isbn": "3",
            "title": "Book 3",
            "author": "Author A",
            "price": "30.00",
        },
        {
            "isbn": "4",
            "title": "Book 4",
            "author": "Author A",
            "price": "40.00",
        },
    ]
    catalog_file.write_text(json.dumps(records), encoding="utf-8")

    cat = Catalog(catalog_file)
    books_before = copy.deepcopy(cat.books)

    results = cat.by_author("Author A")
    assert [b["isbn"] for b in results] == ["1", "3", "4"]
    assert cat.books == books_before
