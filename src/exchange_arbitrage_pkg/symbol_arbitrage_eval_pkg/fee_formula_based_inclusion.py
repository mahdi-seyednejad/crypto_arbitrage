def get_withdraw_fee(symbol, symbol_col, df_all_symbol_info, withdraw_fee_col):
    df = df_all_symbol_info
    if symbol in df[symbol_col].values:
        return df[df[symbol_col] == symbol]["withdraw_fee"].iloc[0]
    else:
        return 0


def include_withdraw_fee(df_in, symbol_col, df_all_symbol_info, withdraw_fee_col):
    df = df_in.copy()
    df[withdraw_fee_col] = df.apply(lambda row:
                                    get_withdraw_fee(symbol=row[symbol_col],
                                                     symbol_col=symbol_col,
                                                     df_all_symbol_info=df_all_symbol_info,
                                                     withdraw_fee_col=withdraw_fee_col), axis=1)
    return df


def calculate_quantity_for_arbitrage(src_price, dst_price, withdrawal_fee, transaction_fee_rate):
    """
    Calculate the quantity of cryptocurrency for arbitrage.

    :param src_price: The lower price of the cryptocurrency on one exchange.
    :param dst_price: The higher price of the cryptocurrency on another exchange.
    :param withdrawal_fee: The network withdrawal fee for the cryptocurrency.
    :return: The quantity of cryptocurrency for arbitrage.
    """
    # transaction_fee_rate = 0.001  # 0.1% flat rate
    # Solve for q(A) from the arbitrage equation
    try:  # It is wrong!!!!!!!!!!!!!!!
        quantity = withdrawal_fee / (
                (dst_price * (1 - transaction_fee_rate)) - (src_price * (1 + transaction_fee_rate)))
        return max(quantity, 0)  # Ensure that the quantity is not negative
    except ZeroDivisionError:
        return 0  # Return 0 if division by zero occurs (indicates no profitable arbitrage)


# # Example usage
# min_price = 100  # Example minimum price
# max_price = 105  # Example maximum price
# withdrawal_fee = 1  # Example withdrawal fee
# quantity = calculate_quantity_for_arbitrage(min_price, max_price, withdrawal_fee)
# print("Quantity for arbitrage:", quantity)


# def rank_symbols_for_arbitrage(order_books_low, order_books_high, current_prices_low, current_prices_high, price_diff_percentages):
#     """
#     Rank symbols based on their potential profitability for arbitrage.
#
#     :param order_books_low: Dictionary of order books on the lower-priced exchange, keyed by symbol.
#     :param order_books_high: Dictionary of order books on the higher-priced exchange, keyed by symbol.
#     :param current_prices_low: Dictionary of current prices on the lower-priced exchange, keyed by symbol.
#     :param current_prices_high: Dictionary of current prices on the higher-priced exchange, keyed by symbol.
#     :param price_diff_percentages: Dictionary of price difference percentages, keyed by symbol.
#     :return: A sorted list of symbols based on their arbitrage profitability potential.
#     """
#     profitability_scores = {}
#
#     for symbol in order_books_low:
#         # Assuming the withdrawal fee is known for each symbol
#         withdrawal_fee = get_withdrawal_fee(symbol)  # Placeholder function to get withdrawal fee
#
#         # Calculate the potential quantity for arbitrage
#         quantity = calculate_quantity_for_arbitrage(current_prices_low[symbol], current_prices_high[symbol], withdrawal_fee)
#
#         # Estimate potential profit
#         potential_profit = (current_prices_high[symbol] - current_prices_low[symbol]) * quantity - withdrawal_fee
#
#         # Score each symbol based on potential profit and price difference percentage
#         profitability_scores[symbol] = potential_profit * price_diff_percentages[symbol]
#
#     # Sort symbols by their profitability score
#     ranked_symbols = sorted(profitability_scores, key=profitability_scores.get, reverse=True)
#
#     return ranked_symbols

# Example usage
# # You would need to provide the actual order book data, current prices, and price differences for each symbol
# ranked_symbols = rank_symbols_for_arbitrage(orb_low, orb_high, current_prices_low, current_prices_high, price_diff_percentages)
# print("Ranked symbols for arbitrage:", ranked_symbols)

def match_order_book(order_book, target_quantity):
    cumulative_volume = 0
    for price, volume in order_book:
        cumulative_volume += volume
        if cumulative_volume >= target_quantity:
            return min(cumulative_volume, target_quantity), price
    return cumulative_volume, None


