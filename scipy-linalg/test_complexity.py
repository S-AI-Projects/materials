"""Complexity and scaling verification for scipy.linalg.solve."""
import numpy as np
import scipy.linalg
import unittest

class TestScipyLinalgComplexity(unittest.TestCase):
    def test_smallest_valid_input_n10(self):
        rng = np.random.default_rng(42)
        A = rng.random((10, 10)) + 10 * np.eye(10)
        b = rng.random(10)
        x = scipy.linalg.solve(A, b)
        res = float(np.linalg.norm(A @ x - b))
        self.assertEqual(x.shape, (10,))
        self.assertLess(res, 1e-9)

    def test_ordinary_valid_input_n50(self):
        rng = np.random.default_rng(42)
        A = rng.random((50, 50)) + 50 * np.eye(50)
        b = rng.random(50)
        x = scipy.linalg.solve(A, b)
        res = float(np.linalg.norm(A @ x - b))
        self.assertEqual(x.shape, (50,))
        self.assertLess(res, 1e-9)

    def test_scaled_input_n200(self):
        rng = np.random.default_rng(42)
        A = rng.random((200, 200)) + 200 * np.eye(200)
        b = rng.random(200)
        x = scipy.linalg.solve(A, b)
        res = float(np.linalg.norm(A @ x - b))
        self.assertEqual(x.shape, (200,))
        self.assertLess(res, 1e-9)

if __name__ == "__main__":
    unittest.main()
