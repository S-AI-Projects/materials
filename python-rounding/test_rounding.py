"""Regression tests for truncation toward zero.

In particular, negative inputs must not be rounded down toward negative
infinity. The return value must remain a float.
"""

import pytest

from rounding import truncate


@pytest.mark.parametrize(
    ("number", "decimals", "expected"),
    [
        (-0.9, 0, 0.0),
        (-12.349, 2, -12.34),
        (12.349, 2, 12.34),
        (0, 0, 0.0),
    ],
)
def test_truncate_returns_float_and_truncates_toward_zero(
    number, decimals, expected
):
    actual = truncate(number, decimals)

    assert actual == expected
    assert type(actual) is float
