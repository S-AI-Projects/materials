prices = [1.09, 23.56, 57.84, 4.56, 6.78]
TAX_RATE = 0.08


# One call performs a fixed number of arithmetic operations: O(1).
# Mapping n prices takes O(n) time; materializing the results uses O(n) space.
def get_price_with_tax(price):
    return price * (1 + TAX_RATE)


final_prices = map(get_price_with_tax, prices)
print(list(final_prices))
