from ai_agent_project import double


def test_double_zero():
    """Test the smallest valid integer input.
    Source line establishing precondition: the function returns `value * 2` without side effects.
    """
    assert double(0) == 0


def test_double_seven():
    """Test an ordinary positive integer.
    Source line establishing precondition: pure multiplication ensures deterministic output.
    """
    assert double(7) == 14


def test_double_repeatability():
    """Call the same input twice, with another call in between, and verify identical results.
    The source implementation has no mutable state, so repeated calls must be equal.
    """
    first = double(3)
    _ = double(5)  # intermediate call to ensure no hidden state
    second = double(3)
    assert first == second == 6
