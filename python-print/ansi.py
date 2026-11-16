def esc(*codes):
    """Format ANSI escape sequence for terminal styling and color control.

    Invariant Specification:
        For any tuple of codes C = (c_1, c_2, ..., c_n) where each c_i is
        convertible to string via str(c_i):
        1. Output Type: esc(*C) returns an instance of str.
        2. Framing: The return string strictly begins with CSI prefix '\\033['
           and ends with SGR terminator 'm'.
        3. Inner Payload:
           - If len(C) == 0: inner payload is empty string '' (return '\\033[m').
           - If len(C) > 0: inner payload equals ';'.join(str(c) for c in C),
             containing exactly len(C) - 1 semicolon delimiters.
        4. Reversibility & Roundtrip:
           Splitting payload by ';' recovers exact string representations:
           tuple(payload.split(';')) == tuple(str(c) for c in C) for len(C) > 0.
        5. Ordering Preservation: The relative order of arguments is preserved
           without permutation: str(c_i) precedes str(c_j) for all i < j.
        6. Determinism & Idempotence: Repeated invocations with identical inputs
           yield identical results under controlled external state.
        7. Non-Mutation: Input arguments and containers are never mutated.

    Preconditions established by source:
        Line 1: def esc(*codes): - accepts variable positional arguments.
        Line 2: return f"\\033[{';'.join(str(code) for code in codes)}m" - defines
                CSI framing, semicolon delimiter, and 'm' suffix.
        Line 5: print(esc(31, 1, 4) + "really" + esc(0) + " important") - demonstrates
                multi-code input (31, 1, 4) -> '\\033[31;1;4m' and reset (0,) -> '\\033[0m'.

    Domain Boundaries & Fixtures:
        - Smallest valid input: () (0 arguments) -> '\\033[m'
        - Ordinary input anchor 1: (31, 1, 4) -> '\\033[31;1;4m'
        - Ordinary input anchor 2: (0,) -> '\\033[0m'

    Args:
        *codes: Positional code parameters (integers or str-convertible objects)
            representing ANSI escape sequence parameters.

    Returns:
        str: ANSI escape sequence formatted as f"\\033[{';'.join(codes)}m".
    """
    return f"\033[{';'.join(str(code) for code in codes)}m"


print(esc(31, 1, 4) + "really" + esc(0) + " important")
