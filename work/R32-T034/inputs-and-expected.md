# R32-T034 — Input Fixtures, Invariants, and Expected Behavior

## 1. Source Contract & Preconditions

Evidence from `ai-python-test-generation/bookstore-project/README.md`, `BEHAVIOR.md`, and `ai-python-test-generation/README.md`:

- **Target Documentation (`ai-python-test-generation/README.md`)**:
  - Lines 1–3: Documents the tutorial "Generating Python Tests With AI: A Suite You Can Trust" providing the bookstore project.
- **Bookstore Endpoints & Layout (`ai-python-test-generation/bookstore-project/README.md`)**:
  - Line 9: `GET /books`: List the catalog (returns list of book dicts).
  - Line 10: `GET /books/{isbn}`: Fetch one book (returns book dict).
  - Line 11: `POST /quotes`: Price an order (prices order using `pricing.py`).
  - Line 12: `POST /reservations`: Hold copies for an order (holds stock using `inventory.py`).
  - Line 13: `GET /stock/{isbn}`: Report how many copies are free (reports available copies).
  - Lines 17–25: Architecture layout (`bookstore/pricing.py`, `bookstore/inventory.py`, `bookstore/catalog.py`, `bookstore/data/books.json`).
- **Inventory Specification (`BEHAVIOR.md`)**:
  - Line 172: "`available` is always `on_hand - reserved`."
  - Lines 174–185: `Inventory(stock=None)` creates an inventory that keeps its own copy of the on-hand counts. Input dictionary must not be mutated.
  - Lines 186–196: `on_hand(isbn)` returns copies physically in the warehouse (integer $\ge 0$). Unknown ISBN returns 0.
  - Lines 197–206: `reserved(isbn)` returns copies held for orders (integer $\ge 0$). Unknown or unreserved ISBN returns 0.
  - Lines 207–216: `available(isbn)` returns copies that can still be reserved.
  - Lines 217–232: `reserve(isbn, quantity)`: requires `quantity >= 1` (line 230), `isbn in _on_hand` (line 231), `quantity <= available(isbn)` (line 228). Returns remaining available count.
  - Lines 233–246: `release(isbn, quantity)`: requires `quantity >= 1` (line 244), `isbn in _on_hand` (line 245), `quantity <= reserved(isbn)` (line 243). Returns updated available count.
  - Lines 247–259: `commit(isbn, quantity)`: requires `quantity >= 1` (line 258), `isbn in _on_hand` (line 259), `quantity <= reserved(isbn)` (line 257). Returns updated on-hand count.
- **Pricing Specification (`BEHAVIOR.md`)**:
  - Lines 9–27: `volume_discount(quantity)`: 0% for 1–9 books, 5% for 10–49 books, 12% for 50+ books.
  - Lines 69–80: `quote_order(quantity, unit_price, member_tier="none", country="US")`: returns total customer pays as `Decimal`.

---

## 2. Public Behavior Guarantees

- **Return Types**:
  - `on_hand`, `reserved`, `available`, `reserve`, `release`, `commit`: `int`.
  - `volume_discount`, `member_discount`, `tax_rate`, `shipping_cost`, `quote_order`: `Decimal`.
  - `Catalog.by_author`: `list[dict]`.
- **Output Shape & Ordering**:
  - Single numerical values for counts and prices.
  - `Catalog.by_author` preserves exact catalog file sequence.
- **Input Immutability**:
  - `stock` dictionary passed to `Inventory(stock)` is never mutated.
  - `Catalog.books` records are read-only and immutable.
- **External Dependencies & Mocking**:
  - File reading in `Catalog` backed by JSON on disk. Tests use `tmp_path` fixtures without live network or external services.

---

## 3. Invariant Definitions

1. **Availability Equation Invariant**:
   For any ISBN at any point in time:
   $$\text{available}(\text{isbn}) = \text{on\_hand}(\text{isbn}) - \text{reserved}(\text{isbn})$$
2. **Conservation of Stock**:
   $$\text{available}(\text{isbn}) + \text{reserved}(\text{isbn}) = \text{on\_hand}(\text{isbn})$$
   $$\forall \text{isbn}, \quad 0 \le \text{reserved}(\text{isbn}) \le \text{on\_hand}(\text{isbn}), \quad \text{available}(\text{isbn}) \ge 0$$
