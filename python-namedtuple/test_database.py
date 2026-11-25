"""Refactoring regression tests for get_column_names."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_column_names, get_passenger_by_id, PASSENGER_COLUMNS

class TestDatabaseContract(unittest.TestCase):
    def test_smallest_valid_input_passenger(self):
        expected = ("id", "first_name", "last_name", "class")
        self.assertEqual(get_column_names("passenger"), expected)

    def test_passenger_columns_constant_equality(self):
        self.assertEqual(get_column_names("passenger"), PASSENGER_COLUMNS)

    def test_returns_tuple_type(self):
        self.assertIsInstance(get_column_names("passenger"), tuple)

    def test_tuple_length_four(self):
        self.assertEqual(len(get_column_names("passenger")), 4)

    def test_unknown_table_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_column_names("unknown_table")

    def test_empty_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_column_names("")

    def test_idempotence_and_repeatability(self):
        self.assertEqual(get_column_names("passenger"), get_column_names("passenger"))

    def test_companion_get_passenger_by_id(self):
        res = get_passenger_by_id(1234)
        self.assertEqual(res, (1234, "John", "Doe", "Business"))

if __name__ == "__main__":
    unittest.main()
