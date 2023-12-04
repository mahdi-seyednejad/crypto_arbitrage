"""
Quantity Notes:
For buys, quantity is the amount you want to purchase.
For sells of assets you own, it's the amount you want to sell from your account balance.
For short sells, it's the amount you want to short.
The quantity is always specified in the base asset unit (like BTC, ETH, etc)
"""


def calculate_quantity(row,
                       max_trade_qty_col,
                       price_cols,
                       budget):
    """
    This function calculates the quantity of the symbol to be traded on the exchange.
    """
    # max_trade_qty_col = col_info_obj.symbol_eval_col_obj.max_trade_qty_col
    # price_cols = [val for key, val in col_info_obj.exchange_price_cols.items()]

    max_price = max([row[col] for col in price_cols])

    budget_qty = budget / max_price
    quantity = min(row[max_trade_qty_col], budget_qty)
    return quantity

# def calculate_quantity(row,
#                        col_info_obj: ColumnInfoClass,
#                        budget):
#     """
#     This function calculates the quantity of the symbol to be traded on the exchange.
#     """
#     max_trade_qty_col = col_info_obj.symbol_eval_col_obj.max_trade_qty_col
#     price_cols = [val for key, val in col_info_obj.exchange_price_cols.items()]
#
#     max_price = max([row[col] for col in price_cols])
#
#     budget_qty = budget / max_price
#     quantity = min(row[max_trade_qty_col], budget_qty)
#     return quantity
