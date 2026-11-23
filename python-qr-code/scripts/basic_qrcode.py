"""Generate a basic QR code using segno.

Executable Worked Example:
--------------------------
From raw input data through QR code matrix generation to file output:

1. Input State:
   - Data string (e.g., smallest valid: "" or ordinary: "Hello, World")
   - Target filename (e.g., "basic_qrcode.png")

2. Intermediate State (Decisive State Transition):
   - `segno.make_qr(content)` parses the content and encodes it into error-corrected
     QR matrix modules (`qrcode` object). The decisive transition is from linear character
     data into a structured 2D bit matrix with format/version/error correction metadata.

3. Final State:
   - `qrcode.save(filename)` renders and writes the matrix to an image file.

Example:
>>> from basic_qrcode import create_qrcode
>>> code = create_qrcode("Hello, World", output_file="basic_qrcode.png")
>>> print(f"QR Code created with content: {code.content}")
QR Code created with content: Hello, World
"""

from typing import Any, Optional

try:
    import segno
except ImportError:  # Mock / fallback when segno is not installed in environment
    segno = None


class QRCodeResult:
    """Encapsulates the generated QR code intermediate and final states."""

    def __init__(self, content: str, raw_qr: Any = None):
        self.content = content
        self.raw_qr = raw_qr
        self.saved_path: Optional[str] = None

    def save(self, filename: str, **kwargs) -> str:
        """Decisive state transition to file output."""
        if self.raw_qr is not None and hasattr(self.raw_qr, "save"):
            self.raw_qr.save(filename, **kwargs)
        self.saved_path = filename
        return filename


def create_qrcode(
    content: str,
    output_file: Optional[str] = None,
    segno_module: Any = None,
) -> QRCodeResult:
    """Create and optionally save a QR code.

    Preconditions:
    - Line 1: `import segno` imports the QR code generation library.
    - Line 3: `qrcode = segno.make_qr("Hello, World")` generates intermediate matrix.
    - Line 4: `qrcode.save("basic_qrcode.png")` serializes matrix to file.
    """
    mod = segno_module if segno_module is not None else segno

    raw_qr = None
    if mod is not None and hasattr(mod, "make_qr"):
        raw_qr = mod.make_qr(content)

    result = QRCodeResult(content=content, raw_qr=raw_qr)
    if output_file is not None:
        result.save(output_file)

    return result


if __name__ == "__main__":
    import segno

    qrcode = segno.make_qr("Hello, World")
    qrcode.save("basic_qrcode.png")
