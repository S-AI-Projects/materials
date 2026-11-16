"""Focused reference-comparison regression tests for employee.py.

Preconditions established by ipython-console/employee.py:
    - Line 1: first_name = "Han"
    - Line 2: last_name = "Solo"
    - Line 3: department = "Accounts"
    - Line 4: salary = 1000
"""

import copy
import sys
import unittest
from pathlib import Path

# Ensure ipython-console directory is in sys.path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import employee  # noqa: E402
from employee import ipython_console  # noqa: E402


def independent_oracle(*args, **kwargs):
    """Independent reference implementation for employee inspection.

    Derives expected employee dictionary independently without calling
    ipython_console. Uses separate string construction and dictionary
    instantiation mechanisms.
    """
    if args and isinstance(args[0], dict) and len(args) == 1 and not kwargs:
        d = args[0]
        fn = d.get("first_name", "")
        ln = d.get("last_name", "")
        dept = d.get("department", "")
        sal = d.get("salary", 0)
    elif (
        args
        and isinstance(args[0], (list, tuple))
        and len(args) == 1
        and not kwargs
    ):
        seq = args[0]
        fn = seq[0] if len(seq) > 0 else ""
        ln = seq[1] if len(seq) > 1 else ""
        dept = seq[2] if len(seq) > 2 else ""
        sal = seq[3] if len(seq) > 3 else 0
    elif args or kwargs:
        fn = kwargs.get("first_name", args[0] if len(args) > 0 else "Han")
        ln = kwargs.get("last_name", args[1] if len(args) > 1 else "Solo")
        dept = kwargs.get(
            "department", args[2] if len(args) > 2 else "Accounts"
        )
        sal = kwargs.get("salary", args[3] if len(args) > 3 else 1000)
    else:
        # Preconditions established by lines 1-4
        fn, ln, dept, sal = "Han", "Solo", "Accounts", 1000

    # Independently derive full_name using formatting without list join
    if fn and ln:
        expected_full_name = f"{fn} {ln}"
    elif fn:
        expected_full_name = f"{fn}"
    elif ln:
        expected_full_name = f"{ln}"
    else:
        expected_full_name = ""

    # Construct result using dict constructor over zipped pairs
    keys = ("first_name", "last_name", "department", "salary", "full_name")
    vals = (fn, ln, dept, sal, expected_full_name)
    return dict(zip(keys, vals))


