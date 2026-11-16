import io
import unittest
from unittest.mock import patch

from weather import (
    CYAN,
    RED,
    RESET,
    REVERSE,
    _select_weather_display_params,
    change_color,
)


class TestChangeColorBoundaries(unittest.TestCase):
    """Focused boundary and contract tests for change_color in weather.py.

    Preconditions established by how-to-use-github/weather.py:
    - Line 11: RED = "\\033[1;31m"
    - Line 13: CYAN = "\\033[1;36m"
    - Line 17: REVERSE = "\\033[;7m"
    - Line 18: RESET = "\\033[0m"
    - Line 21-22: def change_color(color): print(color, end="")
    - Line 31: THUNDERSTORM = range(200, 300)
    - Line 32: DRIZZLE = range(300, 400)
    - Line 133: change_color(REVERSE)
    - Line 135: change_color(RESET)
    - Line 137: change_color(color)
    - Line 143: change_color(RESET)
    - Line 157: display_params = ("💥", RED)
    - Line 159: display_params = ("💧", CYAN)
    """

    def _call_change_color(self, color_input):
        """Invoke change_color with stdout captured (mocked I/O)."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            ret = change_color(color_input)
            output = mock_stdout.getvalue()
        return ret, output

    def test_smallest_valid_input(self):
        """Test smallest valid input: empty string of length 0.

        Precondition: weather.py line 21-22 accepts string, prints end="".
        Smallest valid string domain boundary is the empty string "".
        """
        input_value = ""
        expected_output = ""
        expected_return = None

        ret, actual_output = self._call_change_color(input_value)

        self.assertEqual(
            actual_output,
            expected_output,
            f"Input={input_value!r}, Expected={expected_output!r}, "
            f"Actual={actual_output!r}",
        )
        self.assertIs(ret, expected_return)
        self.assertFalse(actual_output.endswith("\n"))

    def test_ordinary_input_anchor_red(self):
        """Test ordinary input from anchor 1: RED ("\\033[1;31m").

        Preconditions:
        - weather.py line 11: RED = "\\033[1;31m"
        - weather.py line 157: display_params = ("💥", RED)
        - weather.py line 137: change_color(color)
        """
        input_value = "\033[1;31m"
        expected_output = "\033[1;31m"
        expected_return = None

        self.assertEqual(input_value, RED)
        ret, actual_output = self._call_change_color(input_value)

        self.assertEqual(
            actual_output,
            expected_output,
            f"Input={input_value!r}, Expected={expected_output!r}, "
            f"Actual={actual_output!r}",
        )
        self.assertIs(ret, expected_return)
        self.assertFalse(actual_output.endswith("\n"))

    def test_ordinary_input_anchor_cyan(self):
        """Test ordinary input from anchor 2: CYAN ("\\033[1;36m").

        Preconditions:
        - weather.py line 13: CYAN = "\\033[1;36m"
        - weather.py line 159: display_params = ("💧", CYAN)
        - weather.py line 137: change_color(color)
        """
        input_value = "\033[1;36m"
        expected_output = "\033[1;36m"
        expected_return = None

        self.assertEqual(input_value, CYAN)
        ret, actual_output = self._call_change_color(input_value)

        self.assertEqual(
            actual_output,
            expected_output,
            f"Input={input_value!r}, Expected={expected_output!r}, "
            f"Actual={actual_output!r}",
        )
        self.assertIs(ret, expected_return)
        self.assertFalse(actual_output.endswith("\n"))

    def test_documented_boundary_reset(self):
        """Test documented reset boundary code: RESET ("\\033[0m").

        Preconditions:
        - weather.py line 18: RESET = "\\033[0m"
        - weather.py lines 135, 143: change_color(RESET)
        - weather.py line 171: display_params = ("🌈", RESET)
        """
        input_value = "\033[0m"
        expected_output = "\033[0m"
        expected_return = None

        self.assertEqual(input_value, RESET)
        ret, actual_output = self._call_change_color(input_value)

        self.assertEqual(
            actual_output,
            expected_output,
            f"Input={input_value!r}, Expected={expected_output!r}, "
            f"Actual={actual_output!r}",
        )
        self.assertIs(ret, expected_return)
        self.assertFalse(actual_output.endswith("\n"))

    def test_documented_boundary_reverse(self):
        """Test documented reverse-style boundary code: REVERSE ("\\033[;7m").

        Preconditions:
        - weather.py line 17: REVERSE = "\\033[;7m"
        - weather.py line 133: change_color(REVERSE)
        """
        input_value = "\033[;7m"
        expected_output = "\033[;7m"
        expected_return = None

        self.assertEqual(input_value, REVERSE)
        ret, actual_output = self._call_change_color(input_value)

        self.assertEqual(
            actual_output,
            expected_output,
            f"Input={input_value!r}, Expected={expected_output!r}, "
            f"Actual={actual_output!r}",
        )
        self.assertIs(ret, expected_return)
        self.assertFalse(actual_output.endswith("\n"))

    def test_weather_condition_boundary_both_sides(self):
        """Test both sides of documented weather condition boundary.

        Boundary at weather_id = 299 vs 300:
        Side A (upper bound of THUNDERSTORM, range(200, 300)):
        - weather.py line 31: THUNDERSTORM = range(200, 300)
        - weather.py line 156-157: display_params = ("💥", RED)
        - weather_id = 299 produces RED ("\\033[1;31m")

        Side B (lower bound of DRIZZLE, range(300, 400)):
        - weather.py line 32: DRIZZLE = range(300, 400)
        - weather.py line 158-159: display_params = ("💧", CYAN)
        - weather_id = 300 produces CYAN ("\\033[1;36m")
        """
        # Side A: Upper boundary of THUNDERSTORM (299)
        symbol_a, color_a = _select_weather_display_params(299)
        self.assertEqual(symbol_a, "💥")
        self.assertEqual(color_a, "\033[1;31m")
        ret_a, output_a = self._call_change_color(color_a)
        self.assertEqual(output_a, "\033[1;31m")
        self.assertIsNone(ret_a)
        self.assertFalse(output_a.endswith("\n"))

        # Side B: Lower boundary of DRIZZLE (300)
        symbol_b, color_b = _select_weather_display_params(300)
        self.assertEqual(symbol_b, "💧")
        self.assertEqual(color_b, "\033[1;36m")
        ret_b, output_b = self._call_change_color(color_b)
        self.assertEqual(output_b, "\033[1;36m")
        self.assertIsNone(ret_b)
        self.assertFalse(output_b.endswith("\n"))

    def test_absence_of_added_newline(self):
        """Verify absence of added newline across multiple valid inputs.

        Precondition: weather.py line 22 specifies end="" in print().
        """
        sample_inputs = [
            "",
            "\033[1;31m",
            "\033[1;36m",
            "\033[0m",
            "\033[;7m",
        ]
        for input_val in sample_inputs:
            _, output = self._call_change_color(input_val)
            self.assertEqual(
                output,
                input_val,
                f"Mismatch for input {input_val!r}",
            )
            self.assertFalse(
                output.endswith("\n"),
                f"Output for {input_val!r} unexpectedly ended with newline",
            )

    def test_return_behavior_is_none(self):
        """Verify change_color always returns None.

        Precondition: weather.py line 21-22 has no return statement.
        """
        sample_inputs = ["", "\033[1;31m", "\033[1;36m"]
        for input_val in sample_inputs:
            ret, _ = self._call_change_color(input_val)
            self.assertIsNone(
                ret,
                f"Expected None return for {input_val!r}, got {ret!r}",
            )

    def test_input_is_not_mutated(self):
        """Verify change_color does not mutate the input argument.

        Precondition: Strings are immutable and change_color only reads input.
        """
        input_string = "\033[1;31m"
        expected_value = "\033[1;31m"
        self._call_change_color(input_string)
        self.assertEqual(input_string, expected_value)


if __name__ == "__main__":
    unittest.main()
