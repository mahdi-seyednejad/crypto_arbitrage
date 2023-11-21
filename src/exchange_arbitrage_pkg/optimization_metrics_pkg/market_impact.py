
def calculate_market_impact(order_book, sell_amount):
    """
    Calculate the market impact of selling a cryptocurrency using DataFrame operations.
    :param order_book: A DataFrame containing 'price' and 'volume' of buy orders.
    :param sell_amount: Amount of cryptocurrency to sell.
    :return: Estimated price impact in percentage.
    """
    # Create a new column in the DataFrame for the trade volume
    order_book['trade_volume'] = order_book['volume'].apply(lambda x: min(x, sell_amount))
    order_book['trade_cost'] = order_book['trade_volume'] * order_book['price']

    # Update the sell amount after each trade
    order_book['sell_amount_remaining'] = sell_amount - order_book['trade_volume'].cumsum()
    order_book = order_book[order_book['sell_amount_remaining'] > 0]
    if order_book.empty:
        return None  # Return a default value when order_book is empty

    # Calculate total trade volume and cost
    total_volume = order_book['trade_volume'].sum()
    total_cost = order_book['trade_cost'].sum()

    # Calculate average executed price and price impact
    average_executed_price = total_cost / total_volume
    original_price = order_book.iloc[0]['price']
    price_impact = ((original_price - average_executed_price) / original_price) * 100

    return price_impact

#
# def calculate_market_impact_2(order_book, sell_amount):
#     """
#     Calculate the market impact of selling a cryptocurrency using DataFrame operations.
#
#     :param sell_amount: Amount of cryptocurrency to sell.
#     :param order_book: A DataFrame containing 'price' and 'volume' of buy orders.
#     :return: Estimated price impact in percentage.
#     """
#     # Calculate the cumulative volume and the cumulative cost
#     order_book['trade_volume'] = order_book['volume'].cummin(sell_amount)
#     order_book['trade_cost'] = order_book['trade_volume'] * order_book['price']
#
#     # Sum up the total volume and total cost
#     total_volume = order_book['trade_volume'].sum()
#     total_cost = order_book['trade_cost'].sum()
#
#     # Calculate the average executed price and price impact
#     average_executed_price = total_cost / total_volume
#     original_price = order_book.iloc[0]['price']
#     price_impact = ((original_price - average_executed_price) / original_price) * 100
#
#     return price_impact
