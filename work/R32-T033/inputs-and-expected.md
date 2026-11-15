# R32-T033 — Input and Expected Output for `make_table`

## 1. Source Contract & Evidence

Evidence from `python-rich-package/live_table.py`:

- **Line 13 (`def make_table(coin_list):`)**:
  - The function accepts a single mandatory positional parameter, `coin_list`. No default argument is provided.
- **Lines 15–19 (`table = Table(...)`)**:
  - Instantiates a `rich.table.Table` with:
    - `title=f"Crypto Data - {time.asctime()}"` (dynamic timestamp from standard library `time.asctime()`).
    - `style="black on grey66"`.
    - `header_style="white on dark_blue"`.
- **Lines 20–24 (`table.add_column(...)`)**:
  - Defines 5 columns in fixed order:
    1. `"Symbol"` (default width `None`, default justify `"left"`).
    2. `"Name"` (width `30`, default justify `"left"`).
    3. `"Price (USD)"` (default width `None`, justify `"right"`).
    4. `"Volume (24h)"` (width `16`, justify `"right"`).
    5. `"Percent Change (7d)"` (width `8`, justify `"right"`).
- **Line 25 (`for coin in coin_list:`)**:
  - Iterates through `coin_list`. Requires `coin_list` to be an iterable of mapping objects.
- **Lines 26–32 (Field extraction and formatting)**:
  - `coin["symbol"]`: extracted as-is.
  - `coin["name"]`: extracted as-is.
  - `coin["price_usd"]`: extracted as-is.
  - `coin["volume24"]`: formatted via `f"{coin['volume24']:.2f}"` (requires float/numeric convertible).
  - `coin["percent_change_7d"]`: converted via `float(coin["percent_change_7d"])`.
- **Lines 33–37 (Percent change styling)**:
  - Base formatted string: `pct_change_str = f"{pct_change:2.1f}%"`.
  - Condition `pct_change > 5.0`: styled as `f"[white on dark_green]{pct_change_str:>8}[/]"`.
  - Condition `pct_change < -5.0`: styled as `f"[white on red]{pct_change_str:>8}[/]"`.
  - Neutral `[-5.0, 5.0]`: left unstyled as `pct_change_str` without width 8 right padding.
- **Line 38 (`table.add_row(...)`)**:
  - Appends the row `(symbol, name, price, volume, pct_change_str)` to the table.
- **Line 39 (`return table`)**:
  - Returns the constructed `rich.table.Table` instance.
- **Lines 42–45 (Module-level external I/O)**:
  - Reads `crypto_data.json` relative to current working directory on import. In tests, external I/O and `time.asctime()` are mocked to ensure isolation and deterministic results.

---

## 2. Public Behavior & Guarantees

- **Return Type**: `rich.table.Table`.
- **Output Shape**:
  - Columns: exactly 5 columns with specified headers, justifications, and widths.
  - Rows: exactly `len(coin_list)` rows, each containing 5 string cells.
- **Ordering**:
  - Columns are ordered: `Symbol`, `Name`, `Price (USD)`, `Volume (24h)`, `Percent Change (7d)`.
  - Rows strictly follow the iteration order of `coin_list`.
- **Input Mutation**:
  - `coin_list` and its element dictionaries are read-only; no keys or elements are added, removed, or mutated.
- **External Dependencies & Side Effects**:
  - System clock queried via `time.asctime()`.
  - Rich library formatting tags embedded in strings.
  - No network access or disk writes.

---

## 3. Independent Reference Specification

The expected output is established independently of the implementation under test using explicit logical rules:

1. **Title**: `f"Crypto Data - {MOCK_TIME}"` where `MOCK_TIME = "Sun Nov 15 20:00:00 2026"`.
2. **Columns**:
   - `Symbol` (justify: left, width: None)
   - `Name` (justify: left, width: 30)
   - `Price (USD)` (justify: right, width: None)
   - `Volume (24h)` (justify: right, width: 16)
   - `Percent Change (7d)` (justify: right, width: 8)
3. **Cells**:
   - `c0 = str(coin["symbol"])`
   - `c1 = str(coin["name"])`
   - `c2 = str(coin["price_usd"])`
   - `c3 = f"{float(coin['volume24']):.2f}"`
   - `pct = float(coin["percent_change_7d"])`
   - `pct_raw = f"{pct:2.1f}%"`
   - `c4 = f"[white on dark_green]{pct_raw:>8}[/]" if pct > 5.0 else (f"[white on red]{pct_raw:>8}[/]" if pct < -5.0 else pct_raw)`

---

## 4. Enumerated Test Cases (22 Cases)

