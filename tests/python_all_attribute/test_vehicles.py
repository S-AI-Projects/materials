"""Regression tests for Car in python-all-attribute/vehicles.py.

Source fixture/data anchors:
    python-all-attribute/vehicles.py:1: __all__ = ["Car", "Truck"]
    python-all-attribute/vehicles.py:4: class Car:
    python-all-attribute/vehicles.py:5:     def start(self):
    python-all-attribute/vehicles.py:6:         print("The car is starting")
    python-all-attribute/vehicles.py:8:     def drive(self):
    python-all-attribute/vehicles.py:9:         print("The car is driving")
    python-all-attribute/vehicles.py:11:    def stop(self):
    python-all-attribute/vehicles.py:12:        print("The car is stopping")
"""

import io
import unittest
from unittest.mock import patch
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "python-all-attribute"))

import vehicles  # noqa: E402


class TestCarRegression(unittest.TestCase):
    """Focused regression tests for Car testing return values, mutations, and stdout."""

    def test_all_export_fixture(self):
        """Precondition established at vehicles.py:1: __all__ = ['Car', 'Truck']."""
        expected_all = ["Car", "Truck"]
        actual_all = getattr(vehicles, "__all__", None)
        self.assertEqual(
            actual_all,
            expected_all,
            f"Expected __all__ to be {expected_all}, got {actual_all}",
        )
        self.assertIn("Car", vehicles.__all__)

    def test_car_initialization_smallest_valid_input(self):
        """Smallest valid input: Car() with no positional or keyword arguments.

        Precondition: vehicles.py:4 (class Car: default __init__).
        Literal input: ()
        Expected return: isinstance Car, exact type Car.
        Expected mutation: __dict__ is empty (no instance attributes added).
        """
        # Literal input
        args = ()
        kwargs = {}

        # Pre-instantiation / instantiation
        car = vehicles.Car(*args, **kwargs)

        # Assert return / instance identity
        self.assertIsInstance(car, vehicles.Car)
        self.assertIs(type(car), vehicles.Car)

        # Assert observable mutation separately
        expected_dict = {}
        actual_dict = car.__dict__
        self.assertEqual(
            actual_dict,
            expected_dict,
            f"Expected car.__dict__={expected_dict}, got {actual_dict}",
        )

    def test_car_initialization_ordinary_input_rejected(self):
        """Ordinary input domain boundary: Passing arguments to Car(...) raises TypeError.

        Precondition: vehicles.py:4 (class Car has no custom __init__ accepting arguments).
        Literal input: ("Tesla", "Model 3")
        Independently calculated expectation: object.__init__() takes exactly one argument (the instance).
        """
        literal_args = ("Tesla", "Model 3")
        with self.assertRaises(TypeError):
            vehicles.Car(*literal_args)

    def test_car_start_behavior(self):
        """Preconditions: vehicles.py:4 (class Car) and vehicles.py:5-6 (def start).

        Literal input: car.start() with self=car, no additional args.
        Expected return value: None.
        Observable mutation: none (car.__dict__ remains unchanged).
        Expected side-effect (I/O): prints 'The car is starting\\n'.
        """
        car = vehicles.Car()
        pre_dict = dict(car.__dict__)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            ret = car.start()
            actual_output = mock_stdout.getvalue()

        expected_ret = None
        expected_output = "The car is starting\n"
        expected_dict = pre_dict

        # Assert returned values and observable mutation separately
        self.assertIs(
            ret,
            expected_ret,
            f"Expected return {expected_ret}, got {ret}",
        )
        self.assertEqual(
            car.__dict__,
            expected_dict,
            f"Observable mutation detected: {car.__dict__} != {expected_dict}",
        )
        self.assertEqual(
            actual_output,
            expected_output,
            f"Expected stdout {expected_output!r}, got {actual_output!r}",
        )

    def test_car_drive_behavior(self):
        """Preconditions: vehicles.py:4 (class Car) and vehicles.py:8-9 (def drive).

        Literal input: car.drive() with self=car, no additional args.
        Expected return value: None.
        Observable mutation: none (car.__dict__ remains unchanged).
        Expected side-effect (I/O): prints 'The car is driving\\n'.
        """
        car = vehicles.Car()
        pre_dict = dict(car.__dict__)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            ret = car.drive()
            actual_output = mock_stdout.getvalue()

        expected_ret = None
        expected_output = "The car is driving\n"
        expected_dict = pre_dict

        self.assertIs(
            ret,
            expected_ret,
            f"Expected return {expected_ret}, got {ret}",
        )
        self.assertEqual(
            car.__dict__,
            expected_dict,
            f"Observable mutation detected: {car.__dict__} != {expected_dict}",
        )
        self.assertEqual(
            actual_output,
            expected_output,
            f"Expected stdout {expected_output!r}, got {actual_output!r}",
        )

    def test_car_stop_behavior(self):
        """Preconditions: vehicles.py:4 (class Car) and vehicles.py:11-12 (def stop).

        Literal input: car.stop() with self=car, no additional args.
        Expected return value: None.
        Observable mutation: none (car.__dict__ remains unchanged).
        Expected side-effect (I/O): prints 'The car is stopping\\n'.
        """
        car = vehicles.Car()
        pre_dict = dict(car.__dict__)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            ret = car.stop()
            actual_output = mock_stdout.getvalue()

        expected_ret = None
        expected_output = "The car is stopping\n"
        expected_dict = pre_dict

        self.assertIs(
            ret,
            expected_ret,
            f"Expected return {expected_ret}, got {ret}",
        )
        self.assertEqual(
            car.__dict__,
            expected_dict,
            f"Observable mutation detected: {car.__dict__} != {expected_dict}",
        )
        self.assertEqual(
            actual_output,
            expected_output,
            f"Expected stdout {expected_output!r}, got {actual_output!r}",
        )

    def test_repeated_method_calls_boundary(self):
        """Repeated-value / idempotence domain boundary.

        Preconditions: vehicles.py:4-12 (repeated sequential invocations).
        Repeated calls: drive() invoked 3 times in succession.
        Expected: identical return values (None), identical outputs, and zero observable state accumulation.
        """
        car = vehicles.Car()

        for step in range(3):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                ret = car.drive()
                out = mock_stdout.getvalue()

            self.assertIs(ret, None, f"Iteration {step}: expected return None, got {ret}")
            self.assertEqual(
                out,
                "The car is driving\n",
                f"Iteration {step}: expected stdout 'The car is driving\\n', got {out!r}",
            )
            self.assertEqual(
                car.__dict__,
                {},
                f"Iteration {step}: expected empty instance dict, got {car.__dict__}",
            )


if __name__ == "__main__":
    unittest.main()