# 24 diverse test cases covering the input domain
TEST_CASES = [
    {
        "id": "TC-01",
        "description": "Smallest valid input (empty strings, zero salary)",
        "precondition": "employee.py lines 1-4 string/numeric domain lower bounds",
        "args": ("", "", "", 0),
        "kwargs": {},
        "expected": {
            "first_name": "",
            "last_name": "",
            "department": "",
            "salary": 0,
            "full_name": "",
        },
    },
    {
        "id": "TC-02",
        "description": "Ordinary input (Han Solo from employee.py)",
        "precondition": "employee.py lines 1-4 standard employee fixture",
        "args": ("Han", "Solo", "Accounts", 1000),
        "kwargs": {},
        "expected": {
            "first_name": "Han",
            "last_name": "Solo",
            "department": "Accounts",
            "salary": 1000,
            "full_name": "Han Solo",
        },
    },
    {
        "id": "TC-03",
        "description": "Default arguments invocation (empty args/kwargs)",
        "precondition": "employee.py lines 1-4 default module constants",
        "args": (),
        "kwargs": {},
        "expected": {
            "first_name": "Han",
            "last_name": "Solo",
            "department": "Accounts",
            "salary": 1000,
            "full_name": "Han Solo",
        },
    },
    {
        "id": "TC-04",
        "description": "Single character names",
        "precondition": "employee.py lines 1-2 minimal non-empty string length",
        "args": ("A", "B", "R&D", 500),
        "kwargs": {},
        "expected": {
            "first_name": "A",
            "last_name": "B",
            "department": "R&D",
            "salary": 500,
            "full_name": "A B",
        },
    },
    {
        "id": "TC-05",
        "description": "Alphanumeric identifiers in name fields",
        "precondition": "employee.py lines 1-2 string representation",
        "args": ("User1", "Test2", "IT", 2500),
        "kwargs": {},
        "expected": {
            "first_name": "User1",
            "last_name": "Test2",
            "department": "IT",
            "salary": 2500,
            "full_name": "User1 Test2",
        },
    },
    {
        "id": "TC-06",
        "description": "Hyphenated last name",
        "precondition": "employee.py line 2 hyphenated string token",
        "args": ("Leia", "Organa-Solo", "Executive", 5000),
        "kwargs": {},
        "expected": {
            "first_name": "Leia",
            "last_name": "Organa-Solo",
            "department": "Executive",
            "salary": 5000,
            "full_name": "Leia Organa-Solo",
        },
    },
    {
        "id": "TC-07",
        "description": "Multi-word first name containing spaces",
        "precondition": "employee.py line 1 compound string token",
        "args": ("Mary Jane", "Watson", "Editorial", 3200),
        "kwargs": {},
        "expected": {
            "first_name": "Mary Jane",
            "last_name": "Watson",
            "department": "Editorial",
            "salary": 3200,
            "full_name": "Mary Jane Watson",
        },
    },
    {
        "id": "TC-08",
        "description": "First name only (empty last name)",
        "precondition": "employee.py line 2 empty string boundary",
        "args": ("Chewbacca", "", "Co-Pilot", 800),
        "kwargs": {},
        "expected": {
            "first_name": "Chewbacca",
            "last_name": "",
            "department": "Co-Pilot",
            "salary": 800,
            "full_name": "Chewbacca",
        },
    },
    {
        "id": "TC-09",
        "description": "Last name only (empty first name)",
        "precondition": "employee.py line 1 empty string boundary",
        "args": ("", "Yoda", "Jedi Council", 0),
        "kwargs": {},
        "expected": {
            "first_name": "",
            "last_name": "Yoda",
            "department": "Jedi Council",
            "salary": 0,
            "full_name": "Yoda",
        },
    },
    {
        "id": "TC-10",
        "description": "Zero salary boundary with named employee",
        "precondition": "employee.py line 4 zero salary threshold",
        "args": ("Luke", "Skywalker", "Jedi", 0),
        "kwargs": {},
        "expected": {
            "first_name": "Luke",
            "last_name": "Skywalker",
            "department": "Jedi",
            "salary": 0,
            "full_name": "Luke Skywalker",
        },
    },
    {
        "id": "TC-11",
        "description": "Negative salary boundary (accounting deduction)",
        "precondition": "employee.py line 4 signed numeric domain",
        "args": ("Lando", "Calrissian", "Operations", -500),
        "kwargs": {},
        "expected": {
            "first_name": "Lando",
            "last_name": "Calrissian",
            "department": "Operations",
            "salary": -500,
            "full_name": "Lando Calrissian",
        },
    },
    {
        "id": "TC-12",
        "description": "Floating point salary with fractional cents",
        "precondition": "employee.py line 4 float numeric support",
        "args": ("Wedge", "Antilles", "Flight", 1250.75),
        "kwargs": {},
        "expected": {
            "first_name": "Wedge",
            "last_name": "Antilles",
            "department": "Flight",
            "salary": 1250.75,
            "full_name": "Wedge Antilles",
        },
    },
    {
        "id": "TC-13",
        "description": "Large integer salary",
        "precondition": "employee.py line 4 high-magnitude integer",
        "args": ("Palpatine", "Emperor", "Administration", 1000000),
        "kwargs": {},
        "expected": {
            "first_name": "Palpatine",
            "last_name": "Emperor",
            "department": "Administration",
            "salary": 1000000,
            "full_name": "Palpatine Emperor",
        },
    },
    {
        "id": "TC-14",
        "description": "Unicode accented string attributes",
        "precondition": "employee.py lines 1-3 UTF-8 unicode encoding",
        "args": ("Amélie", "Poulain", "Café", 1800),
        "kwargs": {},
        "expected": {
            "first_name": "Amélie",
            "last_name": "Poulain",
            "department": "Café",
            "salary": 1800,
            "full_name": "Amélie Poulain",
        },
    },
    {
        "id": "TC-15",
        "description": "Non-ASCII CJK string attributes",
        "precondition": "employee.py lines 1-3 multi-byte character support",
        "args": ("太郎", "山田", "Engineering", 4500),
        "kwargs": {},
        "expected": {
            "first_name": "太郎",
            "last_name": "山田",
            "department": "Engineering",
            "salary": 4500,
            "full_name": "太郎 山田",
        },
    },
    {
        "id": "TC-16",
        "description": "Special punctuation characters in department",
        "precondition": "employee.py line 3 punctuation symbol support",
        "args": ("C-3PO", "Droid", "Protocol & Translation", 150),
        "kwargs": {},
        "expected": {
            "first_name": "C-3PO",
            "last_name": "Droid",
            "department": "Protocol & Translation",
            "salary": 150,
            "full_name": "C-3PO Droid",
        },
    },
    {
        "id": "TC-17",
        "description": "Multi-word spaced department name",
        "precondition": "employee.py line 3 spaced string token",
        "args": ("R2-D2", "Astromech", "Starship Maintenance", 200),
        "kwargs": {},
        "expected": {
            "first_name": "R2-D2",
            "last_name": "Astromech",
            "department": "Starship Maintenance",
            "salary": 200,
            "full_name": "R2-D2 Astromech",
        },
    },
    {
        "id": "TC-18",
        "description": "All lowercase string values",
        "precondition": "employee.py lines 1-3 case variance",
        "args": ("obi-wan", "kenobi", "general", 3000),
        "kwargs": {},
        "expected": {
            "first_name": "obi-wan",
            "last_name": "kenobi",
            "department": "general",
            "salary": 3000,
            "full_name": "obi-wan kenobi",
        },
    },
    {
        "id": "TC-19",
        "description": "All uppercase string values",
        "precondition": "employee.py lines 1-3 case variance",
        "args": ("BOBA", "FETT", "BOUNTY", 7500),
        "kwargs": {},
        "expected": {
            "first_name": "BOBA",
            "last_name": "FETT",
            "department": "BOUNTY",
            "salary": 7500,
            "full_name": "BOBA FETT",
        },
    },
    {
        "id": "TC-20",
        "description": "Long department description string",
        "precondition": "employee.py line 3 long string support",
        "args": (
            "Ahsoka",
            "Tano",
            "Department of Outer Rim Exploration and Peacekeeping Operations",
            3800,
        ),
        "kwargs": {},
        "expected": {
            "first_name": "Ahsoka",
            "last_name": "Tano",
            "department": "Department of Outer Rim Exploration and Peacekeeping Operations",
            "salary": 3800,
            "full_name": "Ahsoka Tano",
        },
    },
    {
        "id": "TC-21",
        "description": "Sub-dollar fractional salary",
        "precondition": "employee.py line 4 decimal fraction support",
        "args": ("Wicket", "Ewok", "Scouting", 0.99),
        "kwargs": {},
        "expected": {
            "first_name": "Wicket",
            "last_name": "Ewok",
            "department": "Scouting",
            "salary": 0.99,
            "full_name": "Wicket Ewok",
        },
    },
    {
        "id": "TC-22",
        "description": "High-precision float salary",
        "precondition": "employee.py line 4 float precision handling",
        "args": ("Bail", "Organa", "Senate", 9999.999),
        "kwargs": {},
        "expected": {
            "first_name": "Bail",
            "last_name": "Organa",
            "department": "Senate",
            "salary": 9999.999,
            "full_name": "Bail Organa",
        },
    },
    {
        "id": "TC-23",
        "description": "Dictionary input mapping",
        "precondition": "employee.py lines 1-4 dictionary record support",
        "args": (
            {
                "first_name": "Cassian",
                "last_name": "Andor",
                "department": "Intelligence",
                "salary": 2800,
            },
        ),
        "kwargs": {},
        "expected": {
            "first_name": "Cassian",
            "last_name": "Andor",
            "department": "Intelligence",
            "salary": 2800,
            "full_name": "Cassian Andor",
        },
    },
    {
        "id": "TC-24",
        "description": "Tuple input sequence",
        "precondition": "employee.py lines 1-4 sequence record support",
        "args": (("Jyn", "Erso", "Special Ops", 2100),),
        "kwargs": {},
        "expected": {
            "first_name": "Jyn",
            "last_name": "Erso",
            "department": "Special Ops",
            "salary": 2100,
            "full_name": "Jyn Erso",
        },
    },
]


