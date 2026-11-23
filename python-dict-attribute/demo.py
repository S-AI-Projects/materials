"""Demonstration of Python class and instance dictionary attributes.

Source lines establishing preconditions:
- Line 1: `class DemoClass:` definition.
- Line 2: `class_attr = "This is a class attribute"` establishes class-level attribute.
- Line 4: `def __init__(self, value=None):` establishes instance attribute initialization.
- Line 5: `self.instance_attr = ...` establishes instance-level attribute in instance `__dict__`.
- Line 7: `def method(self):` callable method bound to instances.

Protected Condition:
- Class attributes reside in `DemoClass.__dict__`, while instance attributes reside exclusively
  in `self.__dict__`.
- Plausible mutant: Setting `DemoClass.class_attr` inside `__init__` as an instance attribute
  or overriding class attribute desynchronizes class vs instance dictionary separation.
"""

from typing import Optional


class DemoClass:
    """Class demonstrating class vs instance dictionary attributes."""

    class_attr: str = "This is a class attribute"

    def __init__(self, value: Optional[str] = None):
        """Initializes instance with default or customized instance_attr."""
        if value is None:
            self.instance_attr: str = "This is an instance attribute"
        else:
            self.instance_attr: str = value

    def method(self) -> str:
        """Returns demo method string."""
        return "This is a method"


if __name__ == "__main__":
    print(DemoClass.__dict__)
    demo_object = DemoClass()
    print(demo_object.__dict__)
