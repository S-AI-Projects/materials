from functools import reduce
from itertools import chain
from operator import add, concat, iconcat


def flatten_extend(matrix):
    """Flatten a two-dimensional matrix or iterable of iterables into a 1D list.

    Iterates through each row of the input matrix and extends an accumulator
    list in-place using `list.extend()`. The decisive state transition occurs
    when `flat_list.extend(row)` unpacks the elements of `row` and appends
    them directly into the existing list buffer in-place, avoiding the repeated
    memory reallocations required by concatenation (+ or +=).

    Args:
        matrix (Iterable[Iterable[Any]]): A 2D sequence or iterable of
            iterables to be flattened.

    Returns:
        list: A new flat list containing all elements from each row in order.

    Preconditions:
        - Source anchor (line 7): `flat_list = []` initializes the mutable
          list accumulator.
        - Sibling anchor (line 14): `flat_list = []` initializes the mutable
          list accumulator for `flatten_concatenation`.
        - Each item `row` in `matrix` must be an iterable whose elements can
          be unpacked by `list.extend()`.

    Worked Examples:
        Smallest valid input (empty matrix):
        >>> from flatten import flatten_extend
        >>> flatten_extend([])
        []

        Smallest valid input with empty row:
        >>> flatten_extend([[]])
        []

        Ordinary input (3x3 matrix):
        >>> matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        >>> flatten_extend(matrix)
        [1, 2, 3, 4, 5, 6, 7, 8, 9]

    Trace of State Transitions (Ordinary Input: [[1, 2, 3], [4, 5, 6], [7, 8, 9]]):
        - Precondition anchor (line 7): flat_list = [] (id preserved across steps)
        - Initial state: flat_list = [] (length 0)
        - Step 1: row = [1, 2, 3]
            Decisive transition: flat_list.extend([1, 2, 3]) appends elements
            in-place to the accumulator buffer.
            State: flat_list = [1, 2, 3] (length 3)
        - Step 2: row = [4, 5, 6]
            Decisive transition: flat_list.extend([4, 5, 6]) appends elements
            in-place to the accumulator buffer.
            State: flat_list = [1, 2, 3, 4, 5, 6] (length 6)
        - Step 3: row = [7, 8, 9]
            Decisive transition: flat_list.extend([7, 8, 9]) appends elements
            in-place to the accumulator buffer.
            State: flat_list = [1, 2, 3, 4, 5, 6, 7, 8, 9] (length 9)
        - Return value: [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    flat_list = []
    for row in matrix:
        flat_list.extend(row)
    return flat_list


def flatten_concatenation(matrix):
    flat_list = []
    for row in matrix:
        flat_list += row
    return flat_list


def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]


def flatten_chain(matrix):
    return list(chain.from_iterable(matrix))


def flatten_reduce_lambda(matrix):
    return list(reduce(lambda x, y: x + y, matrix, []))


def flatten_reduce_add(matrix):
    return reduce(add, matrix, [])


def flatten_reduce_concat(matrix):
    return reduce(concat, matrix, [])


def flatten_reduce_iconcat(matrix):
    return reduce(iconcat, matrix, [])


def flatten_sum(matrix):
    return sum(matrix, [])


def run_worked_example():
    """Execute and display the worked example for flatten_extend."""
    print("=" * 60)
    print("Worked Example: flatten_extend (python-flatten-list/flatten.py)")
    print("=" * 60)
    print()
    print("1. Smallest Valid Input:")
    print("   Input matrix: []")
    print("   Precondition (line 7): flat_list = []")
    print("   Initial state: flat_list = []")
    print("   Loop iterations: 0 (matrix is empty)")
    result_empty = flatten_extend([])
    print(f"   Final result: {result_empty}")
    print()
    print("2. Smallest Valid Input (Single Empty Row):")
    print("   Input matrix: [[]]")
    print("   Precondition (line 7): flat_list = []")
    print("   Initial state: flat_list = []")
    print("   Iteration 1: row = [] -> flat_list.extend([]) -> flat_list = []")
    result_empty_row = flatten_extend([[]])
    print(f"   Final result: {result_empty_row}")
    print()
    print("3. Ordinary Input (3x3 Matrix):")
    ordinary_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    print(f"   Input matrix: {ordinary_matrix}")
    print("   Precondition (line 7): flat_list = []")
    print("   Initial state: flat_list = [] (len=0)")

    # Tracing the decisive state transitions
    accumulator = []
    for step, row in enumerate(ordinary_matrix, 1):
        print(f"   Iteration {step}: row = {row}")
        print(
            f"     Decisive transition: flat_list.extend({row}) appends elements in-place to accumulator buffer"
        )
        accumulator.extend(row)
        print(
            f"     Intermediate state: flat_list = {accumulator} (len={len(accumulator)})"
        )

    final_result = flatten_extend(ordinary_matrix)
    print(f"   Final result: {final_result}")
    print("=" * 60)
    return final_result


if __name__ == "__main__":
    run_worked_example()
