# %%
try:
    import pandas as pd
except ImportError:
    pd = None


def calculate_cumulative_income(products):
    """Calculate cumulative income using row iteration.

    Source fixture anchor:
    - Line 7: cumulative_sum = []

    Preconditions:
    - Line 9: products is an iterable of row tuples or objects providing .sales and .unit_price.
    - Line 10: income = product.sales * product.unit_price
    - Lines 11-14:
        if cumulative_sum:
            cumulative_sum.append(cumulative_sum[-1] + income)
        else:
            cumulative_sum.append(income)

    Failure & Empty-Result Paths:
    - Empty Input Branch (Line 9): When products is empty (0 rows), the loop does not run.
      Returns [] as the valid empty/missing-result branch without error.
    - Failure Branch (Line 10): If any item lacks 'sales' or 'unit_price', an AttributeError
      is raised immediately, leaving caller state unmutated.
    """
    cumulative_sum = []

    it = products.itertuples() if hasattr(products, "itertuples") else iter(products)
    for product in it:
        if not hasattr(product, "sales") or not hasattr(product, "unit_price"):
            raise AttributeError("Row object missing required 'sales' or 'unit_price' attribute")
        income = product.sales * product.unit_price
        if cumulative_sum:
            cumulative_sum.append(cumulative_sum[-1] + income)
        else:
            cumulative_sum.append(income)

    return cumulative_sum


def main():
    if pd is None:
        raise RuntimeError("pandas is required to execute main with CSV files")
    # %% Get the cumulative sum with .itertuples()
    products = pd.read_csv("resources/products.csv")
    cumulative_sum = calculate_cumulative_income(products)
    products = products.assign(cumulative_income=cumulative_sum)
    return products


if __name__ == "__main__":
    main()