def calculate_executable_quantity(order_book_src_buy, order_book_dst_sell, desired_quantity):
    """
    Calculate the executable quantity for arbitrage based on the order book volumes.

    :param order_book_src_buy: List of (price, volume) tuples for the buy side, sorted by increasing price.
    :param order_book_dst_sell: List of (price, volume) tuples for the sell side, sorted by decreasing price.
    :param desired_quantity: The desired quantity for arbitrage.
    :return: The executable quantity, adjusted buy price, and adjusted sell price.
    """
    # Match against the buy side order book
    buy_quantity, buy_price = match_order_book(order_book_src_buy, desired_quantity)

    # Match against the sell side order book
    sell_quantity, sell_price = match_order_book(order_book_dst_sell, desired_quantity)

    # Adjust quantity based on the lesser of buy and sell quantities
    executable_quantity = min(buy_quantity, sell_quantity)

    return executable_quantity, buy_price, sell_price


def evaluate_arbitrage_opportunity(symbol,
                                   order_book_df,
                                   withdrawal_fee,
                                   src_exchange_name,
                                   dst_exchange_name,
                                   transaction_fee_rate=0.001,
                                   price_col='price',
                                   volume_col='volume',
                                   side_col='side',
                                   exchange_name_col='exchange_name'):
    """
    Evaluate arbitrage opportunities for a given symbol using order book data.
    :param symbol: The cryptocurrency symbol to evaluate.
    :param order_book_df: DataFrame containing order book data.
    :param withdrawal_fee: The withdrawal fee for the cryptocurrency.
    :param src_exchange_name: The name of the source exchange (where to buy).
    :param dst_exchange_name: The name of the destination exchange (where to sell).
    :param transaction_fee_rate: The percentage of the trade that will be taken by exchange as fee
    :type transaction_fee_rate: float
    :param price_col: Column name for price.
    :param volume_col: Column name for volume.
    :param side_col: Column name for side (buy/sell).
    :param exchange_name_col: Column name for exchange name.
    :return: A dictionary with evaluated arbitrage information for the symbol.
    """
    # Filter the DataFrame for the buy side on the source exchange
    order_book_src_df = order_book_df[order_book_df[exchange_name_col] == src_exchange_name]
    order_book_src_df_buy = order_book_src_df[order_book_src_df[side_col] == 'buy']
    order_book_src_df_sell = order_book_src_df[order_book_src_df[side_col] == 'sell']
    order_book_src_buy = order_book_src_df_buy[[price_col, volume_col]].to_records(index=False).tolist()
    src_price = min(order_book_src_df_sell[price_col])

    # Filter the DataFrame for the sell side on the destination exchange
    order_book_dst_df = order_book_df[order_book_df[exchange_name_col] == dst_exchange_name]
    # order_book_dst_df_buy = order_book_dst_df[order_book_dst_df[side_col] == 'buy']
    order_book_dst_df_sell = order_book_dst_df[order_book_dst_df[side_col] == 'sell']
    order_book_dst_sell = order_book_dst_df_sell[[price_col, volume_col]].to_records(index=False).tolist()
    dst_price = min(order_book_dst_df_sell[price_col])

    # Calculate theoretical quantity for arbitrage
    theoretical_quantity = calculate_quantity_for_arbitrage(src_price=src_price,
                                                            dst_price=dst_price,
                                                            withdrawal_fee=withdrawal_fee,
                                                            transaction_fee_rate=transaction_fee_rate)

    # Calculate executable quantity based on order book volumes
    executable_quantity, adjusted_buy_price, \
        adjusted_sell_price = calculate_executable_quantity(order_book_src_buy,
                                                            order_book_dst_sell,
                                                            theoretical_quantity)

    # Calculate expected net profit
    gross_profit = (adjusted_sell_price - adjusted_buy_price) * executable_quantity
    total_fees = adjusted_buy_price * executable_quantity * 0.001 + \
                 adjusted_sell_price * executable_quantity * 0.001 + \
                 withdrawal_fee
    net_profit = gross_profit - total_fees

    return {
        'symbol': symbol,
        'theoretical_quantity': theoretical_quantity,
        'executable_quantity': executable_quantity,
        'adjusted_buy_price': adjusted_buy_price,
        'adjusted_sell_price': adjusted_sell_price,
        'net_profit': net_profit
    }


def rank_symbols_for_arbitrage(symbols, quantities, buy_prices, sell_prices, withdrawal_fees,
                               transaction_fee_rate=0.001):
    """
    Rank symbols based on expected net profit from arbitrage.

    :param symbols: List of cryptocurrency symbols.
    :param quantities: List of realistic quantities for each symbol.
    :param buy_prices: List of buy prices for each symbol.
    :param sell_prices: List of sell prices for each symbol.
    :param withdrawal_fees: List of withdrawal fees for each symbol.
    :param transaction_fee_rate: Transaction fee rate (default to 0.1%).
    :return: Sorted list of symbols based on expected net profit.
    """
    profits = []

    for i, symbol in enumerate(symbols):
        # Calculate gross profit
        gross_profit = (sell_prices[i] - buy_prices[i]) * quantities[i]

        # Calculate total fees
        total_fees = buy_prices[i] * quantities[i] * transaction_fee_rate + \
                     sell_prices[i] * quantities[i] * transaction_fee_rate + \
                     withdrawal_fees[i]

        # Calculate net profit
        net_profit = gross_profit - total_fees

        profits.append((symbol, net_profit))

    # Sort symbols by net profit
    ranked_symbols = sorted(profits, key=lambda x: x[1], reverse=True)

    return [symbol for symbol, profit in ranked_symbols]


