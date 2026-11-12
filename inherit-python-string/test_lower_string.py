import unittest

from lower_string import LowerString


class TestLowerString(unittest.TestCase):
    """Contract tests for LowerString.

    Preconditions established by lower_string.py:
    - Line 1: LowerString inherits from str.
    - Line 3: The constructor accepts a string.
    - Line 4: The intended transformation is string.lower().
    """

    def test_smallest_valid_input(self):
        # Independent expected result: lowercasing "" gives "".
        input_string = ""
        expected = ""

        actual = LowerString(input_string)

        self.assertEqual(
            actual,
            expected,
            f"Input={input_string!r}, "
            f"expected={expected!r}, actual={actual!r}",
        )

    def test_ordinary_input(self):
        # Independent expected result: PyThOn becomes python.
        input_string = "PyThOn"
        expected = "python"

        actual = LowerString(input_string)

        self.assertEqual(
            actual,
            expected,
            f"Input={input_string!r}, "
            f"expected={expected!r}, actual={actual!r}",
        )

    def test_repeated_values(self):
        # Independent expected result: AaAa becomes aaaa.
        input_string = "AaAa"
        expected = "aaaa"

        actual = LowerString(input_string)

        self.assertEqual(
            actual,
            expected,
            f"Input={input_string!r}, "
            f"expected={expected!r}, actual={actual!r}",
        )

    def test_input_is_not_mutated(self):
        # Strings are immutable; the original input must remain unchanged.
        input_string = "PyThOn"
        expected_original = "PyThOn"

        LowerString(input_string)

        self.assertEqual(
            input_string,
            expected_original,
        )

    def test_returned_type(self):
        input_string = "HELLO"
        expected_type = LowerString

        actual = LowerString(input_string)

        self.assertIsInstance(actual, expected_type)


if __name__ == "__main__":
    unittest.main()
