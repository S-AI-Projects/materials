import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure venv site-packages is in sys.path if running under system python
ROOT_DIR = Path(__file__).resolve().parents[1]
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

# Ensure python-rich-package directory is in sys.path
PKG_DIR = Path(__file__).resolve().parent
if str(PKG_DIR) not in sys.path:
    sys.path.insert(0, str(PKG_DIR))

# Mock module-level file read of crypto_data.json on import
with patch.object(Path, "read_text", return_value="[]"):
    from live_table import make_table

FIXED_TIME = "Sun Nov 15 20:00:00 2026"


def extract_table_rows(table: Table):
    """Extract table rows as a list of string lists."""
    num_rows = len(table.rows)
    return [[col._cells[i] for col in table.columns] for i in range(num_rows)]


class TestMakeTable(unittest.TestCase):
    def setUp(self):
        self.time_patcher = patch("time.asctime", return_value=FIXED_TIME)
        self.mock_asctime = self.time_patcher.start()

    def tearDown(self):
        self.time_patcher.stop()

    def test_case_01_empty_input(self):
        result = make_table([])
        self.assertIsInstance(result, Table)
        self.assertEqual(len(result.rows), 0)
        self.assertEqual(len(result.columns), 5)
        self.assertEqual(
            [c.header for c in result.columns],
            [
                "Symbol",
                "Name",
                "Price (USD)",
                "Volume (24h)",
                "Percent Change (7d)",
            ],
        )
        self.assertEqual(extract_table_rows(result), [])

    def test_case_02_neutral_percentage(self):
        coins = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "price_usd": "50000.00",
                "volume24": 1000.5,
                "percent_change_7d": "0.0",
            }
        ]
        result = make_table(coins)
        self.assertIsInstance(result, Table)
        expected_rows = [["BTC", "Bitcoin", "50000.00", "1000.50", "0.0%"]]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_03_positive_boundary_exact_5(self):
        coins = [
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "price_usd": "3000.00",
                "volume24": 500.0,
                "percent_change_7d": 5.0,
            }
        ]
        result = make_table(coins)
        expected_rows = [["ETH", "Ethereum", "3000.00", "500.00", "5.0%"]]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_04_positive_threshold_above_5_1(self):
        coins = [
            {
                "symbol": "SOL",
                "name": "Solana",
                "price_usd": "150.00",
                "volume24": 250.25,
                "percent_change_7d": 5.1,
            }
        ]
        result = make_table(coins)
        expected_rows = [
            [
                "SOL",
                "Solana",
                "150.00",
                "250.25",
                "[white on dark_green]    5.1%[/]",
            ]
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_05_ordinary_positive_gain(self):
        coins = [
            {
                "symbol": "ADA",
                "name": "Cardano",
                "price_usd": "0.45",
                "volume24": 12345.678,
                "percent_change_7d": "12.4",
            }
        ]
        result = make_table(coins)
        expected_rows = [
            [
                "ADA",
                "Cardano",
                "0.45",
                "12345.68",
                "[white on dark_green]   12.4%[/]",
            ]
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_06_negative_boundary_exact_minus_5(self):
        coins = [
            {
                "symbol": "DOT",
                "name": "Polkadot",
                "price_usd": "6.50",
                "volume24": 80.0,
                "percent_change_7d": -5.0,
            }
        ]
        result = make_table(coins)
        expected_rows = [["DOT", "Polkadot", "6.50", "80.00", "-5.0%"]]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_07_negative_threshold_below_minus_5_1(self):
        coins = [
            {
                "symbol": "DOGE",
                "name": "Dogecoin",
                "price_usd": "0.12",
                "volume24": 999.9,
                "percent_change_7d": -5.1,
            }
        ]
        result = make_table(coins)
        expected_rows = [
            ["DOGE", "Dogecoin", "0.12", "999.90", "[white on red]   -5.1%[/]"]
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_08_large_negative_loss(self):
        coins = [
            {
                "symbol": "LUNA",
                "name": "Terra",
                "price_usd": "0.0001",
                "volume24": 50.0,
                "percent_change_7d": "-35.8",
            }
        ]
        result = make_table(coins)
        expected_rows = [
            ["LUNA", "Terra", "0.0001", "50.00", "[white on red]  -35.8%[/]"]
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_09_zero_volume_and_integer_percent(self):
        coins = [
            {
                "symbol": "ZERO",
                "name": "ZeroCoin",
                "price_usd": "0.00",
                "volume24": 0,
                "percent_change_7d": 0,
            }
        ]
        result = make_table(coins)
        expected_rows = [["ZERO", "ZeroCoin", "0.00", "0.00", "0.0%"]]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_10_integer_volume(self):
        coins = [
            {
                "symbol": "INTV",
                "name": "Integer Volume",
                "price_usd": "10.00",
                "volume24": 1000000,
                "percent_change_7d": "1.5",
            }
        ]
        result = make_table(coins)
        expected_rows = [
            ["INTV", "Integer Volume", "10.00", "1000000.00", "1.5%"]
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_11_tuple_input(self):
        coins = (
            {
                "symbol": "TUP",
                "name": "TupleCoin",
                "price_usd": "1.23",
                "volume24": 45.6,
                "percent_change_7d": "2.0",
            },
        )
        result = make_table(coins)
        expected_rows = [["TUP", "TupleCoin", "1.23", "45.60", "2.0%"]]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_12_sequential_ordering(self):
        coins = [
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
        ]
        result = make_table(coins)
        expected_rows = [
            ["A", "Coin A", "1", "10.00", "1.0%"],
            ["B", "Coin B", "2", "20.00", "2.0%"],
            ["C", "Coin C", "3", "30.00", "3.0%"],
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_13_reversed_ordering(self):
        coins = [
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
        ]
        result = make_table(coins)
        expected_rows = [
            ["C", "Coin C", "3", "30.00", "3.0%"],
            ["B", "Coin B", "2", "20.00", "2.0%"],
            ["A", "Coin A", "1", "10.00", "1.0%"],
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_14_input_mutation_check(self):
        input_data = [
            {
                "symbol": "MUT",
                "name": "MutCoin",
                "price_usd": "1.0",
                "volume24": 10.0,
                "percent_change_7d": "0.0",
                "extra_key": 999,
            }
        ]
        original = copy.deepcopy(input_data)
        make_table(input_data)
        self.assertEqual(input_data, original)

    def test_case_15_positive_interior_4_9(self):
        coins = [
            {
                "symbol": "POS",
                "name": "PosNear",
                "price_usd": "10",
                "volume24": 100,
                "percent_change_7d": 4.9,
            }
        ]
        result = make_table(coins)
        expected_rows = [["POS", "PosNear", "10", "100.00", "4.9%"]]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_16_negative_interior_minus_4_9(self):
        coins = [
            {
                "symbol": "NEG",
                "name": "NegNear",
                "price_usd": "10",
                "volume24": 100,
                "percent_change_7d": -4.9,
            }
        ]
        result = make_table(coins)
        expected_rows = [["NEG", "NegNear", "10", "100.00", "-4.9%"]]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_17_large_gain_over_100(self):
        coins = [
            {
                "symbol": "MOON",
                "name": "MoonCoin",
                "price_usd": "100.00",
                "volume24": 50000,
                "percent_change_7d": "150.5",
            }
        ]
        result = make_table(coins)
        expected_rows = [
            [
                "MOON",
                "MoonCoin",
                "100.00",
                "50000.00",
                "[white on dark_green]  150.5%[/]",
            ]
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_18_extreme_loss_near_100(self):
        coins = [
            {
                "symbol": "REKT",
                "name": "RektCoin",
                "price_usd": "0.00001",
                "volume24": 12.34,
                "percent_change_7d": "-99.9",
            }
        ]
        result = make_table(coins)
        expected_rows = [
            [
                "REKT",
                "RektCoin",
                "0.00001",
                "12.34",
                "[white on red]  -99.9%[/]",
            ]
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_19_high_precision_volume_rounding(self):
        coins = [
            {
                "symbol": "RND",
                "name": "RoundCoin",
                "price_usd": "5.55",
                "volume24": 12345.6789,
                "percent_change_7d": "0.1",
            }
        ]
        result = make_table(coins)
        expected_rows = [["RND", "RoundCoin", "5.55", "12345.68", "0.1%"]]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_20_unicode_name(self):
        coins = [
            {
                "symbol": "UNI",
                "name": "₮ether €uro 日本語",
                "price_usd": "1.00",
                "volume24": 500.0,
                "percent_change_7d": "1.0",
            }
        ]
        result = make_table(coins)
        expected_rows = [
            ["UNI", "₮ether €uro 日本語", "1.00", "500.00", "1.0%"]
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_21_micro_price_string(self):
        coins = [
            {
                "symbol": "SHIB",
                "name": "Shiba",
                "price_usd": "0.00002715",
                "volume24": 987654.32,
                "percent_change_7d": "7.5",
            }
        ]
        result = make_table(coins)
        expected_rows = [
            [
                "SHIB",
                "Shiba",
                "0.00002715",
                "987654.32",
                "[white on dark_green]    7.5%[/]",
            ]
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_case_22_realistic_multi_coin_mix(self):
        coins = [
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
        ]
        result = make_table(coins)
        expected_rows = [
            ["BTC", "Bitcoin", "68500.00", "30000000000.00", "2.4%"],
            [
                "ETH",
                "Ethereum",
                "3500.50",
                "15000000000.00",
                "[white on dark_green]    6.8%[/]",
            ],
            ["USDT", "Tether", "1.00", "45000000000.00", "0.0%"],
            [
                "SOL",
                "Solana",
                "175.20",
                "4000000000.00",
                "[white on red]   -8.2%[/]",
            ],
            ["BNB", "BNB", "590.10", "1200000000.00", "-2.1%"],
        ]
        self.assertEqual(extract_table_rows(result), expected_rows)

    def test_table_structure_and_styles(self):
        result = make_table([])
        self.assertEqual(result.title, f"Crypto Data - {FIXED_TIME}")
        self.assertEqual(str(result.style), "black on grey66")
        self.assertEqual(str(result.header_style), "white on dark_blue")
        columns = result.columns
        self.assertEqual(len(columns), 5)
        self.assertEqual(columns[0].header, "Symbol")
        self.assertEqual(columns[0].justify, "left")
        self.assertIsNone(columns[0].width)
        self.assertEqual(columns[1].header, "Name")
        self.assertEqual(columns[1].justify, "left")
        self.assertEqual(columns[1].width, 30)
        self.assertEqual(columns[2].header, "Price (USD)")
        self.assertEqual(columns[2].justify, "right")
        self.assertIsNone(columns[2].width)
        self.assertEqual(columns[3].header, "Volume (24h)")
        self.assertEqual(columns[3].justify, "right")
        self.assertEqual(columns[3].width, 16)
        self.assertEqual(columns[4].header, "Percent Change (7d)")
        self.assertEqual(columns[4].justify, "right")
        self.assertEqual(columns[4].width, 8)


if __name__ == "__main__":
    unittest.main()
