# Generating Python Tests With AI: A Suite You Can Trust

This folder provides the code examples for the Real Python tutorial [Generating Python Tests With AI: A Suite You Can Trust](https://realpython.com/ai-python-test-generation/).

## Bookstore Project & Core Invariants

The sample code in [`bookstore-project/`](bookstore-project/) provides a bookstore backend featuring order pricing, catalog records, and inventory tracking.

### Core System Invariants

1. **Inventory Availability Invariant**:
   For every ISBN, the available count is strictly equal to on-hand copies minus reserved copies:
   $$\text{available}(\text{isbn}) = \text{on\_hand}(\text{isbn}) - \text{reserved}(\text{isbn})$$
   where $0 \le \text{reserved}(\text{isbn}) \le \text{on\_hand}(\text{isbn})$ and $\text{available}(\text{isbn}) \ge 0$.

2. **Inventory Stock Immutability**:
   The input dictionary supplied to `Inventory(stock)` is never modified by any subsequent operations.

3. **Round-Trip Identity**:
   Reserving $q$ copies followed by releasing $q$ copies restores the inventory state identically.

4. **Pricing Monotonicity**:
   `volume_discount(quantity)` is monotonically non-decreasing with respect to order size:
   $$\forall q_1 \le q_2, \quad \text{volume\_discount}(q_1) \le \text{volume\_discount}(q_2)$$
