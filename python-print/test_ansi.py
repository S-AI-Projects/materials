#!/usr/bin/env python3
"""Invariant and property tests for esc function in python-print/ansi.py.

Task ID: R32-T054
Target: python-print/ansi.py
Target function: esc

Preconditions established by source:
    Line 1: def esc(*codes): accepts arbitrary positional arguments.
    Line 2: return f"\\033[{';'.join(str(code) for code in codes)}m" defines CSI framing,
            semicolon delimiter, and 'm' suffix.
    Line 5: print(esc(31, 1, 4) + "really" + esc(0) + " important") demonstrates
            multi-code input (31, 1, 4) -> '\\033[31;1;4m' and reset (0,) -> '\\033[0m'.
"""

import io
import random
import unittest
from unittest.mock import patch

# Mock sys.stdout during import to intercept the module-level demonstration print on line 5
with patch("sys.stdout", new_callable=io.StringIO):
    from ansi import esc

# Fixed random seed for reproducible property-based testing
PROPERTY_SEED = 42


def independent_oracle(*codes):
    """Independently calculate expected ANSI escape sequence.

    Derives expected string without calling esc(), using explicit ASCII ESC
    character chr(27) ('\\033'), CSI bracket '[', string conversions of
    each code, semicolon delimiters, and SGR terminator 'm'.
    """
    esc_byte = chr(27)  # '\033' / '\x1b'
    prefix = esc_byte + "["
    suffix = "m"
    if not codes:
        return prefix + suffix
    payload = ";".join(str(c) for c in codes)
    return prefix + payload + suffix


def verify_esc_invariant(codes, result):
    """Formally verify contract invariants for esc(*codes) -> result.

    Invariants checked:
    1. Output Type: result must be a str instance.
    2. Framing: result starts with '\\033[' and ends with 'm'.
    3. Payload Semicolon Count: exactly max(0, len(codes) - 1) semicolons.
    4. Exact Length: 3 (prefix '\\033[' + suffix 'm') + sum(len(str(c))) + max(0, len(codes) - 1).
    5. Reversibility / Parse-Back Roundtrip:
       - If codes is empty: inner payload is empty string ''.
       - If codes is non-empty: splitting inner payload on ';' recovers
         exact tuple of string representations tuple(str(c) for c in codes).
    6. Ordering Preservation: relative order of input codes is preserved exactly.
    """
    # 1. Output Type
    assert isinstance(result, str), (
        f"Expected str, got {type(result).__name__}"
    )

    # 2. Framing
    assert result.startswith("\033["), (
        f"Result {result!r} does not start with \\033["
    )
    assert result.endswith("m"), f"Result {result!r} does not end with 'm'"

    payload = result[2:-1]
    n = len(codes)

    if n == 0:
        # Smallest valid input boundary
        assert payload == "", (
            f"Expected empty payload for 0 codes, got {payload!r}"
        )
        assert result.count(";") == 0, (
            f"Expected 0 semicolons for empty codes, got {result.count(';')}"
        )
        assert len(result) == 3, (
            f"Expected length 3 for esc(), got {len(result)}"
        )
    else:
        # 3. Payload Semicolon Count
        expected_semicolons = n - 1
        assert result.count(";") == expected_semicolons, (
            f"Expected {expected_semicolons} semicolons, got {result.count(';')}"
        )

        # 4. Exact Length
        expected_len = 3 + sum(len(str(c)) for c in codes) + (n - 1)
        assert len(result) == expected_len, (
            f"Expected length {expected_len}, got {len(result)}"
        )

        # 5. Reversibility / Parse-Back Roundtrip
        parsed_tokens = tuple(payload.split(";"))
        expected_tokens = tuple(str(c) for c in codes)
        assert parsed_tokens == expected_tokens, (
            f"Roundtrip token mismatch: expected {expected_tokens}, got {parsed_tokens}"
        )

        # 6. Ordering Preservation
        for i in range(len(codes)):
            tok_i = str(codes[i])
            assert parsed_tokens[i] == tok_i, (
                f"Token ordering violation at index {i}: expected {tok_i!r}, got {parsed_tokens[i]!r}"
            )


def generate_bounded_cases(seed=PROPERTY_SEED, count=120):
    """Deterministically generate bounded valid ANSI code sequences."""
    rng = random.Random(seed)

    styles = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 21, 22, 24, 27, 28, 29]
    fg_colors = list(range(30, 38)) + [39] + list(range(90, 98))
    bg_colors = list(range(40, 48)) + [49] + list(range(100, 108))
    extended = [38, 48, 5, 2] + list(range(0, 256, 17))
    code_pool = sorted(set(styles + fg_colors + bg_colors + extended))

    cases = []
    for i in range(count):
        # Generate varied sequence lengths from 0 to 8
        if i % 15 == 0:
            length = 0
        elif i % 15 in (1, 2, 3):
            length = 1
        elif i % 15 in (4, 5, 6):
            length = 2
        elif i % 15 in (7, 8, 9):
            length = 3
        elif i % 15 in (10, 11):
            length = 4
        elif i % 15 == 12:
            length = 5
        elif i % 15 == 13:
            length = 6
        else:
            length = 8

        case_tuple = tuple(rng.choice(code_pool) for _ in range(length))
        cases.append(case_tuple)

    return cases


