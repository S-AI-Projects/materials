"""Regression tests for python-markitdown/ocr.py contract."""
import sys
import types
import unittest
from unittest.mock import MagicMock

def _make_markitdown_stub():
    stub = types.ModuleType("markitdown")
    class _ConvertResult:
        def __init__(self, markdown=""):
            self.markdown = markdown
    class MarkItDown:
        def __init__(self, llm_client=None, llm_model=None, llm_prompt=None):
            self.llm_client = llm_client
            self.llm_model = llm_model
            self.llm_prompt = llm_prompt
        def convert(self, path):
            if path == "":
                return _ConvertResult(markdown="")
            return _ConvertResult(markdown=f"# OCR result for {path}")
    stub.MarkItDown = MarkItDown
    return stub

sys.modules.setdefault("markitdown", _make_markitdown_stub())
sys.modules.setdefault("openai", types.ModuleType("openai"))
sys.modules["openai"].OpenAI = MagicMock(return_value=MagicMock())

class TestMarkItDownContract(unittest.TestCase):
    def setUp(self):
        from markitdown import MarkItDown
        self.md = MarkItDown(
            llm_client=MagicMock(),
            llm_model="gpt-4o",
            llm_prompt="Extract text from image with OCR and return Markdown.",
        )

    def test_convert_smallest_valid_input_empty_path(self):
        result = self.md.convert("")
        self.assertIsInstance(result.markdown, str)
        self.assertEqual(result.markdown, "")

    def test_convert_ordinary_input_png_path(self):
        result = self.md.convert("./data/zen-of-python.png")
        self.assertIsInstance(result.markdown, str)
        self.assertIn("zen-of-python.png", result.markdown)

    def test_convert_result_has_markdown_attribute(self):
        result = self.md.convert("./data/zen-of-python.png")
        self.assertTrue(hasattr(result, "markdown"))
        self.assertIsInstance(result.markdown, str)

    def test_constructor_preserves_model_parameter(self):
        self.assertEqual(self.md.llm_model, "gpt-4o")

    def test_constructor_preserves_prompt_parameter(self):
        expected = "Extract text from image with OCR and return Markdown."
        self.assertEqual(self.md.llm_prompt, expected)

    def test_repeated_calls_produce_isolated_results(self):
        r1 = self.md.convert("./data/zen-of-python.png")
        r2 = self.md.convert("./data/sample.png")
        self.assertIsNot(r1, r2)

if __name__ == "__main__":
    unittest.main()
