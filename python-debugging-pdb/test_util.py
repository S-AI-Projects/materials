"""Independent reference comparison tests for get_path."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import get_path

def oracle(filename):
    return os.path.dirname(filename)

INPUTS = [
    "",
    "file.py",
    "/",
    "/file.py",
    "/dir/file.py",
    "/a/b/c/file.py",
    "dir/file.py",
    "dir/",
    "/dir/",
    "a",
    "a/b",
    "a/b/c",
    "./file.py",
    "../file.py",
    "../../file.py",
    "./dir/file.py",
    "../dir/file.py",
    "dir/subdir/file.txt",
    "/usr/local/bin/python",
    "C:/Windows/System32/cmd.exe",
    "relative/path/file.txt",
    "file",
    "/only_root_file",
    "deeply/nested/path/to/some/file.py",
    "no_extension_file",
]

class TestGetPathOracleComparison(unittest.TestCase):
    def test_smallest_valid_input_empty_string(self):
        self.assertEqual(get_path(""), "")
        self.assertEqual(get_path(""), oracle(""))

    def test_ordinary_valid_input_dir_file(self):
        self.assertEqual(get_path("/dir/file.py"), "/dir")
        self.assertEqual(get_path("/dir/file.py"), oracle("/dir/file.py"))

    def test_filename_only_returns_empty_string(self):
        self.assertEqual(get_path("file.py"), "")
        self.assertEqual(get_path("file.py"), oracle("file.py"))

    def test_root_path(self):
        self.assertEqual(get_path("/"), "/")
        self.assertEqual(get_path("/"), oracle("/"))

    def test_all_twenty_five_inputs_agree_with_oracle(self):
        mismatches = []
        for inp in INPUTS:
            actual = get_path(inp)
            expected = oracle(inp)
            if actual != expected:
                mismatches.append((inp, actual, expected))
        self.assertFalse(mismatches, msg=f"Mismatches: {mismatches}")

    def test_returns_string_type(self):
        for inp in INPUTS:
            self.assertIsInstance(get_path(inp), str)

    def test_input_immutability(self):
        s = "/var/log/syslog"
        cp = str(s)
        get_path(s)
        self.assertEqual(s, cp)

    def test_repeatability(self):
        p = "/usr/bin/python3"
        self.assertEqual(get_path(p), get_path(p))

if __name__ == "__main__":
    unittest.main()
