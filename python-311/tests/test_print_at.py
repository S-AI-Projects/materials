import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import count


def test_print_at_smallest_valid_row(monkeypatch):
    printed = []
    sleeps = []
    monkeypatch.setattr(count, "print", printed.append, raising=False)
    monkeypatch.setattr(count.time, "sleep", sleeps.append)

    result = count.print_at(0, "")

    assert printed == ["\x1b[1;1H"]
    assert sleeps == [0.03]
    assert result is None


def test_print_at_ordinary_row(monkeypatch):
    printed = []
    sleeps = []
    monkeypatch.setattr(count, "print", printed.append, raising=False)
    monkeypatch.setattr(count.time, "sleep", sleeps.append)

    result = count.print_at(4, "hello")

    assert printed == ["\x1b[5;1Hhello"]
    assert sleeps == [0.03]
    assert result is None
