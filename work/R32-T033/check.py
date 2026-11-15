#!/usr/bin/env python3
"""
Independent checker for R32-T033: make_table
Exercises the target function against an independent reference.
Verifies return type, output shape, element ordering, styling, and input mutation.
"""

import copy
import sys
from pathlib import Path
from unittest.mock import patch

# Configure sys.path for local environment
ROOT_DIR = Path(__file__).resolve().parents[2]
VENV_PACKAGES = (
    ROOT_DIR
    / ".venv"
    / "lib"
    / f"python{sys.version_info.major}.{sys.version_info.minor}"
    / "site-packages"
)
if VENV_PACKAGES.is_dir() and str(VENV_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_PACKAGES))

from rich.table import Table  # noqa: E402

PKG_DIR = ROOT_DIR / "python-rich-package"
if str(PKG_DIR) not in sys.path:
    sys.path.insert(0, str(PKG_DIR))

# Mock module-level file read of crypto_data.json on import
with patch.object(Path, "read_text", return_value="[]"):
    from live_table import make_table

FIXED_MOCK_TIME = "Sun Nov 15 20:00:00 2026"


def independent_reference(coin_list, mock_time=FIXED_MOCK_TIME):
    """
    Independent reference implementation for make_table.
    Derives expected Table characteristics and rows from documented contract
    without calling the target function.
    """
    expected_title = f"Crypto Data - {mock_time}"
    expected_style = "black on grey66"
    expected_header_style = "white on dark_blue"
    expected_columns = [
        {"header": "Symbol", "justify": "left", "width": None},
        {"header": "Name", "justify": "left", "width": 30},
        {"header": "Price (USD)", "justify": "right", "width": None},
        {"header": "Volume (24h)", "justify": "right", "width": 16},
        {"header": "Percent Change (7d)", "justify": "right", "width": 8},
    ]

    expected_rows = []
    for coin in coin_list:
        symbol = str(coin["symbol"])
        name = str(coin["name"])
        price = str(coin["price_usd"])
        volume = f"{float(coin['volume24']):.2f}"

        pct_val = float(coin["percent_change_7d"])
        pct_raw = f"{pct_val:2.1f}%"
        if pct_val > 5.0:
            pct_formatted = f"[white on dark_green]{pct_raw:>8}[/]"
        elif pct_val < -5.0:
            pct_formatted = f"[white on red]{pct_raw:>8}[/]"
        else:
            pct_formatted = pct_raw

        expected_rows.append([symbol, name, price, volume, pct_formatted])

    return {
        "title": expected_title,
        "style": expected_style,
        "header_style": expected_header_style,
        "columns": expected_columns,
        "rows": expected_rows,
    }


def extract_table_data(table: Table):
    """Extract structural data from a rich.table.Table instance."""
    col_info = [
        {"header": c.header, "justify": c.justify, "width": c.width}
        for c in table.columns
    ]
    num_rows = len(table.rows)
    rows = [[col._cells[i] for col in table.columns] for i in range(num_rows)]
    return {
        "title": table.title,
        "style": str(table.style),
        "header_style": str(table.header_style),
        "columns": col_info,
        "rows": rows,
    }