### Case 1: Empty input list (Smallest valid boundary)
* **Input**: `[]`
* **Expected Output**:
  * Row count: 0
  * Columns: 5 columns
  * Rows: `[]`

### Case 2: Single coin with zero change (Neutral boundary)
* **Input**: `[{"symbol": "BTC", "name": "Bitcoin", "price_usd": "50000.00", "volume24": 1000.5, "percent_change_7d": "0.0"}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['BTC', 'Bitcoin', '50000.00', '1000.50', '0.0%']`

### Case 3: Positive threshold exact boundary (5.0%)
* **Input**: `[{"symbol": "ETH", "name": "Ethereum", "price_usd": "3000.00", "volume24": 500.0, "percent_change_7d": 5.0}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['ETH', 'Ethereum', '3000.00', '500.00', '5.0%']`
  * Reason: `5.0 > 5.0` is False; no green style tag applied.

### Case 4: Positive threshold just above (5.1%)
* **Input**: `[{"symbol": "SOL", "name": "Solana", "price_usd": "150.00", "volume24": 250.25, "percent_change_7d": 5.1}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['SOL', 'Solana', '150.00', '250.25', '[white on dark_green]    5.1%[/]']`
  * Reason: `5.1 > 5.0` is True; green style tag applied with 8-character right padding.

### Case 5: Ordinary strong positive gain (12.4%)
* **Input**: `[{"symbol": "ADA", "name": "Cardano", "price_usd": "0.45", "volume24": 12345.678, "percent_change_7d": "12.4"}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['ADA', 'Cardano', '0.45', '12345.68', '[white on dark_green]   12.4%[/]']`

### Case 6: Negative threshold exact boundary (-5.0%)
* **Input**: `[{"symbol": "DOT", "name": "Polkadot", "price_usd": "6.50", "volume24": 80.0, "percent_change_7d": -5.0}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['DOT', 'Polkadot', '6.50', '80.00', '-5.0%']`
  * Reason: `-5.0 < -5.0` is False; no red style tag applied.

### Case 7: Negative threshold just below (-5.1%)
* **Input**: `[{"symbol": "DOGE", "name": "Dogecoin", "price_usd": "0.12", "volume24": 999.9, "percent_change_7d": -5.1}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['DOGE', 'Dogecoin', '0.12', '999.90', '[white on red]   -5.1%[/]']`
  * Reason: `-5.1 < -5.0` is True; red style tag applied with 8-character right padding.

### Case 8: Large negative loss (-35.8%)
* **Input**: `[{"symbol": "LUNA", "name": "Terra", "price_usd": "0.0001", "volume24": 50.0, "percent_change_7d": "-35.8"}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['LUNA', 'Terra', '0.0001', '50.00', '[white on red]  -35.8%[/]']`

### Case 9: Zero volume and integer percent change
* **Input**: `[{"symbol": "ZERO", "name": "ZeroCoin", "price_usd": "0.00", "volume24": 0, "percent_change_7d": 0}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['ZERO', 'ZeroCoin', '0.00', '0.00', '0.0%']`

### Case 10: Integer volume requiring float formatting
* **Input**: `[{"symbol": "INTV", "name": "Integer Volume", "price_usd": "10.00", "volume24": 1000000, "percent_change_7d": "1.5"}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['INTV', 'Integer Volume', '10.00', '1000000.00', '1.5%']`

