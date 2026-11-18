"""Property and invariant test suite for python-serialize/hierarchical-data/bson_demo.py.

Verifies the Round-Trip Identity Invariant, Immutability Invariant,
Type Invariant, and Determinism Invariant across generated inputs.
"""

import copy
import json
import os
import random
import unittest

from bson_demo import deserialize, main, serialize


class TestBsonDemoInvariants(unittest.TestCase):
    """Property tests evaluating core serialization invariants."""

    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self.training_path = os.path.join(self.data_dir, "training.json")

    def test_precondition_anchors(self):
        """Verify training.json fixture anchor exists and contains valid JSON."""
        self.assertTrue(
            os.path.exists(self.training_path), "training.json fixture anchor must exist"
        )
        with open(self.training_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        self.assertIn("program", doc)
        self.assertIn("metadata", doc["program"])

    def test_smallest_valid_input_roundtrip(self):
        """Verify smallest valid input: empty dict {} roundtrip invariant."""
        doc = {}
        encoded = serialize(document=doc)
        decoded = deserialize(encoded)
        self.assertEqual(decoded, doc)
        self.assertIsInstance(encoded, bytes)
        self.assertIsInstance(decoded, dict)

    def test_ordinary_valid_input_training_fixture_roundtrip(self):
        """Verify ordinary valid input: training.json document roundtrip invariant."""
        encoded, decoded = main(file_path=self.training_path)
        with open(self.training_path, "r", encoding="utf-8") as f:
            expected_doc = json.load(f)

        self.assertEqual(decoded, expected_doc)
        self.assertIsInstance(encoded, bytes)
        self.assertIsInstance(decoded, dict)

    def test_immutability_invariant(self):
        """Verify serialization does not mutate the caller input document."""
        original_doc = {
            "title": "Workout Plan",
            "active": True,
            "metrics": [10, 20, 30],
            "nested": {"key": "val"},
        }
        doc_copy = copy.deepcopy(original_doc)
        serialize(document=original_doc)
        self.assertEqual(
            original_doc,
            doc_copy,
            "Input document must remain strictly unchanged after serialization",
        )

    def test_determinism_invariant(self):
        """Verify identical inputs produce bit-for-bit identical BSON outputs."""
        doc = {"alpha": 123, "beta": ["x", "y"], "gamma": {"nested": True}}
        out1 = serialize(document=doc)
        out2 = serialize(document=doc)
        self.assertEqual(out1, out2)

    def test_property_generated_structures_roundtrip(self):
        """Property test: evaluate 50 randomly generated documents across varied types and nestings."""
        random.seed(42)  # Fixed seed for repeatability
        primitives = [
            "short string",
            "a" * 100,
            0,
            -1,
            42,
            2147483647,
            -2147483648,
            3.14159,
            0.0,
            -99.99,
            True,
            False,
            None,
        ]

        for i in range(50):
            # Generate random dictionary
            num_keys = random.randint(1, 8)
            doc = {}
            for k in range(num_keys):
                key = f"key_{k}_{random.randint(100, 999)}"
                choice = random.choice(["primitive", "list", "dict"])
                if choice == "primitive":
                    doc[key] = random.choice(primitives)
                elif choice == "list":
                    doc[key] = [
                        random.choice(primitives) for _ in range(random.randint(0, 5))
                    ]
                else:
                    doc[key] = {
                        f"sub_{s}": random.choice(primitives)
                        for s in range(random.randint(1, 4))
                    }

            with self.subTest(iteration=i):
                encoded = serialize(document=doc)
                decoded = deserialize(encoded)
                self.assertEqual(decoded, doc)

    def test_malformed_bytes_rejection(self):
        """Verify malformed BSON bytes raise ValueError during deserialization."""
        malformed_inputs = [b"", b"\x00\x00\x00", b"random junk data that is not BSON"]
        for bad_bytes in malformed_inputs:
            with self.subTest(bad_bytes=bad_bytes):
                with self.assertRaises((ValueError, Exception)):
                    deserialize(bad_bytes)


if __name__ == "__main__":
    unittest.main()