# Example usage
# symbols = ["BTC", "ETH", "LTC"]  # Example symbols
# quantities = [0.5, 1.0, 0.75]  # Example quantities
# buy_prices = [10000, 2000, 150]  # Example buy prices
# sell_prices = [10100, 2050, 155]  # Example sell prices
# withdrawal_fees = [5, 10, 2]  # Example withdrawal fees
# ranked_symbols = rank_symbols_for_arbitrage(symbols, quantities, buy_prices, sell_prices, withdrawal_fees)
# print("Ranked symbols for arbitrage:", ranked_symbols)


def calculate_symbol_profit_old(order_book_df,
                            withdrawal_fee,
                            src_exchange_name,
                            dst_exchange_name,
                            transaction_fee_rate=0.001,
                            price_col='price',
                            volume_col='volume',
                            side_col='side',
                            exchange_name_col='exchange_name'):
    order_book_src_df = order_book_df[order_book_df[exchange_name_col] == src_exchange_name]
    # order_book_src_df_buy = order_book_src_df[order_book_src_df[side_col] == 'buy']
    order_book_src_df_sell = order_book_src_df[order_book_src_df[side_col] == 'sell']
    orbk_src_sell_tuples = order_book_src_df_sell[[price_col, volume_col]].to_records(index=False).tolist()

    order_book_dst_df = order_book_df[order_book_df[exchange_name_col] == dst_exchange_name]
    order_book_dst_df_buy = order_book_dst_df[order_book_dst_df[side_col] == 'buy']
    orbk_dst_buy_tuples = order_book_dst_df_buy[[price_col, volume_col]].to_records(index=False).tolist()

    total_volume, net_profit = calculate_arbitrage(order_book_sell_src=orbk_src_sell_tuples,
                                                  order_book_buy_dst=orbk_dst_buy_tuples,
                                                  withdrawal_fee=withdrawal_fee,
                                                  transaction_fee_rate=transaction_fee_rate)
    return total_volume, net_profit


def calculate_profit_old(buy_price, sell_price, volume, withdrawal_fee, transaction_fee_rate):
    total_buy_cost = buy_price * volume * (1 + transaction_fee_rate)
    total_sell_revenue = sell_price * volume * (1 - transaction_fee_rate)
    return total_sell_revenue - total_buy_cost - withdrawal_fee


def calculate_arbitrage(order_book_sell_src, order_book_buy_dst, transaction_fee_rate, withdrawal_fee):
    total_profit = 0
    total_volume = 0

    # Sorting the destination buy order book in descending order of price
    order_book_buy_dst.sort(key=lambda x: x[0], reverse=True)

    # Iterating through the source sell orders
    for src_price, src_volume in order_book_sell_src:
        for dst_price, dst_volume in order_book_buy_dst:
            if dst_price > src_price and src_volume > 0 and dst_volume > 0:
                executable_volume = min(src_volume, dst_volume)

                # Calculate profit for this transaction
                buy_cost = src_price * executable_volume * (1 + transaction_fee_rate)
                sell_revenue = dst_price * executable_volume * (1 - transaction_fee_rate)
                profit = sell_revenue - buy_cost

                # If the transaction is profitable, update the totals
                if profit > 0:
                    total_profit += profit
                    total_volume += executable_volume

                    # Update remaining volumes for source and destination
                    src_volume -= executable_volume
                    dst_volume -= executable_volume

                    # Update the destination order book with the new remaining volume
                    order_book_buy_dst = [(price, vol - executable_volume if price == dst_price else vol) for price, vol in order_book_buy_dst]

                # If no more volume is left in the source, break the inner loop
                if src_volume <= 0:
                    break

    # Subtract withdrawal fees from total profit only once
    net_profit = total_profit - withdrawal_fee

    return total_volume, net_profit


# # Sample order book data
# order_book_src = [(10000, 2), (10050, 1.5)]  # (price, volume) tuples
# order_book_dst = [(10200, 0.5), (10100, 5)]  # (price, volume) tuples
# withdrawal_fee = 0.1
#
# # Calculate optimized arbitrage profit
# optimized_profit = calculate_optimized_arbitrage(order_book_src, order_book_dst, withdrawal_fee)
# print(f"Optimized Arbitrage Profit: {optimized_profit}")
