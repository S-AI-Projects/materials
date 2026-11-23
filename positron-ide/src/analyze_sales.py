# %%
"""Positron IDE: Sales Analysis.

Analyzes retail and wholesale sales order data, summarizes median order values
across product categories and order types, and generates comparative bar visualizations.

Supported Boundary Contract:
- Target Item: positron-ide (analyze_sales.py)
- Preconditions established at:
    * Line 9: `sales = pd.read_csv(...)` loading cleaned sales data
    * Line 11: `parse_dates=['order_date']` parsing date column
    * Line 15: Required numerical columns: 'quantity', 'unit_price', 'sale_price'
    * Line 16: Required categorical/grouping column: 'order_type'
    * Line 19-20: Grouping columns: ['product_category', 'order_type']
    * Line 23: Aggregate size column: 'order_number' -> 'orders'
    * Line 24: Aggregate median column: 'sale_price' -> 'median_order_value'
    * Line 30-34: Pivot contract: index='product_category', columns='order_type', values='median_order_value'
- Supported Domain Boundaries:
    * Smallest valid input: Single-row sales DataFrame/mapping containing required columns
    * Ordinary input: Multi-row sales dataset across multiple categories and order types
    * Valid boundary (empty dataset): 0-row dataset containing required column schema
    * Explicitly unsupported: None, missing required columns, non-tabular types
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path.cwd()

REQUIRED_COLUMNS = {
    "order_number",
    "order_date",
    "order_type",
    "product_category",
    "quantity",
    "unit_price",
    "sale_price",
}


def validate_sales_data(df: pd.DataFrame) -> bool:
    """Validate that sales data conforms to the supported schema boundaries.

    Preconditions:
    - Data must not be None (raises ValueError).
    - Data must be a pandas DataFrame or mapping convertible to DataFrame.
    - Required columns must be present (raises ValueError if missing).
    - Empty DataFrame (0 rows) with valid schema is a supported boundary.
    """
    if df is None:
        raise ValueError("Sales data cannot be None")

    if not isinstance(df, (pd.DataFrame, dict)):
        raise ValueError(f"Unsupported sales data type: {type(df)}")

    if isinstance(df, dict):
        cols = set(df.keys())
    else:
        cols = set(df.columns)

    missing = REQUIRED_COLUMNS - cols
    if missing:
        raise ValueError(
            f"Missing required columns in sales data: {sorted(list(missing))}"
        )
    return True


def load_clean_sales(file_path: Path | str | None = None) -> pd.DataFrame:
    """Load cleaned sales data from disk.

    Preconditions established at Lines 9-12.
    """
    path = (
        Path(file_path)
        if file_path is not None
        else PROJECT_ROOT / "data/sales_clean.csv"
    )
    return pd.read_csv(
        path,
        parse_dates=["order_date"],
    )


def summarize_orders(sales_df: pd.DataFrame) -> pd.DataFrame:
    """Group sales data by product category and order type and calculate order summary.

    Preconditions established at Lines 19-25.
    Returns:
        DataFrame with columns ['product_category', 'order_type', 'orders', 'median_order_value']
    """
    validate_sales_data(sales_df)
    if isinstance(sales_df, dict):
        sales_df = pd.DataFrame(sales_df)

    if sales_df.empty:
        return pd.DataFrame(
            columns=[
                "product_category",
                "order_type",
                "orders",
                "median_order_value",
            ]
        )

    return sales_df.groupby(
        ["product_category", "order_type"],
        as_index=False,
    ).agg(
        orders=("order_number", "size"),
        median_order_value=("sale_price", "median"),
    )


def build_chart_data(order_summary_df: pd.DataFrame) -> pd.DataFrame:
    """Pivot order summary to create table indexed by product category with order types as columns.

    Preconditions established at Lines 30-34.
    """
    if order_summary_df.empty:
        return pd.DataFrame()

    return order_summary_df.pivot(
        index="product_category",
        columns="order_type",
        values="median_order_value",
    )


def plot_sales_chart(chart_data_df: pd.DataFrame, show: bool = True):
    """Generate and display bar chart for median order value by category and order type.

    Preconditions established at Lines 36-40.
    """
    if chart_data_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set(xlabel="Product category", ylabel="Median order value")
        ax.set_title("Retail and Wholesale Order Values")
        plt.tight_layout()
        if show:
            plt.show()
        return ax

    ax = chart_data_df.plot.bar(rot=0, figsize=(8, 4))
    ax.set(xlabel="Product category", ylabel="Median order value")
    ax.set_title("Retail and Wholesale Order Values")
    plt.tight_layout()
    if show:
        plt.show()
    return ax


# Module execution block preserving original script behavior
if __name__ == "__main__":
    sales = load_clean_sales()
    print(sales[["quantity", "unit_price", "sale_price"]].describe().round(2))
    print(sales["order_type"].value_counts())

    order_summary = summarize_orders(sales)
    print(order_summary.round(2).to_string(index=False))

    chart_data = build_chart_data(order_summary)
    plot_sales_chart(chart_data, show=True)
