# R32-T036 verification

## Python
Python 3.11.18

## Pytest
pytest 9.2.0

## Test command
python work/R32-T036/check.py

## Test output
..                                                                       [100%]
2 passed in 0.02s

## Refactor source lines
    10	def _format_position(row):
    11	    return Cursor.POS(1, 1 + row)
    14	def print_at(row, text):
    16	    time.sleep(0.03)
    36	    print(Cursor.POS(1, 1 + len(sys.argv)))

## Test cases
- row=0, text="": expected cursor output "\033[1;1H"
- row=4, text="hello": expected cursor output "\033[5;1Hhello"

## Behaviour preserved
- Cursor position, string conversion, 0.03-second sleep, None return.