class TestEscInvariant(unittest.TestCase):
    """Test suite verifying invariant properties of esc (*codes)."""

    def test_preconditions_and_literal_fixtures(self):
        """Test smallest valid input and ordinary inputs with literal expectations.

        Preconditions cited from source:
            Line 1: def esc(*codes): establishes positional parameter support.
            Line 2: return f"\\033[{';'.join(str(code) for code in codes)}m" establishes format.
            Line 5: print(esc(31, 1, 4) + "really" + esc(0) + " important") establishes
                    ordinary multi-argument (31, 1, 4) and reset (0,).
        """
        # Smallest valid input: zero arguments ()
        smallest_input = ()
        expected_smallest = "\033[m"
        actual_smallest = esc(*smallest_input)
        self.assertEqual(actual_smallest, expected_smallest)
        verify_esc_invariant(smallest_input, actual_smallest)

        # Ordinary input anchor 1: (31, 1, 4) from line 5
        ordinary_input_1 = (31, 1, 4)
        expected_ordinary_1 = "\033[31;1;4m"
        actual_ordinary_1 = esc(*ordinary_input_1)
        self.assertEqual(actual_ordinary_1, expected_ordinary_1)
        verify_esc_invariant(ordinary_input_1, actual_ordinary_1)

        # Ordinary input anchor 2: (0,) from line 5
        ordinary_input_2 = (0,)
        expected_ordinary_2 = "\033[0m"
        actual_ordinary_2 = esc(*ordinary_input_2)
        self.assertEqual(actual_ordinary_2, expected_ordinary_2)
        verify_esc_invariant(ordinary_input_2, actual_ordinary_2)

    def test_output_type_and_framing(self):
        """Verify return type is str and starts with '\\033[' and ends with 'm'."""
        test_inputs = [
            (),
            (0,),
            (1,),
            (31, 1, 4),
            (38, 5, 128),
            (38, 2, 255, 128, 64),
        ]
        for inp in test_inputs:
            with self.subTest(inp=inp):
                res = esc(*inp)
                self.assertIsInstance(res, str)
                self.assertTrue(res.startswith("\033["))
                self.assertTrue(res.endswith("m"))

    def test_ordering_behavior(self):
        """Verify sequential order of arguments is strictly preserved."""
        forward = (10, 20, 30)
        reverse = (30, 20, 10)

        res_forward = esc(*forward)
        res_reverse = esc(*reverse)

        self.assertEqual(res_forward, "\033[10;20;30m")
        self.assertEqual(res_reverse, "\033[30;20;10m")
        self.assertNotEqual(res_forward, res_reverse)

    def test_input_non_mutation(self):
        """Verify caller input collections and arguments are not mutated."""
        input_list = [31, 1, 4]
        input_copy = list(input_list)

        res = esc(*input_list)
        self.assertEqual(input_list, input_copy)
        self.assertEqual(res, "\033[31;1;4m")

    def test_idempotence_and_determinism(self):
        """Verify repeated invocations under controlled state yield identical outputs."""
        sample_inputs = [(), (0,), (31, 1, 4), (38, 5, 200)]
        for inp in sample_inputs:
            with self.subTest(inp=inp):
                first = esc(*inp)
                second = esc(*inp)
                third = esc(*copy_of(inp))
                self.assertEqual(first, second)
                self.assertEqual(second, third)

    def test_homomorphic_substring_composition(self):
        """Verify payload concatenation holds for non-empty code sequences."""
        a = (31, 1)
        b = (4, 42)
        combined = a + b

        payload_a = esc(*a)[2:-1]
        payload_b = esc(*b)[2:-1]
        payload_combined = esc(*combined)[2:-1]

        self.assertEqual(payload_combined, f"{payload_a};{payload_b}")

    def test_curated_domain_boundaries(self):
        """Verify curated standard ANSI styling and color boundaries."""
        curated_cases = [
            ((), "\033[m"),
            ((0,), "\033[0m"),
            ((1,), "\033[1m"),
            ((4,), "\033[4m"),
            ((7,), "\033[7m"),
            ((31,), "\033[31m"),
            ((32,), "\033[32m"),
            ((41,), "\033[41m"),
            ((92,), "\033[92m"),
            ((38, 5, 196), "\033[38;5;196m"),
            ((48, 2, 255, 128, 0), "\033[48;2;255;128;0m"),
            (("31", "1", 4), "\033[31;1;4m"),
        ]
        for inp, expected in curated_cases:
            with self.subTest(inp=inp):
                actual = esc(*inp)
                self.assertEqual(actual, expected)
                verify_esc_invariant(inp, actual)

    def test_property_generated_bounded_cases(self):
        """Verify invariants across 120 deterministic generated bounded cases."""
        cases = generate_bounded_cases(seed=PROPERTY_SEED, count=120)
        self.assertEqual(len(cases), 120)

        for idx, c in enumerate(cases):
            with self.subTest(case_index=idx, codes=c):
                expected = independent_oracle(*c)
                actual = esc(*c)
                self.assertEqual(
                    actual,
                    expected,
                    f"Mismatch at case {idx} with codes {c!r}: expected {expected!r}, got {actual!r}",
                )
                verify_esc_invariant(c, actual)


def copy_of(inp):
    """Create fresh equivalent copy of input tuple."""
    return tuple(list(inp))


if __name__ == "__main__":
    unittest.main()
