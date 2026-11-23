"""Draw an x-y plot with its regression line.

Covers the "X-Y Plots" section of https://realpython.com/python-statistics/
"""

import math

try:
    import matplotlib.pyplot as plt
    plt.style.use("ggplot")
except (ImportError, Exception):
    plt = None

try:
    import numpy as np
except (ImportError, Exception):
    np = None

try:
    import scipy.stats
except (ImportError, Exception):
    scipy = None


def compute_regression_line(x, y):
    """Compute slope, intercept, Pearson correlation coefficient, and formatted regression string.

    Precondition Contracts:
    - Line 15-16: x and y are numerical sequences of equal length (n >= 2) with non-zero variance in x.
    - Line 18: slope, intercept, r computed via linear regression.
    - Line 19: line = f"Regression line: y={intercept:.2f}+{slope:.2f}x, r={r:.2f}"
    """
    if len(x) != len(y):
        raise ValueError(f"x and y must have the same length, got {len(x)} and {len(y)}")
    if len(x) < 2:
        raise ValueError("At least 2 points are required for linear regression")

    if scipy is not None and hasattr(scipy, "stats"):
        slope, intercept, r, *__ = scipy.stats.linregress(x, y)
    else:
        # Exact arithmetic fallback for environments without scipy
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        ss_xx = sum((xi - mean_x) ** 2 for xi in x)
        if ss_xx == 0.0:
            raise ValueError("Variance of x must not be zero")
        ss_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        ss_yy = sum((yi - mean_y) ** 2 for yi in y)
        slope = ss_xy / ss_xx
        intercept = mean_y - slope * mean_x
        denom = math.sqrt(ss_xx * ss_yy)
        r = (ss_xy / denom) if denom != 0.0 else 0.0

    line = f"Regression line: y={intercept:.2f}+{slope:.2f}x, r={r:.2f}"
    return slope, intercept, r, line


def main(x=None, y=None, show=True):
    """Draw an x-y plot with its regression line.

    Executable Worked Example:
    >>> from plot_xy import compute_regression_line
    >>> x = [0.0, 1.0]
    >>> y = [5.0, 7.0]
    >>> slope, intercept, r, line = compute_regression_line(x, y)
    >>> print(line)
    Regression line: y=5.00+2.00x, r=1.00

    Decisive State Transition:
    The input coordinate vectors (x, y) transition through bivariate summary
    statistics (mean_x, mean_y, sum of squared deviations ss_xx, ss_xy) to
    estimate optimal ordinary least squares coefficients:
        slope = ss_xy / ss_xx = 2.0 / 1.0 = 2.0
        intercept = mean_y - slope * mean_x = 6.0 - 2.0 * 0.5 = 5.0
        r = ss_xy / sqrt(ss_xx * ss_yy) = 1.00
    yielding the formatted regression line label.
    """
    if x is None or y is None:
        if np is None:
            raise RuntimeError("numpy is required for default synthetic dataset")
        np.random.seed(seed=0)
        x = np.arange(21)
        y = 5 + 2 * x + 2 * np.random.randn(21)

    slope, intercept, r, line = compute_regression_line(x, y)

    if show and plt is not None:
        fig, ax = plt.subplots()
        ax.plot(x, y, linewidth=0, marker="s", label="Data points")
        y_pred = [intercept + slope * xi for xi in x]
        ax.plot(x, y_pred, label=line)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend(facecolor="white")
        plt.show()

    return slope, intercept, r, line


if __name__ == "__main__":
    main()
