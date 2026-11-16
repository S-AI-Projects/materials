# How to Flatten a List of Lists in Python

This folder provides the code examples for the Real Python tutorial [How to Flatten a List of Lists in Python](https://realpython.com/python-flatten-list/).

## Executable Worked Example: `flatten_extend`

The function `flatten_extend(matrix)` in `flatten.py` flattens a two-dimensional matrix or iterable of iterables into a one-dimensional list by iterating through each row and extending an accumulator list.

### Preconditions and Fixture Anchors
- Line 7 (`flat_list = []`): Initializes the empty mutable list accumulator for `flatten_extend`.
- Line 14 (`flat_list = []`): Sibling accumulator for `flatten_concatenation`.

### Decisive State Transition
The decisive state transition occurs during `flat_list.extend(row)`:
- `extend()` unpacks the elements of `row` and appends them in-place directly into the existing list buffer (`id(flat_list)` remains identical throughout).
- This avoids intermediate list object allocations and copies that occur with concatenation (`+` or `+=`), making `extend()` an efficient, idiomatic flattening approach.

### Step-by-Step Trace (Ordinary Input: `[[1, 2, 3], [4, 5, 6], [7, 8, 9]]`)
1. **Initial state:** `flat_list = []` (length 0)
2. **Iteration 1 (`row = [1, 2, 3]`):**
   - In-place buffer extension: `flat_list.extend([1, 2, 3])`
   - Intermediate state: `flat_list = [1, 2, 3]` (length 3)
3. **Iteration 2 (`row = [4, 5, 6]`):**
   - In-place buffer extension: `flat_list.extend([4, 5, 6])`
   - Intermediate state: `flat_list = [1, 2, 3, 4, 5, 6]` (length 6)
4. **Iteration 3 (`row = [7, 8, 9]`):**
   - In-place buffer extension: `flat_list.extend([7, 8, 9])`
   - Intermediate state: `flat_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]` (length 9)
5. **Final Result:** `[1, 2, 3, 4, 5, 6, 7, 8, 9]`

### Running the Worked Example
Run the example directly from the command line:

```bash
python3 python-flatten-list/flatten.py
```
