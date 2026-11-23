"""
Python formatted output examples and reference specifications.

Preconditions:
- Line 1: `print(f"{257:b}")` establishes binary string formatting (`:b`) for integers.
  Representative result:
    Input: 257 (ordinary input from Line 1)
    Formatting: `f"{257:b}"` converts the integer 257 (2^8 + 2^0) into its base-2 representation without prefix.
    Expected output: "100000001"
  Smallest valid input: 0 -> "0"
- Line 4: `print(f"{42:c}")` establishes Unicode character formatting (`:c`).
  Ordinary input: 42 -> "*"
  Smallest valid input: 0 -> "\x00"
"""


def format_binary(val: int) -> str:
    """Format an integer as a base-2 binary string without prefix.

    Precondition: Line 1 (`f"{257:b}"`).
    Requires integer val >= 0 for standard unsigned bit representation.
    """
    if not isinstance(val, int):
        raise TypeError(f"format_binary expects int, got {type(val).__name__}")
    return f"{val:b}"


def format_char(val: int) -> str:
    """Format an integer code point as a character string.

    Precondition: Line 4 (`f"{42:c}"`).
    """
    if not isinstance(val, int):
        raise TypeError(f"format_char expects int, got {type(val).__name__}")
    return f"{val:c}"


def main():
    print(f"{257:b}")
    print("{:b}".format(257))

    print(f"{42:c}")
    print("{:c}".format(42))

    print(f"{3.14159:g}")
    print(f"{-123456789.8765:g}")
    print("{:g}".format(3.14159))
    print("{:g}".format(-123456789.8765))

    print(f"{-123456789.8765:G}")
    print("{:G}".format(-123456789.8765))

    infinite = float("inf")
    not_a_number = infinite * 0
    print(f"{infinite:g}")
    print(f"{not_a_number:g}")
    print(f"{infinite:G}")
    print(f"{not_a_number:G}")
    print("{:g}".format(infinite))
    print("{:g}".format(not_a_number))
    print("{:G}".format(infinite))
    print("{:G}".format(not_a_number))

    print(f"{'Hi':8s}")
    print(f"{123:8d}")
    print("{0:8s}".format("Hi"))
    print("{0:8d}".format(123))

    print("{0:2s}".format("Pythonista"))

    print(f"{'Hi':<8s}")
    print(f"{123:<8d}")
    print("{0:<8s}".format("Hi"))
    print("{0:<8d}".format(123))

    print(f"{'Hi':>8s}")
    print(f"{123:>8d}")
    print("{0:>8s}".format("Hi"))
    print("{0:>8d}".format(123))

    print(f"{'Hi':^8s}")
    print(f"{123:^8d}")
    print("{0:^8s}".format("Hi"))
    print("{0:^8d}".format(123))

    print(f"{123:+8d}")
    print(f"{-123:+8d}")
    print("{0:+8d}".format(123))
    print("{0:+8d}".format(-123))

    print(f"{123:=+8d}")
    print(f"{-123:=+8d}")
    print("{0:=+8d}".format(123))
    print("{0:=+8d}".format(-123))

    print(f"{'Hi':->8s}")
    print(f"{123:#<8d}")
    print(f"{'Hi':*^8s}")
    print("{0:->8s}".format("Hi"))
    print("{0:#<8d}".format(123))
    print("{0:*^8s}".format("Hi"))

    print(f"{123:+6d}")
    print(f"{-123:+6d}")
    print("{0:+6d}".format(123))
    print("{0:+6d}".format(-123))

    print(f"{123:-6d}")
    print(f"{-123:-6d}")
    print("{0:-6d}".format(123))
    print("{0:-6d}".format(-123))

    print(f"{123:*> 6d}")
    print(f"{-123:*> 6d}")
    print("{0:*> 6d}".format(123))
    print("{0:*> 6d}".format(-123))

    value = 16
    print(f"{value:b}, {value:#b}")
    print(f"{value:o}, {value:#o}")
    print(f"{value:x}, {value:#x}")
    print("{0:b}, {0:#b}".format(value))
    print("{0:o}, {0:#o}".format(value))
    print("{0:x}, {0:#x}".format(value))

    print(f"{123:.0f}, {123:#.0f}")
    print(f"{123:.0e}, {123:#.0e}")
    print("{0:.0f}, {0:#.0f}".format(123))
    print("{0:.0e}, {0:#.0e}".format(123))

    print(f"{123:05d}")
    print(f"{12.3:08.1f}")
    print("{0:05d}".format(123))
    print("{0:08.1f}".format(12.3))

    print(f"{'Hi':>06s}")
    print("{0:>06s}".format("Hi"))

    print(f"{123:*>05d}")
    print("{0:*>05d}".format(123))

    print(f"{1234567:,d}")
    print(f"{1234567:_d}")
    print(f"{1234567.89:,.2f}")
    print(f"{1234567.89:_.2f}")
    print("{0:,d}".format(1234567))
    print("{0:_d}".format(1234567))
    print("{0:,.2f}".format(1234567.89))
    print("{0:_.2f}".format(1234567.89))

    print(f"{1.23456789:.8_f}")
    print("{0:.8_f}".format(1.23456789))

    print(f"{0b111010100001:_b}")
    print(f"{0b111010100001:#_b}")
    print(f"{0xAE123FCC8AB2:_x}")
    print(f"{0xAE123FCC8AB2:#_x}")
    print("{0:_b}".format(0b111010100001))
    print("{0:#_b}".format(0b111010100001))
    print("{0:_x}".format(0xAE123FCC8AB2))
    print("{0:#_x}".format(0xAE123FCC8AB2))

    print(f"{1234.5678:8.2f}")
    print(f"{1.23:8.4f}")
    print(f"{1234.5678:8.2e}")
    print(f"{1.23:8.4e}")
    print("{0:8.2f}".format(1234.5678))
    print("{0:8.4f}".format(1.23))
    print("{0:8.2e}".format(1234.5678))
    print("{0:8.4e}".format(1.23))

    print(f"{'Pythonista':.6s}")
    print("{0:.6s}".format("Pythonista"))

    width = 10
    precision = 2
    print(f"{123.4567:{width}.{precision}f}")
    print("{2:{0}.{1}f}".format(width, precision, 123.4567))
    print(
        "{number:{width}.{precision}f}".format(
            width=width, precision=precision, number=123.4567
        )
    )


if __name__ == "__main__":
    main()
