


def get_withdraw_fee(symbol, df_all_symbol_info):
    df = df_all_symbol_info
    if symbol in df["symbol"].values:
        return df[df["symbol"] == symbol]["withdraw_fee"].iloc[0]
    else:
        return 0

def include_withdraw_fee(df_in, symbol_col, df_all_symbol_info):
    df = df_in.copy()
    df["withdraw_fee"] = df.apply(lambda row: get_withdraw_fee(row[symbol_col], df_all_symbol_info), axis=1)
    return df


def calculate_quantity_for_arbitrage(min_price, max_price, withdrawal_fee):
    """
    Calculate the quantity of cryptocurrency for arbitrage.

    :param min_price: The lower price of the cryptocurrency on one exchange.
    :param max_price: The higher price of the cryptocurrency on another exchange.
    :param withdrawal_fee: The network withdrawal fee for the cryptocurrency.
    :return: The quantity of cryptocurrency for arbitrage.
    """
    transaction_fee_rate = 0.001  # 0.1% flat rate

    # Solve for q(A) from the arbitrage equation
    try:
        quantity = withdrawal_fee / ((max_price * (1 - transaction_fee_rate)) - (min_price * (1 + transaction_fee_rate)))
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


def calculate_executable_quantity(order_book_buy, order_book_sell, desired_quantity):
    """
    Calculate the executable quantity for arbitrage based on the order book volumes.

    :param order_book_buy: List of (price, volume) tuples for the buy side, sorted by increasing price.
    :param order_book_sell: List of (price, volume) tuples for the sell side, sorted by decreasing price.
    :param desired_quantity: The desired quantity for arbitrage.
    :return: The executable quantity, adjusted buy price, and adjusted sell price.
    """
    # Function to calculate cumulative volume and price
    def match_order_book(order_book, target_quantity):
        cumulative_volume = 0
        for price, volume in order_book:
            cumulative_volume += volume
            if cumulative_volume >= target_quantity:
                return min(cumulative_volume, target_quantity), price
        return cumulative_volume, None

    # Match against the buy side order book
    buy_quantity, buy_price = match_order_book(order_book_buy, desired_quantity)

    # Match against the sell side order book
    sell_quantity, sell_price = match_order_book(order_book_sell, desired_quantity)

    # Adjust quantity based on the lesser of buy and sell quantities
    executable_quantity = min(buy_quantity, sell_quantity)

    return executable_quantity, buy_price, sell_price

# Example usage
# # Assuming order_book_buy and order_book_sell are provided for a symbol
# desired_quantity = calculate_quantity_for_arbitrage(min_price, max_price, withdrawal_fee)
# executable_quantity, adjusted_buy_price, adjusted_sell_price = calculate_executable_quantity(order_book_buy, order_book_sell, desired_quantity)
# print("Executable quantity:", executable_quantity)
# print("Adjusted Buy Price:", adjusted_buy_price)
# print("Adjusted Sell Price:", adjusted_sell_price)
#
def evaluate_arbitrage_opportunity(symbol, order_book_df, withdrawal_fee):
    """
    Evaluate arbitrage opportunities for a given symbol using order book data.

    :param symbol: The cryptocurrency symbol to evaluate.
    :param order_book_df: DataFrame containing order book data with columns price_col, volume_col, num_orders, symbol_col, exchange_name_col.
    :param withdrawal_fee: The withdrawal fee for the cryptocurrency.
    :return: A dictionary with evaluated arbitrage information for the symbol.
    """
    # Split the order book DataFrame into buy and sell sides based on exchange names or other criteria
    order_book_buy = order_book_df[...].to_records(index=False).tolist()  # Define criteria to filter buy side
    order_book_sell = order_book_df[...].to_records(index=False).tolist()  # Define criteria to filter sell side

    # Get min and max prices for the buy and sell sides
    min_price = min(order_book_df['price_col'])  # Assuming lowest price for buying
    max_price = max(order_book_df['price_col'])  # Assuming highest price for selling

    # Calculate theoretical quantity for arbitrage
    theoretical_quantity = calculate_quantity_for_arbitrage(min_price, max_price, withdrawal_fee)

    # Calculate executable quantity based on order book volumes
    executable_quantity, adjusted_buy_price, adjusted_sell_price = calculate_executable_quantity(order_book_buy, order_book_sell, theoretical_quantity)

    # Calculate expected net profit (considering only one symbol here, so no need for ranking function)
    gross_profit = (adjusted_sell_price - adjusted_buy_price) * executable_quantity
    total_fees = adjusted_buy_price * executable_quantity * 0.001 + adjusted_sell_price * executable_quantity * 0.001 + withdrawal_fee
    net_profit = gross_profit - total_fees

    return {
        'symbol': symbol,
        'theoretical_quantity': theoretical_quantity,
        'executable_quantity': executable_quantity,
        'adjusted_buy_price': adjusted_buy_price,
        'adjusted_sell_price': adjusted_sell_price,
        'net_profit': net_profit
    }

# Example usage
# Assuming order_book_df is provided for a symbol 'A'
symbol_info = evaluate_arbitrage_opportunity('A', order_book_df, withdrawal_fee)
print(symbol_info)


def rank_symbols_for_arbitrage(symbols, quantities, buy_prices, sell_prices, withdrawal_fees, transaction_fee_rate=0.001):
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
symbols = ["BTC", "ETH", "LTC"]  # Example symbols
quantities = [0.5, 1.0, 0.75]  # Example quantities
buy_prices = [10000, 2000, 150]  # Example buy prices
sell_prices = [10100, 2050, 155]  # Example sell prices
withdrawal_fees = [5, 10, 2]  # Example withdrawal fees
ranked_symbols = rank_symbols_for_arbitrage(symbols, quantities, buy_prices, sell_prices, withdrawal_fees)
print("Ranked symbols for arbitrage:", ranked_symbols)

