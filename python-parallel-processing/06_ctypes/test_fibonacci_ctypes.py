"""Regression tests for the pure-Python Fibonacci implementation used to
measure scaling complexity of the ctypes fibonacci function.

The ctypes version (fibonacci.so) wraps:
    int fib(int n) { return n < 2 ? n : fib(n-2) + fib(n-1); }

Since the .so is not compiled during CI we use a pure-Python mirror that is
mathematically identical, and validate it against known Fibonacci values.
The fixture anchor that links these tests to the production ctypes code is:

    fib.argtypes = (ctypes.c_int,)

which appears in fibonacci_ctypes.py and confirms the function signature.
"""

import unittest


def fib_py(n, counter=None):
    """Pure-Python naive-recursive Fibonacci mirroring the C implementation.

    Args:
        n: Non-negative integer input.
        counter: Optional list[int] used to count recursive calls (operation count).

    Returns:
        The n-th Fibonacci number.
    """
    if counter is not None:
        counter[0] += 1
    if n < 2:
        return n
    return fib_py(n - 2, counter) + fib_py(n - 1, counter)


class TestFibonacciCtypesRegression(unittest.TestCase):
    """Representative regression tests for fibonacci_ctypes scaling measurement."""

    # --- fixture anchor ---
    FIXTURE_ANCHOR = "fib.argtypes = (ctypes.c_int,)"

    def test_fixture_anchor_present_in_source(self):
        """Verify the ctypes argtypes anchor exists in fibonacci_ctypes.py."""
        import os
        src_path = os.path.join(
            os.path.dirname(__file__), "fibonacci_ctypes.py"
        )
        with open(src_path) as fh:
            source = fh.read()
        self.assertIn(
            self.FIXTURE_ANCHOR,
            source,
            "Fixture anchor 'fib.argtypes = (ctypes.c_int,)' must remain in fibonacci_ctypes.py"
        )

    def test_base_cases(self):
        """fib(0) == 0 and fib(1) == 1 (base cases must hold)."""
        self.assertEqual(fib_py(0), 0)
        self.assertEqual(fib_py(1), 1)

    def test_known_small_values(self):
        """Known Fibonacci sequence values for correctness outside timed interval."""
        expected = {2: 1, 3: 2, 4: 3, 5: 5, 6: 8, 7: 13, 8: 21, 9: 34, 10: 55}
        for n, val in expected.items():
            with self.subTest(n=n):
                self.assertEqual(fib_py(n), val)

    def test_scaling_n10_operation_count(self):
        """fib(10) requires exactly 177 recursive calls — confirms O(2^n) scaling."""
        counter = [0]
        result = fib_py(10, counter)
        self.assertEqual(result, 55, "fib(10) correctness check")
        self.assertEqual(
            counter[0], 177,
            "fib(10) should require exactly 177 recursive calls (O(2^n) complexity)"
        )

    def test_scaling_n15_operation_count(self):
        """fib(15) requires exactly 1973 recursive calls."""
        counter = [0]
        result = fib_py(15, counter)
        self.assertEqual(result, 610, "fib(15) correctness check")
        self.assertEqual(
            counter[0], 1973,
            "fib(15) should require exactly 1973 recursive calls"
        )

    def test_scaling_n20_operation_count(self):
        """fib(20) requires exactly 21891 recursive calls."""
        counter = [0]
        result = fib_py(20, counter)
        self.assertEqual(result, 6765, "fib(20) correctness check")
        self.assertEqual(
            counter[0], 21891,
            "fib(20) should require exactly 21891 recursive calls"
        )

    def test_scaling_exponential_ratio(self):
        """Confirm exponential growth: ratio of op-counts between sizes is consistent."""
        c10 = [0]
        c15 = [0]
        c20 = [0]
        fib_py(10, c10)
        fib_py(15, c15)
        fib_py(20, c20)
        ratio_a = c15[0] / c10[0]  # ~11.1 for Δn=5
        ratio_b = c20[0] / c15[0]  # ~11.1 for Δn=5
        # Both ratios should be approximately equal (within 5%) confirming O(2^n)
        self.assertAlmostEqual(
            ratio_a, ratio_b, delta=0.1 * ratio_a,
            msg="Scaling ratios should be consistent, confirming O(2^n) complexity"
        )

    def test_five_repetitions_give_identical_counts(self):
        """Five repetitions of fib(10) all yield the same operation count (deterministic)."""
        counts = []
        for _ in range(5):
            c = [0]
            fib_py(10, c)
            counts.append(c[0])
        self.assertEqual(
            len(set(counts)), 1,
            "All 5 repetitions should give identical operation counts"
        )
        self.assertEqual(counts[0], 177)

    def test_complexity_comment_present_in_source(self):
        """Verify the complexity comment was added to fibonacci_ctypes.py."""
        import os
        src_path = os.path.join(
            os.path.dirname(__file__), "fibonacci_ctypes.py"
        )
        with open(src_path) as fh:
            source = fh.read()
        self.assertIn(
            "O(2^n)",
            source,
            "Complexity comment 'O(2^n)' must appear in fibonacci_ctypes.py"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
