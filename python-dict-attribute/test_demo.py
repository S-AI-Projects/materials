"""Mutation-resistant regression tests for DemoClass in python-dict-attribute/demo.py.

Preconditions:
- Line 1: `class DemoClass:`
- Line 2: `class_attr = "This is a class attribute"`
- Line 5: `self.instance_attr = ...`
- Line 7: `def method(self): return "This is a method"`
- Smallest valid input fixture: `DemoClass(value="")` -> `instance_attr == ""`
- Ordinary input fixture: `DemoClass(value="custom")` and `DemoClass()` -> `instance_attr == "This is an instance attribute"`
"""

import unittest
from demo import DemoClass


class TestDemoClass(unittest.TestCase):
    """Test suite protecting DemoClass against attribute dictionary mutation mistakes."""

    def test_precondition_line1_and_line2_class_attribute_isolation(self):
        """Line 2: class_attr must belong to DemoClass.__dict__ and not instance __dict__."""
        self.assertIn("class_attr", DemoClass.__dict__)
        self.assertEqual(DemoClass.class_attr, "This is a class attribute")

        instance = DemoClass()
        self.assertNotIn("class_attr", instance.__dict__)

    def test_precondition_smallest_valid_input(self):
        """Smallest valid input fixture: DemoClass(value="") with empty string."""
        instance = DemoClass(value="")
        self.assertEqual(instance.instance_attr, "")
        self.assertEqual(instance.__dict__, {"instance_attr": ""})
        self.assertEqual(instance.method(), "This is a method")

    def test_precondition_ordinary_input(self):
        """Ordinary input fixture: DemoClass() with default value."""
        instance = DemoClass()
        expected_val = "This is an instance attribute"
        self.assertEqual(instance.instance_attr, expected_val)
        self.assertEqual(instance.__dict__, {"instance_attr": expected_val})
        self.assertEqual(instance.method(), "This is a method")

    def test_method_callable_and_unmutated(self):
        """Line 7: method returns expected method string and remains unmutated."""
        instance = DemoClass()
        self.assertEqual(instance.method(), "This is a method")
        self.assertNotIn("method", instance.__dict__)


if __name__ == "__main__":
    unittest.main()
