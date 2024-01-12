"""
Quantity Notes:
For buys, quantity is the amount you want to purchase.
For sells of assets you own, it's the amount you want to sell from your account balance.
For short sells, it's the amount you want to short.
The quantity is always specified in the base asset unit (like BTC, ETH, etc)
"""


def calculate_quantity(row,
                       quantity_col,
                       price_cols,
                       budget):
    """
    This function calculates the quantity of the symbol to be traded on the exchange.
    """
    # max_trade_qty_col = col_info_obj.symbol_eval_col_obj.max_trade_qty_col
    # price_cols = [val for key, val in col_info_obj.exchange_price_cols.items()]
    # ToDo: the quantity should be fixed here.

    max_price = max([row[col] for col in price_cols])

    budget_qty = budget / max_price
    quantity = min(row[quantity_col], budget_qty)
    return quantity


def calculate_quantity_new(row,
                           quantity_col,
                           ex_price_col,
                           withdraw_fee_col,
                           min_acceptable_profit,
                           ex_budget):
    ex_price = row[ex_price_col]
    max_profitable_trading_volume = row[quantity_col]
    withdraw_fee = row[withdraw_fee_col]
    if (withdraw_fee * ex_price) + min_acceptable_profit > ex_budget:
        return 0
    else:
        max_possible_trading_volume = ex_budget / ex_price
        return min(max_profitable_trading_volume, max_possible_trading_volume)


def calculate_quantity_new_2(max_profitable_trading_volume,
                             ex_price,
                             withdraw_fee,
                             min_acceptable_profit,
                             ex_budget):
    if (withdraw_fee * ex_price) + min_acceptable_profit > ex_budget:
        return 0
    else:
        max_possible_trading_volume = ex_budget / ex_price
        return min(max_profitable_trading_volume, max_possible_trading_volume)