3. **Round-Trip Reserve/Release Invariant**:
   For any valid $(H, R)$ and valid reservation quantity $q \le \text{available}(\text{isbn})$:
   $$\text{release}(\text{isbn}, q) \circ \text{reserve}(\text{isbn}, q) \implies \text{state unchanged}$$
4. **Commit Invariant**:
   $$\text{commit}(\text{isbn}, q) \implies \Delta(\text{on\_hand}) = -q, \; \Delta(\text{reserved}) = -q, \; \Delta(\text{available}) = 0$$
5. **Caller Stock Immutability Invariant**:
   The `stock` dict passed to `Inventory(stock)` remains strictly identical before and after any operations.
6. **Volume Discount Monotonicity Invariant**:
   $$\forall q_1 \le q_2 \in \mathbb{Z}^+, \quad \text{volume\_discount}(q_1) \le \text{volume\_discount}(q_2)$$
7. **Catalog Ordering Invariant**:
   `Catalog.by_author` preserves the relative order of entries as defined in the source JSON catalog.

---

## 4. Literal Smallest-Valid and Ordinary Input Fixtures

### Fixture 1: Smallest Valid Inventory (Single Title, 1 copy)
* **Literal Input**:
  ```python
  stock = {"BOOK-1": 1}
  ```
* **Operations & Expected Outputs**:
  - `on_hand("BOOK-1")` $\rightarrow$ `1`
  - `reserved("BOOK-1")` $\rightarrow$ `0`
  - `available("BOOK-1")` $\rightarrow$ `1`
  - `reserve("BOOK-1", 1)` $\rightarrow$ `0`
  - `reserved("BOOK-1")` $\rightarrow$ `1`
  - `release("BOOK-1", 1)` $\rightarrow$ `1`
  - `stock` remains `{"BOOK-1": 1}` (unmutated)

### Fixture 2: Smallest Valid Pricing Order
* **Literal Input**:
  ```python
  quantity = 1
  unit_price = "0.00"
  member_tier = "none"
  country = "US"
  ```
* **Independently Calculated Expected Output**:
  - Subtotal: $1 \times 0.00 = 0.00$
  - Shipping fee: $\$4.99$ (since subtotal $< \$35.00$)
  - Tax: $\$0.00$
  - Total: `Decimal("4.99")`

### Fixture 3: Ordinary Inventory Multi-step Operations
* **Literal Input**:
  ```python
  stock = {"978-1775093305": 10, "978-1775093312": 5}
  ```
* **Operations & Expected Outputs**:
  - Initial `available("978-1775093305")` $\rightarrow$ `10`
  - `reserve("978-1775093305", 4)` $\rightarrow$ `6` (reserved becomes 4, on-hand remains 10)
  - `commit("978-1775093305", 2)` $\rightarrow$ on-hand becomes 8, reserved becomes 2, available remains 6
  - `release("978-1775093305", 2)` $\rightarrow$ `8` (reserved becomes 0, on-hand remains 8, available becomes 8)

### Fixture 4: Ordinary Pricing Order
* **Literal Input**:
  ```python
  quantity = 2
  unit_price = "20.00"
  member_tier = "pro"
  country = "US"
  ```
* **Independently Calculated Expected Output**:
  - Subtotal: $2 \times 20.00 \times (1 - 0.10) = 36.00$
  - Shipping fee: $\$0.00$ (subtotal $\ge \$35.00$)
  - Tax: $\$0.00$
  - Total: `Decimal("36.00")`

---

## 5. Property / Invariant Test Suite Specification

A deterministic property test suite with fixed seed (`seed = 42`) executes **at least 100 bounded valid cases**:
- Generates random valid stock configurations ($1 \le \text{on\_hand} \le 500$, $1 \le \text{titles} \le 10$).
- Generates sequences of valid `reserve`, `release`, and `commit` operations with quantities $1 \le q \le \text{available}$ or $1 \le q \le \text{reserved}$.
- Evaluates all 7 invariants after every single step.
- Verifies exact types (`int`, `Decimal`), non-negativity, boundedness, and lack of input mutation across 100+ distinct iterations.
