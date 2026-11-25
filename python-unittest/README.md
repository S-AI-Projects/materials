# Python's unittest: Writing Unit Tests for Your Code

This folder provides the code examples for the Real Python tutorial [Python's unittest: Writing Unit Tests for Your Code](https://realpython.com/python-unittest/).

## Documented Failure and Absent-Result Paths

This test suite explicitly exercises the failure and absent-result branches of the `unittest` framework:
- **Empty-Result Path**: An empty `TestSuite` executes 0 tests and reports success without error.
- **Assertion Failure Path**: `assertEqual`, `assertTrue`, and `assertFalse` raise `AssertionError` when conditions fail.
- **Missing Exception Path**: `assertRaises` raises `AssertionError` when the enclosed callable fails to raise the expected exception.
- **State Recovery**: Caller-owned state remains valid following any failure, allowing subsequent assertions to succeed cleanly.
