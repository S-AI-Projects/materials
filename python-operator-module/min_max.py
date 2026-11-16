prices = [100, 45, 345, 639]


def get_min_max(values=prices, *args):
    """Compute the minimum and maximum values from an iterable or arguments.

    Preconditions established by source:
        Line 1: prices = [100, 45, 345, 639] - Default price list anchor.

    Representative result:
        >>> get_min_max([100, 45, 345, 639])
        (45, 639)

    Args:
        values: An iterable of comparable elements, or the first positional argument.
            Defaults to `prices` from line 1.
        *args: Additional positional arguments if values was passed as individual elements.

    Returns:
        tuple: A 2-tuple (min_value, max_value) containing the minimum and maximum elements.
    """
    if args:
        items = (values, *args)
    elif not hasattr(values, "__iter__"):
        items = (values,)
    else:
        items = values
    return min(items), max(items)


min_max = get_min_max
python_operator_module = get_min_max

min_price, max_price = get_min_max(prices)
print(min_price)
print(max_price)