TEST_CASES = [
    {
        "id": "CASE-01",
        "name": "Empty input boundary",
        "input": [],
    },
    {
        "id": "CASE-02",
        "name": "Neutral percentage (0.0%)",
        "input": [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_usd": "50000.00",
                "volume24": 1000.5,
                "percent_change_7d": "0.0",
            }
        ],
    },
    {
        "id": "CASE-03",
        "name": "Positive threshold boundary (5.0%)",
        "input": [
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "price_usd": "3000.00",
                "volume24": 500.0,
                "percent_change_7d": 5.0,
            }
        ],
    },
    {
        "id": "CASE-04",
        "name": "Positive threshold crossed (5.1%)",
        "input": [
            {
                "symbol": "SOL",
                "name": "Solana",
                "price_usd": "150.00",
                "volume24": 250.25,
                "percent_change_7d": 5.1,
            }
        ],
    },
    {
        "id": "CASE-05",
        "name": "Ordinary strong positive gain (12.4%)",
        "input": [
            {
                "symbol": "ADA",
                "name": "Cardano",
                "price_usd": "0.45",
                "volume24": 12345.678,
                "percent_change_7d": "12.4",
            }
        ],
    },
    {
        "id": "CASE-06",
        "name": "Negative threshold boundary (-5.0%)",
        "input": [
            {
                "symbol": "DOT",
                "name": "Polkadot",
                "price_usd": "6.50",
                "volume24": 80.0,
                "percent_change_7d": -5.0,
            }
        ],
    },
    {
        "id": "CASE-07",
        "name": "Negative threshold crossed (-5.1%)",
        "input": [
            {
                "symbol": "DOGE",
                "name": "Dogecoin",
                "price_usd": "0.12",
                "volume24": 999.9,
                "percent_change_7d": -5.1,
            }
        ],
    },
    {
        "id": "CASE-08",
        "name": "Large negative loss (-35.8%)",
        "input": [
            {
                "symbol": "LUNA",
                "name": "Terra",
                "price_usd": "0.0001",
                "volume24": 50.0,
                "percent_change_7d": "-35.8",
            }
        ],
    },
    {
        "id": "CASE-09",
        "name": "Zero volume and int 0 percent",
        "input": [
            {
                "symbol": "ZERO",
                "name": "ZeroCoin",
                "price_usd": "0.00",
                "volume24": 0,
                "percent_change_7d": 0,
            }
        ],
    },
    {
        "id": "CASE-10",
        "name": "Large integer volume",
        "input": [
            {
                "symbol": "INTV",
                "name": "Integer Volume",
                "price_usd": "10.00",
                "volume24": 1000000,
                "percent_change_7d": "1.5",
            }
        ],
    },
    {
        "id": "CASE-11",
        "name": "Tuple input (iterable protocol)",
        "input": (
            {
                "symbol": "TUP",
                "name": "TupleCoin",
                "price_usd": "1.23",
                "volume24": 45.6,
                "percent_change_7d": "2.0",
            },
        ),
    },
    {
        "id": "CASE-12",
        "name": "Sequential ordering (A, B, C)",
        "input": [
            {
                "symbol": "A",
                "name": "Coin A",
                "price_usd": "1",
                "volume24": 10,
                "percent_change_7d": "1.0",
            },
            {
                "symbol": "B",
                "name": "Coin B",
                "price_usd": "2",
                "volume24": 20,
                "percent_change_7d": "2.0",
            },
            {
                "symbol": "C",
                "name": "Coin C",
                "price_usd": "3",
                "volume24": 30,
                "percent_change_7d": "3.0",
            },
        ],
    },
    {
        "id": "CASE-13",
        "name": "Reversed ordering (C, B, A)",
        "input": [
            {
                "symbol": "C",
                "name": "Coin C",
                "price_usd": "3",
                "volume24": 30,
                "percent_change_7d": "3.0",
            },
            {
                "symbol": "B",
                "name": "Coin B",
                "price_usd": "2",
                "volume24": 20,
                "percent_change_7d": "2.0",
            },
            {
                "symbol": "A",
                "name": "Coin A",
                "price_usd": "1",
                "volume24": 10,
                "percent_change_7d": "1.0",
            },
        ],
    },
    {
        "id": "CASE-14",
        "name": "Input mutation check",
        "input": [
            {
                "symbol": "MUT",
                "name": "MutCoin",
                "price_usd": "1.0",
                "volume24": 10.0,
                "percent_change_7d": "0.0",
                "extra_key": 999,
            }
        ],
    },
    {
        "id": "CASE-15",
        "name": "Positive interior (+4.9%)",
        "input": [
            {
                "symbol": "POS",
                "name": "PosNear",
                "price_usd": "10",
                "volume24": 100,
                "percent_change_7d": 4.9,
            }
        ],
    },
    {
        "id": "CASE-16",
        "name": "Negative interior (-4.9%)",
        "input": [
            {
                "symbol": "NEG",
                "name": "NegNear",
                "price_usd": "10",
                "volume24": 100,
                "percent_change_7d": -4.9,
            }
        ],
    },
    {
        "id": "CASE-17",
        "name": "Large positive gain over 100% (+150.5%)",
        "input": [
            {
                "symbol": "MOON",
                "name": "MoonCoin",
                "price_usd": "100.00",
                "volume24": 50000,
                "percent_change_7d": "150.5",
            }
        ],
    },
    {
        "id": "CASE-18",
        "name": "Extreme loss near 100% (-99.9%)",
        "input": [
            {
                "symbol": "REKT",
                "name": "RektCoin",
                "price_usd": "0.00001",
                "volume24": 12.34,
                "percent_change_7d": "-99.9",
            }
        ],
    },
    {
        "id": "CASE-19",
        "name": "High precision volume rounding",
        "input": [
            {
                "symbol": "RND",
                "name": "RoundCoin",
                "price_usd": "5.55",
                "volume24": 12345.6789,
                "percent_change_7d": "0.1",
            }
        ],
    },
    {
        "id": "CASE-20",
        "name": "Unicode / non-ASCII coin name",
        "input": [
            {
                "symbol": "UNI",
                "name": "₮ether €uro 日本語",
                "price_usd": "1.00",
                "volume24": 500.0,
                "percent_change_7d": "1.0",
            }
        ],
    },
    {
        "id": "CASE-21",
        "name": "Micro-price string representation",
        "input": [
            {
                "symbol": "SHIB",
                "name": "Shiba",
                "price_usd": "0.00002715",
                "volume24": 987654.32,
                "percent_change_7d": "7.5",
            }
        ],
    },
    {
        "id": "CASE-22",
        "name": "Realistic 5-coin streaming batch",
        "input": [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_usd": "68500.00",
                "volume24": 30000000000.0,
                "percent_change_7d": "2.4",
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "price_usd": "3500.50",
                "volume24": 15000000000.0,
                "percent_change_7d": "6.8",
            },
            {
                "symbol": "USDT",
                "name": "Tether",
                "price_usd": "1.00",
                "volume24": 45000000000.0,
                "percent_change_7d": "0.0",
            },
            {
                "symbol": "SOL",
                "name": "Solana",
                "price_usd": "175.20",
                "volume24": 4000000000.0,
                "percent_change_7d": "-8.2",
            },
            {
                "symbol": "BNB",
                "name": "BNB",
                "price_usd": "590.10",
                "volume24": 1200000000.0,
                "percent_change_7d": "-2.1",
            },
        ],
    },
]


