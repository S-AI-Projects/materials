"""Grade curving algorithm from numpy-tutorial/curve_grades.ipynb.

Preconditions:
- Line 1 in curve_grades.ipynb: CURVE_CENTER = 80
- Smallest valid input: [70.0] -> [80.0]
- Ordinary input: [72, 35, 64, 88, 51, 90, 74, 12] -> [91.25, 54.25, 83.25, 100.0, 70.25, 100.0, 93.25, 31.25]
"""

from typing import List, Sequence

CURVE_CENTER = 80.0


def curve(grades: Sequence[float], curve_center: float = CURVE_CENTER) -> List[float]:
    """Adjusts a sequence of grades so that the average is roughly shifted to curve_center.

    Preconditions:
    - Never causes a student's grade to decrease.
    - Never causes the final grade to exceed 100.0.
    - Time complexity: O(N) operations where N = len(grades).
    """
    if not grades:
        return []

    count = len(grades)
    average = sum(grades) / count
    change = curve_center - average

    result = []
    for g in grades:
        adjusted = g + change
        # np.clip(new_grades, grades, 100)
        clipped = max(g, min(100.0, adjusted))
        result.append(clipped)

    return result