class TestEmployee(unittest.TestCase):
    """Reference-comparison regression tests for employee.py."""

    def test_preconditions_preserved(self):
        """Verify module-level variables are preserved intact (lines 1-4)."""
        self.assertEqual(employee.first_name, "Han")
        self.assertEqual(employee.last_name, "Solo")
        self.assertEqual(employee.department, "Accounts")
        self.assertEqual(employee.salary, 1000)

    def test_smallest_valid_input(self):
        """Verify smallest valid input produces expected result."""
        args = ("", "", "", 0)
        expected = {
            "first_name": "",
            "last_name": "",
            "department": "",
            "salary": 0,
            "full_name": "",
        }
        oracle_res = independent_oracle(*args)
        actual = ipython_console(*args)
        self.assertEqual(actual, expected)
        self.assertEqual(actual, oracle_res)

    def test_ordinary_input(self):
        """Verify ordinary input from employee.py lines 1-4."""
        args = ("Han", "Solo", "Accounts", 1000)
        expected = {
            "first_name": "Han",
            "last_name": "Solo",
            "department": "Accounts",
            "salary": 1000,
            "full_name": "Han Solo",
        }
        oracle_res = independent_oracle(*args)
        actual = ipython_console(*args)
        self.assertEqual(actual, expected)
        self.assertEqual(actual, oracle_res)

    def test_output_type_and_shape(self):
        """Verify return type is dict with exact 5 documented keys."""
        actual = ipython_console()
        self.assertIsInstance(actual, dict)
        expected_keys = [
            "first_name",
            "last_name",
            "department",
            "salary",
            "full_name",
        ]
        self.assertEqual(list(actual.keys()), expected_keys)

    def test_input_immutability(self):
        """Verify input containers and parameters are not mutated."""
        input_dict = {
            "first_name": "Luke",
            "last_name": "Skywalker",
            "department": "Jedi",
            "salary": 500,
        }
        original = copy.deepcopy(input_dict)
        _ = ipython_console(input_dict)
        self.assertEqual(input_dict, original)

    def test_all_test_cases_against_independent_oracle(self):
        """Cross-check all 24 inputs against the independent oracle."""
        for tc in TEST_CASES:
            with self.subTest(tc_id=tc["id"], desc=tc["description"]):
                args_copy = copy.deepcopy(tc["args"])
                kwargs_copy = copy.deepcopy(tc["kwargs"])

                oracle_result = independent_oracle(*tc["args"], **tc["kwargs"])
                actual_result = ipython_console(*tc["args"], **tc["kwargs"])

                self.assertEqual(
                    actual_result,
                    tc["expected"],
                    f"[{tc['id']}] Mismatch with explicit expected value",
                )
                self.assertEqual(
                    actual_result,
                    oracle_result,
                    f"[{tc['id']}] Mismatch with independent oracle",
                )
                self.assertEqual(
                    tc["args"],
                    args_copy,
                    f"[{tc['id']}] Positional args were mutated",
                )
                self.assertEqual(
                    tc["kwargs"],
                    kwargs_copy,
                    f"[{tc['id']}] Keyword args were mutated",
                )


if __name__ == "__main__":
    unittest.main()
