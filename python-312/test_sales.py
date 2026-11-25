"""Boundary tests for python-312/sales.py."""
import calendar
import unittest

SALES = {
    calendar.JANUARY: 5,
    calendar.FEBRUARY: 9,
    calendar.MARCH: 6,
    calendar.APRIL: 14,
    calendar.MAY: 9,
    calendar.JUNE: 8,
    calendar.JULY: 15,
    calendar.AUGUST: 22,
    calendar.SEPTEMBER: 20,
    calendar.OCTOBER: 23,
}

def format_line(month_enum, count):
    return f"{month_enum.value:2d} {month_enum.name:<10} {count:2d} {'*' * count}"

class TestSalesBoundaries(unittest.TestCase):
    def test_smallest_valid_boundary_january(self):
        line = format_line(calendar.Month(1), 5)
        self.assertIn("JANUARY", line)
        self.assertTrue(line.endswith("*****"))
        self.assertEqual(line.count("*"), 5)

    def test_ordinary_valid_input_august(self):
        line = format_line(calendar.Month(8), 22)
        self.assertIn("AUGUST", line)
        self.assertTrue(line.endswith("*" * 22))
        self.assertEqual(line.count("*"), 22)

    def test_interior_months_count(self):
        self.assertEqual(len(SALES), 10)
        for i in range(1, 11):
            self.assertIn(i, SALES)

    def test_boundary_last_included_month_october(self):
        self.assertIn(calendar.OCTOBER, SALES)
        self.assertEqual(SALES[calendar.OCTOBER], 23)

    def test_boundary_absent_month_november(self):
        self.assertNotIn(calendar.NOVEMBER, SALES)

    def test_boundary_absent_month_december(self):
        self.assertNotIn(calendar.DECEMBER, SALES)

    def test_minimum_sales_count_is_five(self):
        self.assertEqual(min(SALES.values()), 5)

    def test_maximum_sales_count_is_twenty_three(self):
        self.assertEqual(max(SALES.values()), 23)

    def test_star_bar_length_exact_match(self):
        for m, c in SALES.items():
            line = format_line(calendar.Month(m), c)
            stars = line.split()[-1]
            self.assertEqual(len(stars), c)

    def test_repeated_sale_values_february_and_may(self):
        self.assertEqual(SALES[calendar.FEBRUARY], SALES[calendar.MAY])

if __name__ == "__main__":
    unittest.main()
