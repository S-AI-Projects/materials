"""Mutation-resistant tests for evaluate_model in sentiment_analyzer.py."""
import sys
import types
import os
import unittest
from unittest.mock import MagicMock

# Stub spacy & pandas
spacy_stub = types.ModuleType("spacy")
spacy_util = types.ModuleType("spacy.util")
spacy_util.compounding = lambda s, st, c: iter([s])
spacy_util.minibatch = lambda d, size: [d]
sys.modules.setdefault("spacy", spacy_stub)
sys.modules.setdefault("spacy.util", spacy_util)
sys.modules.setdefault("pandas", MagicMock())

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sentiment_analyzer import evaluate_model, eval_list

class _ReviewStub:
    def __init__(self, score):
        self.cats = {"pos": score, "neg": 1.0 - score}

class _TextCatStub:
    def __init__(self, scores):
        self.scores = scores
    def pipe(self, reviews):
        return [_ReviewStub(s) for s in self.scores]

class TestEvaluateModelMutationResistance(unittest.TestCase):
    def test_smallest_empty_dataset_raises_value_error(self):
        with self.assertRaises(ValueError):
            evaluate_model(lambda x: x, _TextCatStub([]), [])

    def test_ordinary_valid_input_true_positive(self):
        data = [("great movie", {"cats": {"pos": True, "neg": False}})]
        res = evaluate_model(lambda x: x, _TextCatStub([0.9]), data)
        self.assertGreater(res["precision"], 0.9)
        self.assertGreater(res["recall"], 0.9)
        self.assertGreater(res["f-score"], 0.9)

    def test_mutation_detection_inclusive_half_boundary(self):
        # A mutant with score > 0.5 would fail this test
        data = [("ok movie", {"cats": {"pos": True, "neg": False}})]
        res = evaluate_model(lambda x: x, _TextCatStub([0.5]), data)
        self.assertGreater(res["precision"], 0.5)

    def test_false_positive_case(self):
        data = [("bad movie", {"cats": {"pos": False, "neg": True}})]
        res = evaluate_model(lambda x: x, _TextCatStub([0.8]), data)
        self.assertAlmostEqual(res["precision"], 0.0, places=4)

    def test_eval_list_initially_empty(self):
        self.assertEqual(eval_list, [])

if __name__ == "__main__":
    unittest.main()
