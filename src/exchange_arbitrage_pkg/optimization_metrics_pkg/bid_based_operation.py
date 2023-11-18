def calculate_bid_ask_spread(order_book):
    """
    Calculate the bid-ask spread from the order book.

    :param order_book: A DataFrame with columns 'price', 'volume', and 'side' (buy/sell).
    :return: The bid-ask spread.
    """
    highest_bid = order_book[order_book['side'] == 'buy']['price'].max()
    lowest_ask = order_book[order_book['side'] == 'sell']['price'].min()

    bid_ask_spread = lowest_ask - highest_bid
    return bid_ask_spread

