"""Unit and executable documentation tests for python-qr-code/scripts/basic_qrcode.py.

Preconditions:
- Line 1: `import segno`
- Line 3: `qrcode = segno.make_qr(...)`
- Line 4: `qrcode.save(...)`
- Smallest valid input fixture: content="" -> empty string QR matrix
- Ordinary input fixture: content="Hello, World" -> standard QR code
"""

import unittest
from unittest.mock import MagicMock

from basic_qrcode import QRCodeResult, create_qrcode


class TestBasicQRCode(unittest.TestCase):
    """Test suite for executable documentation and create_qrcode lifecycle."""

    def setUp(self):
        self.mock_segno = MagicMock()
        self.mock_qr_instance = MagicMock()
        self.mock_segno.make_qr.return_value = self.mock_qr_instance

    def test_precondition_line3_smallest_valid_input(self):
        """Line 3: Smallest valid input fixture: empty string content=''."""
        literal_input = ""
        result = create_qrcode(literal_input, segno_module=self.mock_segno)
        self.mock_segno.make_qr.assert_called_with("")
        self.assertEqual(result.content, "")
        self.assertEqual(result.raw_qr, self.mock_qr_instance)
        self.assertIsNone(result.saved_path)

    def test_precondition_line3_and_line4_ordinary_input_with_save(self):
        """Line 3 & 4: Ordinary input fixture: content='Hello, World', saved to file."""
        literal_input = "Hello, World"
        output_file = "basic_qrcode.png"
        result = create_qrcode(literal_input, output_file=output_file, segno_module=self.mock_segno)
        self.mock_segno.make_qr.assert_called_with("Hello, World")
        self.mock_qr_instance.save.assert_called_with("basic_qrcode.png")
        self.assertEqual(result.content, "Hello, World")
        self.assertEqual(result.saved_path, "basic_qrcode.png")

    def test_executable_documentation_worked_example(self):
        """Verifies the documented worked example transitions through states."""
        # Step 1: Input state
        content = "Hello, World"
        out_file = "basic_qrcode.png"

        # Step 2: Intermediate state transition
        code = create_qrcode(content, output_file=out_file, segno_module=self.mock_segno)

        # Step 3: Assert displayed / intermediate properties
        displayed_message = f"QR Code created with content: {code.content}"
        self.assertEqual(displayed_message, "QR Code created with content: Hello, World")
        self.assertEqual(code.saved_path, "basic_qrcode.png")


if __name__ == "__main__":
    unittest.main()
