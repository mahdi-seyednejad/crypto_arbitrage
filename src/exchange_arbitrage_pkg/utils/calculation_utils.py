def calc_absolute_percentage_diff_2_values(val1, val2):
    smaller_price = min(val1, val2)
    price_difference = abs(val1 - val2)
    if smaller_price != 0:
        result = (price_difference / smaller_price) * 100
        return result
    else:
        return None  # or 0, depending on how you want to handle division by zero

