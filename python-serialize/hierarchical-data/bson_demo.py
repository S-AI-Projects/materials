"""BSON serialization and deserialization demo.

Document Invariant:
Round-trip Identity Invariant:
    For any valid hierarchical document D,
    deserialize(serialize(D)) == D
Preserving:
- Output types: bytes for serialize(), dict for deserialize()
- Ordering & hierarchical structure of keys and elements
- Value types (strings, integers, floats, booleans, nested lists/dicts)
- Immutability: input document D is never mutated during serialization

Preconditions established in source:
- Line 58: with open(file_path, encoding="utf-8") as file:
- Line 59: document = json.load(file)
- Line 60: return encode_document(document)
- Line 64: return decode_document(data)
"""

import json
import os
import struct
from typing import Any, Dict, List, Union

try:
    import bson
except ImportError:
    bson = None


# Minimal pure-Python BSON fallback encoder/decoder when bson package is absent
def _encode_element(key: str, val: Any) -> bytes:
    key_bytes = key.encode("utf-8") + b"\x00"
    if val is None:
        return b"\x0a" + key_bytes
    elif isinstance(val, bool):
        return b"\x08" + key_bytes + (b"\x01" if val else b"\x00")
    elif isinstance(val, int):
        if -2147483648 <= val <= 2147483647:
            return b"\x10" + key_bytes + struct.pack("<i", val)
        else:
            return b"\x12" + key_bytes + struct.pack("<q", val)
    elif isinstance(val, float):
        return b"\x01" + key_bytes + struct.pack("<d", val)
    elif isinstance(val, str):
        str_bytes = val.encode("utf-8") + b"\x00"
        return b"\x02" + key_bytes + struct.pack("<i", len(str_bytes)) + str_bytes
    elif isinstance(val, (list, tuple)):
        sub_doc = {str(i): item for i, item in enumerate(val)}
        return b"\x04" + key_bytes + _fallback_encode(sub_doc)
    elif isinstance(val, dict):
        return b"\x03" + key_bytes + _fallback_encode(val)
    else:
        raise TypeError(f"Unsupported BSON type: {type(val)}")


def _fallback_encode(doc: Dict[str, Any]) -> bytes:
    elements = b"".join(_encode_element(k, v) for k, v in doc.items())
    total_len = 4 + len(elements) + 1
    return struct.pack("<i", total_len) + elements + b"\x00"


def _fallback_decode(data: bytes) -> Dict[str, Any]:
    if len(data) < 5:
        raise ValueError("BSON data too short")
    total_len = struct.unpack("<i", data[:4])[0]
    if total_len != len(data) or data[-1] != 0:
        raise ValueError("Invalid BSON framing")

    idx = 4
    doc: Dict[str, Any] = {}
    while idx < total_len - 1:
        elem_type = data[idx]
        idx += 1
        key_end = data.find(b"\x00", idx)
        key = data[idx:key_end].decode("utf-8")
        idx = key_end + 1

        if elem_type == 0x01:  # float
            val = struct.unpack("<d", data[idx : idx + 8])[0]
            idx += 8
        elif elem_type == 0x02:  # string
            str_len = struct.unpack("<i", data[idx : idx + 4])[0]
            idx += 4
            val = data[idx : idx + str_len - 1].decode("utf-8")
            idx += str_len
        elif elem_type == 0x03:  # document
            sub_len = struct.unpack("<i", data[idx : idx + 4])[0]
            val = _fallback_decode(data[idx : idx + sub_len])
            idx += sub_len
        elif elem_type == 0x04:  # array
            sub_len = struct.unpack("<i", data[idx : idx + 4])[0]
            sub_dict = _fallback_decode(data[idx : idx + sub_len])
            val = [sub_dict[str(i)] for i in range(len(sub_dict))]
            idx += sub_len
        elif elem_type == 0x08:  # boolean
            val = data[idx] != 0
            idx += 1
        elif elem_type == 0x0A:  # null
            val = None
        elif elem_type == 0x10:  # int32
            val = struct.unpack("<i", data[idx : idx + 4])[0]
            idx += 4
        elif elem_type == 0x12:  # int64
            val = struct.unpack("<q", data[idx : idx + 8])[0]
            idx += 8
        else:
            raise ValueError(f"Unknown BSON element type: {elem_type}")
        doc[key] = val
    return doc


def encode_document(document: Dict[str, Any]) -> bytes:
    """Encode dictionary to BSON bytes using bson library or pure-Python codec."""
    if bson is not None and hasattr(bson, "encode"):
        return bson.encode(document)
    return _fallback_encode(document)


def decode_document(data: bytes) -> Dict[str, Any]:
    """Decode BSON bytes to dictionary using bson library or pure-Python codec."""
    if bson is not None and hasattr(bson, "decode"):
        return bson.decode(data)
    return _fallback_decode(data)


def serialize(file_path: str = "data/training.json", document: Any = None) -> bytes:
    """Serialize JSON document or dictionary into BSON bytes."""
    if document is not None:
        return encode_document(document)

    # Resolve file_path relative to module directory if not found in cwd
    if not os.path.isabs(file_path) and not os.path.exists(file_path):
        alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
        if os.path.exists(alt_path):
            file_path = alt_path

    with open(file_path, encoding="utf-8") as file:
        doc = json.load(file)
        return encode_document(doc)


def deserialize(data: bytes) -> Dict[str, Any]:
    """Deserialize BSON bytes into document dictionary."""
    return decode_document(data)


def main(file_path: str = "data/training.json", document: Any = None):
    """Execute serialization round-trip demonstration."""
    binary_json = serialize(file_path=file_path, document=document)
    print(binary_json)
    deserialized = deserialize(binary_json)
    print(deserialized)
    return binary_json, deserialized


if __name__ == "__main__":
    main()
