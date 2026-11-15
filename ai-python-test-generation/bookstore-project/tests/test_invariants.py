"""Property and invariant tests for the bookstore package.

Validates core system invariants across at least 100 bounded valid cases
using deterministic fixed-seed generation (seed=42).
Checks return types, output shapes, ordering, input mutation, and fresh equivalent inputs.
"""

import copy
import random
from decimal import Decimal

from bookstore.catalog import Catalog
from bookstore.inventory import Inventory
from bookstore.pricing import (
    member_discount,
    quote_order,
    shipping_cost,
    tax_rate,
    volume_discount,
)

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

        op = rng.choice(["reserve", "release", "commit"])

        if op == "reserve" and avail > 0:
            q = rng.randint(1, min(avail, 10))
            returned = inv.reserve(isbn, q)
            assert type(returned) is int
            cases_verified += 1
        elif op == "release" and held > 0:
            q = rng.randint(1, min(held, 10))
            returned = inv.release(isbn, q)
            assert type(returned) is int
            cases_verified += 1
        elif op == "commit" and held > 0:
            q = rng.randint(1, min(held, 10))
            returned = inv.commit(isbn, q)
            assert type(returned) is int
            cases_verified += 1

        # Check invariants and types for all ISBNs after each operation
        for k in isbns:
            on_h = inv.on_hand(k)
            res = inv.reserved(k)
            av = inv.available(k)

            assert type(on_h) is int
            assert type(res) is int
            assert type(av) is int

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
        ret_reserve = inv.reserve("TEST-ISBN", q)
        assert type(ret_reserve) is int

        # Immediately release q copies
        ret_release = inv.release("TEST-ISBN", q)
        assert type(ret_release) is int

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
        ret_commit = inv.commit("COMMIT-ISBN", commit_q)
        assert type(ret_commit) is int
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

        assert type(d1) is Decimal
        assert type(d2) is Decimal
        assert d1 <= d2


def test_inventory_fresh_equivalent_inputs_produce_identical_states():
    """Verify that fresh equivalent Inventory instances under identical operations produce identical states."""
    rng = random.Random(FIXED_SEED + 10)
    stock = {f"ISBN-{i}": rng.randint(20, 100) for i in range(1, 6)}

    inv1 = Inventory(copy.deepcopy(stock))
    inv2 = Inventory(copy.deepcopy(stock))

    for _ in range(100):
        isbn = rng.choice(list(stock.keys()))
        avail = inv1.available(isbn)
        assert avail == inv2.available(isbn)
        held = inv1.reserved(isbn)
        assert held == inv2.reserved(isbn)

        op = rng.choice(["reserve", "release", "commit"])
        if op == "reserve" and avail > 0:
            q = rng.randint(1, min(avail, 5))
            r1 = inv1.reserve(isbn, q)
            r2 = inv2.reserve(isbn, q)
            assert r1 == r2
        elif op == "release" and held > 0:
            q = rng.randint(1, min(held, 5))
            r1 = inv1.release(isbn, q)
            r2 = inv2.release(isbn, q)
            assert r1 == r2
        elif op == "commit" and held > 0:
            q = rng.randint(1, min(held, 5))
            r1 = inv1.commit(isbn, q)
            r2 = inv2.commit(isbn, q)
            assert r1 == r2

        for k in stock.keys():
            assert inv1.on_hand(k) == inv2.on_hand(k)
            assert inv1.reserved(k) == inv2.reserved(k)
            assert inv1.available(k) == inv2.available(k)


def test_pricing_and_inventory_return_types_and_output_shapes():
    """Verify exact return types and output shapes for inventory and pricing callables."""
    stock = {"A": 10, "B": 20}
    inv = Inventory(stock)

    assert type(inv.on_hand("A")) is int
    assert type(inv.reserved("A")) is int
    assert type(inv.available("A")) is int
    assert type(inv.reserve("A", 2)) is int
    assert type(inv.release("A", 1)) is int
    assert type(inv.commit("A", 1)) is int

    vd = volume_discount(15)
    assert type(vd) is Decimal

    md = member_discount("pro")
    assert type(md) is Decimal

    tr = tax_rate("US")
    assert type(tr) is Decimal

    sc = shipping_cost(Decimal("30.00"))
    assert type(sc) is Decimal

    total = quote_order(2, "20.00", "pro", "US")
    assert type(total) is Decimal
    assert total.as_tuple().exponent == -2


def test_catalog_ordering_and_output_shape(tmp_path):
    """Verify Catalog output shapes, key schemas, and element ordering."""
    import json

    catalog_file = tmp_path / "ordering_catalog.json"
    records = [
        {
            "isbn": "111",
            "title": "First Book",
            "author": "Alice",
            "price": "10.00",
        },
        {
            "isbn": "222",
            "title": "Second Book",
            "author": "Bob",
            "price": "20.00",
        },
        {
            "isbn": "333",
            "title": "Third Book",
            "author": "Alice",
            "price": "30.00",
        },
        {
            "isbn": "444",
            "title": "Fourth Book",
            "author": "Alice",
            "price": "40.00",
        },
    ]
    catalog_file.write_text(json.dumps(records), encoding="utf-8")

    cat1 = Catalog(catalog_file)
    cat2 = Catalog(catalog_file)

    assert isinstance(cat1.books, dict)
    assert list(cat1.books.keys()) == ["111", "222", "333", "444"]
    assert list(cat1.books.keys()) == list(cat2.books.keys())

    expected_keys = {"isbn", "title", "author", "price"}
    for item in cat1.books.values():
        assert isinstance(item, dict)
        assert set(item.keys()) == expected_keys
        assert all(isinstance(v, str) for v in item.values())

    alice_books = cat1.by_author("Alice")
    assert isinstance(alice_books, list)
    assert len(alice_books) == 3
    assert [b["isbn"] for b in alice_books] == ["111", "333", "444"]
    assert [b["title"] for b in alice_books] == [
        "First Book",
        "Third Book",
        "Fourth Book",
    ]
