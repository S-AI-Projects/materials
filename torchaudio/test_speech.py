"""Deterministic execution and repeatability tests for SpeechSample."""
import sys
import types
import os
import unittest
from unittest.mock import MagicMock

# Lightweight stubs for external packages
torch_stub = types.ModuleType("torch")
class _Tensor:
    def __init__(self, data):
        self._data = data
    def size(self, dim):
        if dim == 0:
            return len(self._data)
        return len(self._data[0]) if self._data else 0
    def numpy(self):
        return self._data
    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            row_k, col_k = key
            if isinstance(col_k, slice):
                stop = col_k.stop or len(self._data[0])
                return _Tensor([r[:stop] for r in self._data])
        return self

torch_stub.Tensor = _Tensor
torch_stub.clamp = lambda t, *a, **kw: t
torch_stub.randn_like = lambda t: t

torch_nn = types.ModuleType("torch.nn")
torch_nn_f = types.ModuleType("torch.nn.functional")
torch_nn_f.pad = lambda t, pad: t
torch_utils = types.ModuleType("torch.utils")
torch_utils_d = types.ModuleType("torch.utils.data")
torch_utils_d.Dataset = object

sys.modules.setdefault("torch", torch_stub)
sys.modules.setdefault("torch.nn", torch_nn)
sys.modules.setdefault("torch.nn.functional", torch_nn_f)
sys.modules.setdefault("torch.utils", torch_utils)
sys.modules.setdefault("torch.utils.data", torch_utils_d)
sys.modules.setdefault("sounddevice", MagicMock())
sys.modules.setdefault("IPython", MagicMock())
sys.modules.setdefault("IPython.display", MagicMock())
sys.modules.setdefault("torchaudio", MagicMock())
sys.modules.setdefault("torchaudio.functional", MagicMock())
sys.modules.setdefault("torchaudio.datasets", MagicMock())
sys.modules.setdefault("torchaudio.datasets.speechcommands", MagicMock())
sys.modules.setdefault("tqdm", MagicMock())

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from speech import SpeechSample

class TestSpeechSampleDeterminism(unittest.TestCase):
    def test_smallest_valid_input_single_sample(self):
        wf = _Tensor([[0.5]])
        s = SpeechSample(wf, 1, "yes", "spk0", 0)
        self.assertEqual(s.num_channels, 1)
        self.assertEqual(s.num_samples, 1)
        self.assertEqual(s.num_seconds, 1.0)

    def test_ordinary_valid_input_16k(self):
        wf = _Tensor([[0.0] * 16000])
        s = SpeechSample(wf, 16000, "stop", "spk1", 1)
        self.assertEqual(s.num_channels, 1)
        self.assertEqual(s.num_samples, 16000)
        self.assertAlmostEqual(s.num_seconds, 1.0)

    def test_repeatability_identical_results_across_calls(self):
        wf = _Tensor([[0.0] * 8000])
        s = SpeechSample(wf, 8000, "up", "spk2", 2)
        r1 = s.num_seconds
        r2 = s.num_seconds
        self.assertEqual(r1, r2)

    def test_input_isolation_between_instances(self):
        wf1 = _Tensor([[0.0] * 4000])
        wf2 = _Tensor([[0.0] * 8000])
        s1 = SpeechSample(wf1, 4000, "left", "spk1", 0)
        s2 = SpeechSample(wf2, 8000, "right", "spk2", 1)
        self.assertEqual(s1.num_samples, 4000)
        self.assertEqual(s2.num_samples, 8000)

    def test_pad_trim_pure_non_mutation(self):
        wf = _Tensor([[0.0] * 16000])
        s = SpeechSample(wf, 16000, "go", "spk3", 0)
        trimmed = s.pad_trim(0.5)
        self.assertEqual(trimmed.num_samples, 8000)
        self.assertEqual(s.num_samples, 16000)

if __name__ == "__main__":
    unittest.main()
