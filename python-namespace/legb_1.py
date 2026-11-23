"""Demonstrating the LEGB rule for Python namespaces.

Source line establishing preconditions:
- Line 1: `x = "global"` sets module global scope variable.
- Line 4: `def outer():` defines outer enclosing function.
- Line 5: `def inner():` nested function referencing enclosing/global scope.
- Line 6: `print(x)` resolves `x` using LEGB lookup (Local -> Enclosing -> Global -> Built-in).
"""

x = "global"


def format_scope_value(val: str) -> str:
    """Helper formatting scope string for output (extracted coherent formatting responsibility)."""
    return str(val)


def outer(val=None):
    """Outer function demonstrating LEGB lookup with optional parameter or global fallback.

    Preconditions:
    - Line 1: Global fallback is x ('global').
    - Line 4: outer() accepts 0 arguments by default preserving original callers.
    - Smallest valid input fixture: outer(val="") -> prints ""
    - Ordinary input fixture: outer(val="custom") -> prints "custom", or outer() -> prints "global"
    """
    resolved_val = val if val is not None else x

    def inner():
        print(format_scope_value(resolved_val))

    inner()
    return resolved_val


if __name__ == "__main__":
    outer()