### Case 11: Tuple input (iterable protocol verification)
* **Input**: `(({"symbol": "TUP", "name": "TupleCoin", "price_usd": "1.23", "volume24": 45.6, "percent_change_7d": "2.0"},))`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['TUP', 'TupleCoin', '1.23', '45.60', '2.0%']`

### Case 12: Sequential ordering (3 items: A, B, C)
* **Input**:
  ```python
  [
      {"symbol": "A", "name": "Coin A", "price_usd": "1", "volume24": 10, "percent_change_7d": "1.0"},
      {"symbol": "B", "name": "Coin B", "price_usd": "2", "volume24": 20, "percent_change_7d": "2.0"},
      {"symbol": "C", "name": "Coin C", "price_usd": "3", "volume24": 30, "percent_change_7d": "3.0"},
  ]
  ```
* **Expected Output**:
  * Row count: 3
  * Row 0: `['A', 'Coin A', '1', '10.00', '1.0%']`
  * Row 1: `['B', 'Coin B', '2', '20.00', '2.0%']`
  * Row 2: `['C', 'Coin C', '3', '30.00', '3.0%']`

### Case 13: Reversed ordering (3 items: C, B, A)
* **Input**:
  ```python
  [
      {"symbol": "C", "name": "Coin C", "price_usd": "3", "volume24": 30, "percent_change_7d": "3.0"},
      {"symbol": "B", "name": "Coin B", "price_usd": "2", "volume24": 20, "percent_change_7d": "2.0"},
      {"symbol": "A", "name": "Coin A", "price_usd": "1", "volume24": 10, "percent_change_7d": "1.0"},
  ]
  ```
* **Expected Output**:
  * Row count: 3
  * Row 0: `['C', 'Coin C', '3', '30.00', '3.0%']`
  * Row 1: `['B', 'Coin B', '2', '20.00', '2.0%']`
  * Row 2: `['A', 'Coin A', '1', '10.00', '1.0%']`

### Case 14: Input mutation verification
* **Input**: list containing a dictionary with extra fields `{"symbol": "MUT", "name": "MutCoin", "price_usd": "1.0", "volume24": 10.0, "percent_change_7d": "0.0", "extra_key": 999}`
* **Expected Output**:
  * Row count: 1
  * Input dictionary retains `"extra_key": 999` and no keys are altered or added.

### Case 15: Positive interior threshold (+4.9%)
* **Input**: `[{"symbol": "POS", "name": "PosNear", "price_usd": "10", "volume24": 100, "percent_change_7d": 4.9}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['POS', 'PosNear', '10', '100.00', '4.9%']`

### Case 16: Negative interior threshold (-4.9%)
* **Input**: `[{"symbol": "NEG", "name": "NegNear", "price_usd": "10", "volume24": 100, "percent_change_7d": -4.9}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['NEG', 'NegNear', '10', '100.00', '-4.9%']`

### Case 17: Large positive gain over 100% (+150.5%)
* **Input**: `[{"symbol": "MOON", "name": "MoonCoin", "price_usd": "100.00", "volume24": 50000, "percent_change_7d": "150.5"}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['MOON', 'MoonCoin', '100.00', '50000.00', '[white on dark_green]  150.5%[/]']`

### Case 18: Extreme loss near -100% (-99.9%)
* **Input**: `[{"symbol": "REKT", "name": "RektCoin", "price_usd": "0.00001", "volume24": 12.34, "percent_change_7d": "-99.9"}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['REKT', 'RektCoin', '0.00001', '12.34', '[white on red]  -99.9%[/]']`

### Case 19: High-precision volume rounding
* **Input**: `[{"symbol": "RND", "name": "RoundCoin", "price_usd": "5.55", "volume24": 12345.6789, "percent_change_7d": "0.1"}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['RND', 'RoundCoin', '5.55', '12345.68', '0.1%']`

### Case 20: Unicode / non-ASCII name support
* **Input**: `[{"symbol": "UNI", "name": "₮ether €uro 日本語", "price_usd": "1.00", "volume24": 500.0, "percent_change_7d": "1.0"}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['UNI', '₮ether €uro 日本語', '1.00', '500.00', '1.0%']`

### Case 21: Sub-cent micro-price string
* **Input**: `[{"symbol": "SHIB", "name": "Shiba", "price_usd": "0.00002715", "volume24": 987654.32, "percent_change_7d": "7.5"}]`
* **Expected Output**:
  * Row count: 1
  * Row 0: `['SHIB', 'Shiba', '0.00002715', '987654.32', '[white on dark_green]    7.5%[/]']`

### Case 22: Realistic multi-coin mix (5 coins)
* **Input**:
  ```python
  [
      {"symbol": "BTC", "name": "Bitcoin", "price_usd": "68500.00", "volume24": 30000000000.0, "percent_change_7d": "2.4"},
      {"symbol": "ETH", "name": "Ethereum", "price_usd": "3500.50", "volume24": 15000000000.0, "percent_change_7d": "6.8"},
      {"symbol": "USDT", "name": "Tether", "price_usd": "1.00", "volume24": 45000000000.0, "percent_change_7d": "0.0"},
      {"symbol": "SOL", "name": "Solana", "price_usd": "175.20", "volume24": 4000000000.0, "percent_change_7d": "-8.2"},
      {"symbol": "BNB", "name": "BNB", "price_usd": "590.10", "volume24": 1200000000.0, "percent_change_7d": "-2.1"},
  ]
  ```
* **Expected Output**:
  * Row count: 5
  * Row 0: `['BTC', 'Bitcoin', '68500.00', '30000000000.00', '2.4%']`
  * Row 1: `['ETH', 'Ethereum', '3500.50', '15000000000.00', '[white on dark_green]    6.8%[/]']`
  * Row 2: `['USDT', 'Tether', '1.00', '45000000000.00', '0.0%']`
  * Row 3: `['SOL', 'Solana', '175.20', '4000000000.00', '[white on red]   -8.2%[/]']`
  * Row 4: `['BNB', 'BNB', '590.10', '1200000000.00', '-2.1%']`
