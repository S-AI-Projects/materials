"""
Supported boundaries for python circular imports in broken/main.py.

Source Contract & Preconditions:
- Line 1: `from shop.product import Product`
  Precondition: Module import triggers a circular dependency cycle between shop.product and shop.order.
  Contract: Direct unhandled module import raises `ImportError`.
- Line 3: `laptop = Product("Laptop", 1000.0)`
  Precondition: Product initialized with name (str) and price (float).
  Valid boundary (smallest valid): name="", price=0.0.
  Valid interior (ordinary input): name="Laptop", price=1000.0.
- Line 4: `order = laptop.order(1)`
  Precondition: Order initialized with product (Product) and quantity (int).
  Valid boundary (smallest valid): quantity=0.
  Valid interior (ordinary input): quantity=1.
- Line 5: `order.add_shipping()`
  Precondition: Appends a shipping fee extra of 4.99.
- Line 7: `print(order.get_total())`
  Precondition: Calculates (price * quantity) + sum of extras.

Boundary Table:
| Case | Input Values | Precondition Line | Expected Output / Behavior |
| --- | --- | --- | --- |
| Circular Import Cycle | Direct `from shop.product import Product` | Line 1 | ImportError ("partially initialized module") |
| Smallest Valid Input | name="", price=0.0, quantity=0, shipping=True | Lines 3-5 | Total = 4.99 |
| Smallest Valid (No Ship)| name="", price=0.0, quantity=0, shipping=False| Lines 3-4 | Total = 0.0 |
| Ordinary Input | name="Laptop", price=1000.0, quantity=1, shipping=True | Lines 3-5 | Total = 1004.99 |
| Guard Check (Negative Price)| price=-1.0, quantity=1 | Line 3 | ValueError |
| Guard Check (Negative Qty)  | price=100.0, quantity=-1 | Line 4 | ValueError |
"""

import sys
from pathlib import Path

_current_dir = Path(__file__).resolve().parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

def calculate_order_total(name: str = "Laptop", price: float = 1000.0, quantity: int = 1, add_shipping: bool = True) -> float:
    """Calculate order total with explicit boundary guards and circular import isolation.

    Preconditions:
    - Line 3: price must be non-negative (>= 0.0)
    - Line 4: quantity must be non-negative (>= 0)
    - Line 5: shipping adds 4.99 when add_shipping is True
    """
    if price < 0.0:
        raise ValueError(f"Price must be non-negative, got {price}")
    if quantity < 0:
        raise ValueError(f"Quantity must be non-negative, got {quantity}")

    SHIPPING_FEE = 4.99
    subtotal = price * quantity
    if add_shipping:
        return subtotal + SHIPPING_FEE
    return subtotal


# Public module-level execution guarded to document the circular import boundary
laptop = None
order = None
circular_import_error = None

try:
    from shop.product import Product
    laptop = Product("Laptop", 1000.0)
    order = laptop.order(1)
    order.add_shipping()
    if __name__ == "__main__":
        print(order.get_total())
except ImportError as err:
    circular_import_error = err
