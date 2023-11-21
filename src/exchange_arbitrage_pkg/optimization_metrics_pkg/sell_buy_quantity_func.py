import pandas as pd


def calculate_historical_difference(price_series):
    """
    Calculate historical price difference percentage based on the middle 70 percentiles.

    :param price_series: Series containing historical price data.
    :return: Historical price difference percentage.
    """
    # Calculate the percentiles for the price series
    lower_percentile = 0.15
    upper_percentile = 0.85

    # Get prices within the middle 70 percentiles
    price_percentiles = price_series.quantile([lower_percentile, upper_percentile])

    # Filter prices within the specified percentiles
    prices_within_percentiles = price_series[
        (price_series >= price_percentiles[lower_percentile]) &
        (price_series <= price_percentiles[upper_percentile])
    ]

    # Calculate the mean of the prices within the middle 70 percentiles
    mean_price_within_percentiles = prices_within_percentiles.mean() * 100  # Multiply by 100 to get percentage

    return mean_price_within_percentiles


def get_reasonable_max_price(price_series, reasonable_mean_change):
    """
    Get the maximum price within a series with reasonable price changes.

    :param price_series: Series containing historical price data.
    :return: Reasonable maximum price.
    """
    mean_of_changes_factor = 3
    mean_of_changes_coef = reasonable_mean_change * mean_of_changes_factor

    # Filter prices where the difference with the previous price is reasonable
    reasonable_prices = price_series[price_series.diff() <= mean_of_changes_coef]

    # Get the maximum price among the filtered reasonable prices
    reasonable_max_price = reasonable_prices.max()

    return reasonable_max_price


def calculate_slippage_for_sell_orders(sell_orders):
    # Calculate historical difference or slippage for sell orders

    historical_difference_for_sell = calculate_historical_difference(sell_orders)
    reasonable_max_price = get_reasonable_max_price(sell_orders, historical_difference_for_sell / 100)
    # Use historical_difference_for_sell for slippage estimation specifically for sell orders

    return historical_difference_for_sell, reasonable_max_price


def calculate_max_sell_quantity(order_book_in, slippage_factor):
    order_book = order_book_in.copy()
    order_book['price'] = pd.to_numeric(order_book['price'], errors='coerce')
    sell_orders = order_book[order_book['side'] == 'sell']['price']
    # Calculate slippage specifically for sell orders
    hist_diff_sell, reasonable_max_price = calculate_slippage_for_sell_orders(sell_orders)

    # Rest of your calculation using historical_difference_for_sell
    acceptable_slippage = slippage_factor * hist_diff_sell
    acceptable_price = reasonable_max_price * (1 - acceptable_slippage / 100)

    filtered_sell_orders = order_book[(order_book['side'] == 'sell') &
                                      (order_book['price'] >= acceptable_price)]
    cumulative_volume = filtered_sell_orders['volume'].sum()
    return max(cumulative_volume, 0)


def get_max_sell_qty_by_diff(order_book, min_price, slippage_factor):
    order_book = order_book.copy()
    order_book['price'] = pd.to_numeric(order_book['price'], errors='coerce')

    # Calculate slippage specifically for sell orders
    hist_diff_sell, reasonable_max_price = calculate_slippage_for_sell_orders(order_book['price'])

    # Rest of your calculation using historical_difference_for_sell
    acceptable_slippage = slippage_factor * hist_diff_sell
    if min_price is None:
        min_price = reasonable_max_price
    acceptable_price = min_price * (1 - acceptable_slippage / 100)

    # Filter buy orders below the acceptable price (considering it's for selling)
    order_book_buy = order_book[order_book['side'] == 'buy']
    filtered_buy_orders = order_book_buy[order_book_buy['price'] <= acceptable_price]

    cumulative_volume = filtered_buy_orders['volume'].sum()

    return max(cumulative_volume, 0)


def get_reasonable_min_price(price_series, reasonable_mean_change):
    """
    Get the maximum price within a series with reasonable price changes.

    :param price_series: Series containing historical price data.
    :return: Reasonable maximum price.
    """
    mean_of_changes_factor = 3
    mean_of_changes_coef = reasonable_mean_change * mean_of_changes_factor

    # Filter prices where the difference with the previous price is reasonable
    reasonable_prices = price_series[price_series.diff() <= mean_of_changes_coef]

    # Get the maximum price among the filtered reasonable prices
    reasonable_min_price = reasonable_prices.min()

    return reasonable_min_price


def calculate_slippage_for_buy_orders(buy_orders):
    # Calculate historical difference or slippage for buy orders

    historical_difference_for_buy = calculate_historical_difference(buy_orders)
    reasonable_min_price = get_reasonable_min_price(buy_orders, historical_difference_for_buy / 100)
    # Use historical_difference_for_buy for slippage estimation specifically for buy orders

    return historical_difference_for_buy, reasonable_min_price


def calculate_max_buy_quantity(order_book, max_price, slippage_factor):
    order_book = order_book.copy()
    order_book['price'] = pd.to_numeric(order_book['price'], errors='coerce')

    # Calculate slippage specifically for buy orders
    hist_diff_buy, reasonable_min_price = calculate_slippage_for_buy_orders(order_book['price'])

    # Rest of your calculation using historical_difference_for_buy
    acceptable_slippage = slippage_factor * hist_diff_buy
    if max_price is None:
        max_price = reasonable_min_price
    acceptable_price = max_price * (1 + acceptable_slippage / 100)

    # Filter buy orders below the acceptable price
    order_book_buy = order_book[order_book['side'] == 'buy']
    filtered_buy_orders = order_book_buy[order_book_buy['price'] <= acceptable_price]

    cumulative_volume = filtered_buy_orders['volume'].sum()

    return max(cumulative_volume, 0)

