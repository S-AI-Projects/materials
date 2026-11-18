"""Altair Steps Visualization.

Defines the weekly step count visualization using Altair and Pandas.
Supported boundary contract:
- Smallest valid input: Single-entry data mapping/DataFrame with columns 'Day' and 'Steps'
- Ordinary input: 7-day weekly step dataset
- Boundary condition: Empty dataset (0 rows)
- Preconditions established at:
    * Line 21: DEFAULT_STEPS_DATA fixture definition
    * Line 22: Day column labels ("1-Mon" through "7-Sun")
    * Line 23: Steps integer counts (6200 through 3769)
"""

try:
    import altair as alt
except ImportError:
    alt = None

try:
    import pandas as pd
except ImportError:
    pd = None

# Fixture / Data Anchors
DEFAULT_STEPS_DATA = {
    "Day": ["1-Mon", "2-Tue", "3-Wed", "4-Thu", "5-Fri", "6-Sat", "7-Sun"],
    "Steps": [6200, 8400, 7100, 9800, 5500, 9870, 3769],
}


def validate_steps_data(data) -> bool:
    """Validate that input data contains the required 'Day' and 'Steps' columns.

    Boundary Rules:
    - Data must not be None.
    - Data must contain 'Day' and 'Steps' columns/keys.
    - Size >= 0 is supported (empty dataset is a valid domain boundary).
    - Missing required fields raises ValueError.
    """
    if data is None:
        raise ValueError("Data cannot be None")

    if hasattr(data, "columns"):
        cols = list(data.columns)
    elif isinstance(data, dict):
        cols = list(data.keys())
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")

    if "Day" not in cols or "Steps" not in cols:
        raise ValueError("Data must contain both 'Day' and 'Steps' fields")
    return True


def create_weekly_steps_chart(data=None):
    """Create and return an Altair bar chart for daily steps.

    Args:
        data: Optional DataFrame or dict containing 'Day' and 'Steps'.
              Defaults to DEFAULT_STEPS_DATA.

    Returns:
        Configured Altair Chart object.
    """
    target_data = data if data is not None else DEFAULT_STEPS_DATA
    validate_steps_data(target_data)

    chart_input = target_data
    if pd is not None and isinstance(chart_input, dict):
        chart_input = pd.DataFrame(chart_input)

    if alt is None:
        return chart_input

    return (
        alt.Chart(chart_input)
        .mark_bar()
        .encode(
            x="Day",
            y="Steps",
        )
    )


# Module-level exports matching original script
if pd is not None:
    steps = pd.DataFrame(DEFAULT_STEPS_DATA)
else:
    steps = DEFAULT_STEPS_DATA

if alt is not None:
    weekly_steps = create_weekly_steps_chart(steps)
else:
    weekly_steps = create_weekly_steps_chart(steps)
