
def calculate_max_sell_quantity(order_book, acceptable_slippage):
    """
    Calculate the maximum quantity of a crypto that can be sold without exceeding the acceptable slippage.

    :param order_book: A DataFrame with 'price' and 'volume' of buy orders (bids).
    :param acceptable_slippage: The maximum acceptable price impact in percentage (e.g., 0.5 for 0.5%).
    :return: The maximum sell quantity.
    """
    highest_bid = order_book['price'].max()
    acceptable_price = highest_bid * (1 - acceptable_slippage / 100)

    cumulative_volume = 0
    for index, row in order_book.iterrows():
        if row['price'] < acceptable_price:
            break
        cumulative_volume += row['volume']

    return cumulative_volume

