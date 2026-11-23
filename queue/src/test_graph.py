"""Native unit and property tests for City (queue/src/graph.py).

Preconditions:
- Line 11: City NamedTuple definition in graph.py.
- Line 23: City.from_dict constructor mapping graph attributes.
- queues.Queue integration: FIFO order, length agreement, instance isolation, and empty-state error.
"""

import sys
import unittest
from unittest.mock import MagicMock

# Mock networkx before importing graph if not installed
if "networkx" not in sys.modules:
    sys.modules["networkx"] = MagicMock()

from graph import City
from queues import Queue


class TestCityQueueInvariants(unittest.TestCase):
    """Verifies City FIFO queue invariants and properties."""

    def setUp(self):
        self.city_a = City(name="Athens", country="Greece", year=-800, latitude=37.98, longitude=23.72)
        self.city_b = City(name="Berlin", country="Germany", year=1237, latitude=52.52, longitude=13.40)
        self.city_c = City(name="Cairo", country="Egypt", year=969, latitude=30.04, longitude=31.23)
        self.city_d = City(name="Dublin", country="Ireland", year=841, latitude=53.34, longitude=-6.26)

    def test_city_namedtuple_instantiation_and_immutability(self):
        """Line 11: Verify City fields, types, and immutability."""
        city = self.city_a
        self.assertEqual(city.name, "Athens")
        self.assertEqual(city.country, "Greece")
        self.assertEqual(city.year, -800)
        self.assertEqual(city.latitude, 37.98)
        self.assertEqual(city.longitude, 23.72)
        with self.assertRaises(AttributeError):
            city.name = "Sparta"  # City is immutable NamedTuple

    def test_city_from_dict(self):
        """Line 23: Verify City.from_dict construction from graph node attributes."""
        attrs = {
            "xlabel": "Rome",
            "country": "Italy",
            "year": "753",
            "latitude": "41.9028",
            "longitude": "12.4964",
        }
        city = City.from_dict(attrs)
        self.assertEqual(city.name, "Rome")
        self.assertEqual(city.country, "Italy")
        self.assertEqual(city.year, 753)
        self.assertAlmostEqual(city.latitude, 41.9028)
        self.assertAlmostEqual(city.longitude, 12.4964)

    def test_required_fixture_fifo_invariant(self):
        """Required Fixture:
        Enqueue A, B, and C; remove twice; insert D; drain the queue.
        Removal order must be A, B, C, D.
        Size and FIFO ordering agree after each operation.
        """
        q = Queue()
        self.assertEqual(len(q), 0)

        # Enqueue A, B, and C
        q.enqueue(self.city_a)
        self.assertEqual(len(q), 1)
        q.enqueue(self.city_b)
        self.assertEqual(len(q), 2)
        q.enqueue(self.city_c)
        self.assertEqual(len(q), 3)

        # Remove twice
        r1 = q.dequeue()
        self.assertEqual(r1, self.city_a)
        self.assertEqual(len(q), 2)

        r2 = q.dequeue()
        self.assertEqual(r2, self.city_b)
        self.assertEqual(len(q), 1)

        # Insert D
        q.enqueue(self.city_d)
        self.assertEqual(len(q), 2)

        # Drain queue
        r3 = q.dequeue()
        self.assertEqual(r3, self.city_c)
        self.assertEqual(len(q), 1)

        r4 = q.dequeue()
        self.assertEqual(r4, self.city_d)
        self.assertEqual(len(q), 0)

        # Verify full sequence of removals
        removals = [r1, r2, r3, r4]
        self.assertEqual(removals, [self.city_a, self.city_b, self.city_c, self.city_d])

    def test_empty_state_behavior(self):
        """Documented empty-state behavior:
        Empty queue has len == 0, and dequeue() raises IndexError.
        """
        q = Queue()
        self.assertEqual(len(q), 0)
        with self.assertRaises(IndexError):
            q.dequeue()

        # Enqueue then dequeue to empty again
        q.enqueue(self.city_a)
        self.assertEqual(len(q), 1)
        res = q.dequeue()
        self.assertEqual(res, self.city_a)
        self.assertEqual(len(q), 0)
        with self.assertRaises(IndexError):
            q.dequeue()

    def test_separate_instances_do_not_share_contents(self):
        """Invariant: Separate queue instances containing City instances are completely isolated."""
        q1 = Queue()
        q2 = Queue()

        q1.enqueue(self.city_a)
        q1.enqueue(self.city_b)

        self.assertEqual(len(q1), 2)
        self.assertEqual(len(q2), 0)

        q2.enqueue(self.city_c)
        self.assertEqual(len(q1), 2)
        self.assertEqual(len(q2), 1)

        d1 = q1.dequeue()
        self.assertEqual(d1, self.city_a)
        self.assertEqual(len(q1), 1)
        self.assertEqual(len(q2), 1)

        d2 = q2.dequeue()
        self.assertEqual(d2, self.city_c)
        self.assertEqual(len(q1), 1)
        self.assertEqual(len(q2), 0)


if __name__ == "__main__":
    unittest.main()
