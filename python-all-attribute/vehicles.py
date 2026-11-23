"""Vehicles module defining vehicle types and operational behaviors.

Preconditions & Data Anchors:
- Line 1: `__all__ = ["Car", "Truck"]` exports Car and Truck.
- Line 4: `class Car:` defines Car class contract.
- Line 5: `def start(self):` prints "The car is starting".
- Line 8: `def drive(self):` prints "The car is driving".
- Line 11: `def stop(self):` prints "The car is stopping".

Car Input/Output Contract:
- Inputs:
  - `Car()` accepts no arguments (smallest valid input).
  - Passing arguments to `Car(*args, **kwargs)` raises `TypeError` (domain boundary).
- Outputs:
  - Methods `start()`, `drive()`, and `stop()` return `None`.
  - Side effects: Write fixed strings followed by newline to stdout (`sys.stdout`).
  - Mutation: Instance state has no mutating attributes (pure I/O side effect).
"""

__all__ = ["Car", "Truck"]


class Car:
    """Represents a car with operational behaviors."""

    def start(self):
        print("The car is starting")

    def drive(self):
        print("The car is driving")

    def stop(self):
        print("The car is stopping")


class Truck:
    """Represents a truck with operational behaviors."""

    def start(self):
        print("The truck is starting")

    def drive(self):
        print("The truck is driving")

    def stop(self):
        print("The truck is stopping")
