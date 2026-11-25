"""Invariant/property tests for Vehicle class in car.py."""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from car import Vehicle, Car

SEED = 42
_COLORS = ["red", "blue", "green", "black", "white", "silver", "gold", "orange"]
_MODELS = ["Sedan", "SUV", "Coupe", "Hatchback", "Truck", "Van", "Touring"]

class TestVehicleInvariant(unittest.TestCase):
    def test_smallest_valid_input_empty_strings(self):
        v = Vehicle("", "")
        self.assertEqual(v.color, "")
        self.assertEqual(v.model, "")

    def test_ordinary_valid_input_red_sedan(self):
        v = Vehicle("red", "Sedan")
        self.assertEqual(v.color, "red")
        self.assertEqual(v.model, "Sedan")

    def test_invariant_over_100_bounded_cases(self):
        rng = random.Random(SEED)
        for _ in range(100):
            c = rng.choice(_COLORS)
            m = rng.choice(_MODELS)
            v = Vehicle(c, m)
            self.assertEqual(v.color, c)
            self.assertEqual(v.model, m)

    def test_car_subclass_preserves_vehicle_invariant(self):
        car = Car("blue", "Coupe", 2022)
        self.assertEqual(car.color, "blue")
        self.assertEqual(car.model, "Coupe")
        self.assertEqual(car.year, 2022)

    def test_input_non_mutation(self):
        c = "black"
        m = "Truck"
        Vehicle(c, m)
        self.assertEqual(c, "black")
        self.assertEqual(m, "Truck")

    def test_discrimination_from_mutated_version(self):
        v = Vehicle("red", "Sedan")
        self.assertNotEqual(v.color, "RED")
        self.assertNotEqual(v.model, "sedan")

if __name__ == "__main__":
    unittest.main()
