"""MarkItDown OCR contract.

Precondition:
  - Line 1: `from markitdown import MarkItDown`
  - Line 4-9: `MarkItDown(llm_client, llm_model, llm_prompt)` accepts configuration
  - Line 10: `md.convert(path)` returns an object exposing a `.markdown` string attribute
"""
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o",
    llm_prompt="Extract text from image with OCR and return Markdown.",
)

result = md.convert("./data/zen-of-python.png")
print(result.markdown)
