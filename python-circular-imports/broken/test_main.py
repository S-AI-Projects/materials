"""
Unit tests for python circular imports in python-circular-imports/broken/main.py.
Cites source lines establishing preconditions and asserts boundaries.
"""

import sys
import unittest
import types
from pathlib import Path

# Ensure broken directory is on sys.path
BROKEN_DIR = Path(__file__).resolve().parent
if str(BROKEN_DIR) not in sys.path:
    sys.path.insert(0, str(BROKEN_DIR))

import main


class TestCircularImportsBoundary(unittest.TestCase):
    def test_circular_import_precondition_line1(self):
        """Line 1: Direct unmitigated import from shop.product raises ImportError due to circular dependency."""
        # Evict shop from sys.modules to simulate clean import attempt
        for mod in list(sys.modules.keys()):
            if mod.startswith("shop"):
                del sys.modules[mod]

        with self.assertRaises(ImportError) as ctx:
            from shop.product import Product
        self.assertIn("circular import", str(ctx.exception))

    def test_smallest_valid_input_precondition_lines3_5(self):
        """Lines 3-5: Smallest valid input with shipping.
        Literal inputs: name="", price=0.0, quantity=0, add_shipping=True.
        Independently calculated expected output: 0.0 * 0 + 4.99 = 4.99.
        """
        expected = 4.99
        actual = main.calculate_order_total(name="", price=0.0, quantity=0, add_shipping=True)
        self.assertEqual(actual, expected)

    def test_smallest_valid_input_no_shipping_lines3_4(self):
        """Lines 3-4: Smallest valid input without shipping.
        Literal inputs: name="", price=0.0, quantity=0, add_shipping=False.
        Independently calculated expected output: 0.0 * 0 = 0.0.
        """
        expected = 0.0
        actual = main.calculate_order_total(name="", price=0.0, quantity=0, add_shipping=False)
        self.assertEqual(actual, expected)

    def test_ordinary_input_precondition_lines3_5(self):
        """Lines 3-5: Ordinary input from main.py fixture.
        Literal inputs: name="Laptop", price=1000.0, quantity=1, add_shipping=True.
        Independently calculated expected output: 1000.0 * 1 + 4.99 = 1004.99.
        """
        expected = 1004.99
        actual = main.calculate_order_total(name="Laptop", price=1000.0, quantity=1, add_shipping=True)
        self.assertEqual(actual, expected)

    def test_negative_price_guard_line3(self):
        """Line 3: Guard against negative price outside supported domain."""
        with self.assertRaises(ValueError):
            main.calculate_order_total(price=-1.0, quantity=1)

    def test_negative_quantity_guard_line4(self):
        """Line 4: Guard against negative quantity outside supported domain."""
        with self.assertRaises(ValueError):
            main.calculate_order_total(price=10.0, quantity=-1)

    def test_source_order_and_product_boundary_behavior(self):
        """Verify the underlying Order logic from shop.order when circular dependency is resolved via stub."""
        # Evict shop from sys.modules
        for mod in list(sys.modules.keys()):
            if mod.startswith("shop"):
                del sys.modules[mod]

        product_mod = types.ModuleType("shop.product")
        sys.modules["shop.product"] = product_mod
        class StubProduct:
            def __init__(self, name: str, price: float):
                self.name = name
                self.price = price
        product_mod.Product = StubProduct

        from shop.order import Order
        # Test smallest input on Order
        order_small = Order(StubProduct("", 0.0), 0)
        order_small.add_shipping()
        self.assertEqual(order_small.get_total(), 4.99)

        # Test ordinary input on Order
        order_ordinary = Order(StubProduct("Laptop", 1000.0), 1)
        order_ordinary.add_shipping()
        self.assertEqual(order_ordinary.get_total(), 1004.99)


if __name__ == "__main__":
    unittest.main()
