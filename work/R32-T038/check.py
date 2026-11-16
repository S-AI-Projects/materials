import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python-mixins-course"))

from sequence import Sequence  # noqa: E402

class ListSequence(Sequence):
    def __init__(self, values):
        self.values = list(values)

    def __getitem__(self, index):
        return self.values[index]

    def __len__(self):
        return len(self.values)


class TestSequence(unittest.TestCase):
    # sequence.py line 4 declares the ABC; lines 10 and 14 mark its methods abstract.
    def test_abstract_sequence_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            Sequence()

    # sequence.py lines 10 and 14 require concrete subclasses to implement
    # both abstract methods. Empty input is a valid concrete sequence.
    def test_empty_sequence(self):
        sequence = ListSequence([])
        self.assertEqual(len(sequence), 0)
        self.assertEqual(list(sequence), [])

    # Same abstract-method contract, exercised with ordinary input.
    def test_nonempty_sequence(self):
        values = [10, 20, 30]
        sequence = ListSequence(values)
        self.assertEqual(len(sequence), 3)
        self.assertEqual(list(sequence), [10, 20, 30])
        self.assertEqual(sequence.values, values)

    # A failed abstract-class construction must not affect later use.
    def test_valid_sequence_after_failed_construction(self):
        with self.assertRaises(TypeError):
            Sequence()

        sequence = ListSequence([7])
        self.assertEqual(len(sequence), 1)
        self.assertEqual(list(sequence), [7])


if __name__ == "__main__":
    unittest.main(verbosity=2)