def run_all_checks():
    print("=== Running R32-T033 Independent Checker ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")
    print("Testing target: live_table.make_table")
    print(f"Total test cases: {len(TEST_CASES)}\n")

    failures = []
    passed_count = 0

    for tc in TEST_CASES:
        tc_id = tc["id"]
        tc_name = tc["name"]
        raw_input = tc["input"]

        # Preserve a deepcopy to detect any input mutation
        input_copy = copy.deepcopy(raw_input)

        # 1. Independently established expected output
        expected = independent_reference(raw_input, mock_time=FIXED_MOCK_TIME)

        # 2. Actual output from target function under mock
        with patch("time.asctime", return_value=FIXED_MOCK_TIME):
            actual_table = make_table(raw_input)

        # Check return type
        if not isinstance(actual_table, Table):
            msg = f"Return type mismatch: expected rich.table.Table, got {type(actual_table)}"
            failures.append((tc_id, tc_name, msg))
            print(f"[{tc_id}] FAIL: {tc_name} -> {msg}")
            continue

        actual_data = extract_table_data(actual_table)

        # Check title
        if actual_data["title"] != expected["title"]:
            msg = f"Title mismatch: expected {expected['title']!r}, got {actual_data['title']!r}"
            failures.append((tc_id, tc_name, msg))
            print(f"[{tc_id}] FAIL: {tc_name} -> {msg}")
            continue

        # Check styles
        if actual_data["style"] != expected["style"]:
            msg = f"Style mismatch: expected {expected['style']!r}, got {actual_data['style']!r}"
            failures.append((tc_id, tc_name, msg))
            print(f"[{tc_id}] FAIL: {tc_name} -> {msg}")
            continue

        if actual_data["header_style"] != expected["header_style"]:
            msg = f"Header style mismatch: expected {expected['header_style']!r}, got {actual_data['header_style']!r}"
            failures.append((tc_id, tc_name, msg))
            print(f"[{tc_id}] FAIL: {tc_name} -> {msg}")
            continue

        # Check columns
        if actual_data["columns"] != expected["columns"]:
            msg = f"Column mismatch:\nExpected: {expected['columns']}\nGot: {actual_data['columns']}"
            failures.append((tc_id, tc_name, msg))
            print(f"[{tc_id}] FAIL: {tc_name} -> {msg}")
            continue

        # Check rows & ordering
        if actual_data["rows"] != expected["rows"]:
            msg = f"Row data mismatch:\nExpected: {expected['rows']}\nGot: {actual_data['rows']}"
            failures.append((tc_id, tc_name, msg))
            print(f"[{tc_id}] FAIL: {tc_name} -> {msg}")
            continue

        # Check input mutation
        if raw_input != input_copy:
            msg = "Input was mutated during make_table execution!"
            failures.append((tc_id, tc_name, msg))
            print(f"[{tc_id}] FAIL: {tc_name} -> {msg}")
            continue

        passed_count += 1
        print(f"[{tc_id}] PASS: {tc_name} (rows={len(actual_data['rows'])})")

    print(f"\nSummary: {passed_count}/{len(TEST_CASES)} passed.")
    if failures:
        print(f"FAILED {len(failures)} checks.")
        sys.exit(1)
    else:
        print("ALL INDEPENDENT REFERENCE CHECKS PASSED.")
        sys.exit(0)


if __name__ == "__main__":
    run_all_checks()
