def calculate_liquidity_from_order_book_depth(order_book, price_range_percent=2):
    """
    Calculate liquidity based on the order book depth.

    :param order_book: A DataFrame with columns 'price', 'volume', and 'side' (buy/sell).
    :param price_range_percent: The percentage range around the current market price to consider.
    :return: Liquidity as the total volume within the price range.
    """
    mid_price = (order_book[order_book['side'] == 'sell']['price'].min() +
                 order_book[order_book['side'] == 'buy']['price'].max()) / 2
    lower_bound = mid_price * (1 - price_range_percent / 100)
    upper_bound = mid_price * (1 + price_range_percent / 100)

    liquidity = order_book[(order_book['price'] >= lower_bound) &
                           (order_book['price'] <= upper_bound)]['volume'].sum()

    return liquidity

