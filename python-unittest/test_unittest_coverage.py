"""Failure path and absent-result tests for unittest."""
import unittest

class TestUnittestFailurePaths(unittest.TestCase):
    def test_empty_suite_absent_result_path(self):
        suite = unittest.TestSuite()
        runner = unittest.TextTestRunner(stream=open("/dev/null", "w"), verbosity=0)
        res = runner.run(suite)
        self.assertEqual(res.testsRun, 0)
        self.assertTrue(res.wasSuccessful())

    def test_assert_equal_mismatch_raises_assertion_error(self):
        tc = unittest.TestCase("__init__")
        with self.assertRaises(AssertionError):
            tc.assertEqual("expected", "actual")

    def test_assert_equal_recovers_after_failure(self):
        tc = unittest.TestCase("__init__")
        try:
            tc.assertEqual(1, 2)
        except AssertionError:
            pass
        tc.assertEqual(42, 42)

    def test_assert_raises_missing_exception_raises_assertion_error(self):
        tc = unittest.TestCase("__init__")
        with self.assertRaises(AssertionError):
            with tc.assertRaises(ValueError):
                pass

    def test_assert_true_failure_and_recovery(self):
        tc = unittest.TestCase("__init__")
        with self.assertRaises(AssertionError):
            tc.assertTrue(False)
        tc.assertTrue(True)

    def test_assert_false_failure_and_recovery(self):
        tc = unittest.TestCase("__init__")
        with self.assertRaises(AssertionError):
            tc.assertFalse(True)
        tc.assertFalse(False)

if __name__ == "__main__":
    unittest.main()
