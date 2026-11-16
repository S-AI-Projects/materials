import contextlib
import io
import statistics
import sys
import time
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR / "python-list-comprehension"))

# map.py prints its demonstration output when imported; keep that out of the runner.
with contextlib.redirect_stdout(io.StringIO()):
    from map import TAX_RATE, get_price_with_tax


class GetPriceWithTaxTests(unittest.TestCase):
    def test_single_price_mapping(self):
        self.assertEqual(list(map(get_price_with_tax, [1.0])), [1.08])

    def test_zero_price(self):
        self.assertAlmostEqual(get_price_with_tax(0.0), 0.0)

    def test_ordinary_price(self):
        self.assertAlmostEqual(get_price_with_tax(23.56), 25.4448)

    def test_sample_prices(self):
        prices = [1.09, 23.56, 57.84, 4.56, 6.78]
        expected = [1.1772, 25.4448, 62.4672, 4.9248, 7.3224]
        actual = list(map(get_price_with_tax, prices))
        self.assertEqual(len(actual), len(expected))
        for result, expected_result in zip(actual, expected):
            self.assertAlmostEqual(result, expected_result)


def benchmark():
    print("\nBenchmark: map(get_price_with_tax, prices)")
    print("Input size n | median (seconds) | range (seconds)")
    for n in (1_000, 10_000, 100_000):
        timings = []
        for _ in range(5):
            prices = [float(i % 100) for i in range(n)]
            start = time.perf_counter()
            actual = list(map(get_price_with_tax, prices))
            elapsed = time.perf_counter() - start
            timings.append(elapsed)

            # Correctness is deliberately checked outside the timed interval.
            expected = [price * (1 + TAX_RATE) for price in prices]
            assert actual == expected

        print(
            f"{n:12d} | {statistics.median(timings):.8f} "
            f"| {min(timings):.8f} - {max(timings):.8f}"
        )


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        GetPriceWithTaxTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    benchmark()
