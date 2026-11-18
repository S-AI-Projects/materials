"""Read CSV data with pandas and provide isolated, repeatable verification seams.

Preconditions established in source:
- Line 3: df = pandas.read_csv("hrdata.csv")
- Line 8: df = pandas.read_csv("hrdata.csv", index_col="Name")
- Line 11: df = pandas.read_csv("hrdata.csv", index_col="Name", parse_dates=["Hire Date"], date_format="%m/%d/%y")
- Line 20: df = pandas.read_csv("hrdata.csv", index_col="Employee", parse_dates=["Hired"], date_format="%m/%d/%y", header=0, names=["Employee", "Hired", "Salary", "Sick Days"])
"""

import csv
import io
import os
from typing import Any, Dict, List, Optional, Union

try:
    import pandas
except ImportError:
    pandas = None


class FallbackDataFrame:
    """Minimal DataFrame abstraction for deterministic testing without pandas."""

    def __init__(self, records: List[Dict[str, Any]], index_col: Optional[str] = None):
        self.records = records
        self.index_col = index_col
        self.columns = list(records[0].keys()) if records else []

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, item: str):
        col_values = [r.get(item) for r in self.records]

        class Series:
            def __init__(self, values):
                self.values = values

            def __getitem__(self, idx):
                return self.values[idx]

            @property
            def iloc(self):
                return self

        return Series(col_values)

    def to_dict(self, orient="records"):
        return [dict(r) for r in self.records]

    def __repr__(self) -> str:
        return f"<FallbackDataFrame rows={len(self.records)} columns={self.columns}>"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FallbackDataFrame):
            return self.records == other.records and self.index_col == other.index_col
        return False


def _fallback_read_csv(
    filepath_or_buffer: Any,
    index_col: Optional[str] = None,
    parse_dates: Optional[List[str]] = None,
    date_format: Optional[str] = None,
    header: int = 0,
    names: Optional[List[str]] = None,
) -> FallbackDataFrame:
    """Fallback reader using Python built-in csv module."""
    if isinstance(filepath_or_buffer, str):
        if not os.path.exists(filepath_or_buffer):
            # Try finding relative to module directory
            alt_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), filepath_or_buffer
            )
            if os.path.exists(alt_path):
                filepath_or_buffer = alt_path
        f = open(filepath_or_buffer, "r", encoding="utf-8")
        close_file = True
    elif hasattr(filepath_or_buffer, "read"):
        f = filepath_or_buffer
        close_file = False
    else:
        raise ValueError("Invalid filepath_or_buffer")

    try:
        reader = csv.reader(f)
        rows = list(reader)
    finally:
        if close_file:
            f.close()

    if not rows:
        return FallbackDataFrame([], index_col=index_col)

    if names is not None:
        col_names = names
        data_rows = rows[header + 1 :] if header == 0 else rows
    else:
        col_names = rows[0]
        data_rows = rows[1:]

    records = []
    for r in data_rows:
        if not r:
            continue
        record = {}
        for idx, col in enumerate(col_names):
            val = r[idx] if idx < len(r) else None
            record[col] = val
        records.append(record)

    return FallbackDataFrame(records, index_col=index_col)


def load_hr_data(
    filepath_or_buffer: Any = "hrdata.csv",
    index_col: Optional[str] = None,
    parse_dates: Optional[List[str]] = None,
    date_format: Optional[str] = None,
    header: int = 0,
    names: Optional[List[str]] = None,
    reader: Optional[Any] = None,
) -> Any:
    """Load and parse HR CSV data with full dependency injection seam.

    Seams:
    - filepath_or_buffer: file path or io.StringIO for memory isolation.
    - reader: optional custom reader callable; defaults to pandas.read_csv or fallback.
    """
    if reader is not None:
        return reader(
            filepath_or_buffer,
            index_col=index_col,
            parse_dates=parse_dates,
            date_format=date_format,
            header=header,
            names=names,
        )

    if pandas is not None and hasattr(pandas, "read_csv"):
        kwargs: Dict[str, Any] = {}
        if index_col is not None:
            kwargs["index_col"] = index_col
        if parse_dates is not None:
            kwargs["parse_dates"] = parse_dates
        if date_format is not None:
            kwargs["date_format"] = date_format
        if header is not None:
            kwargs["header"] = header
        if names is not None:
            kwargs["names"] = names
        return pandas.read_csv(filepath_or_buffer, **kwargs)

    return _fallback_read_csv(
        filepath_or_buffer,
        index_col=index_col,
        parse_dates=parse_dates,
        date_format=date_format,
        header=header,
        names=names,
    )


def run_demo(filepath: str = "hrdata.csv", reader: Optional[Any] = None):
    """Execute standard 4-step demonstration using dependency seam."""
    df1 = load_hr_data(filepath, reader=reader)
    print(df1)
    if len(df1) > 0 and "Hire Date" in df1.columns:
        print(type(df1["Hire Date"][0]))

    df2 = load_hr_data(filepath, index_col="Name", reader=reader)
    print(df2)

    df3 = load_hr_data(
        filepath,
        index_col="Name",
        parse_dates=["Hire Date"],
        date_format="%m/%d/%y",
        reader=reader,
    )
    print(df3)
    if len(df3) > 0 and "Hire Date" in df3.columns:
        print(type(df3["Hire Date"].iloc[0]))

    df4 = load_hr_data(
        filepath,
        index_col="Employee",
        parse_dates=["Hired"],
        date_format="%m/%d/%y",
        header=0,
        names=["Employee", "Hired", "Salary", "Sick Days"],
        reader=reader,
    )
    print(df4)
    return df1, df2, df3, df4


if __name__ == "__main__":
    run_demo()
