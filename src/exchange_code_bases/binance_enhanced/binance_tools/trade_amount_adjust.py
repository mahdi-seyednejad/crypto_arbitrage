# import decimal
#
#
# class BinanceAmountAdjusterSync:
#     def __init__(self, client):
#         self.client = client
#
#     def adjust_sell_amount(self, symbol, quantity):
#         symb_info = self.client.get_symbol_info(symbol)
#         if symb_info is None:
#             raise ValueError(f"No symbol information available for {symbol}")
#
#         return self.apply_market_lot_size_sell(symb_info, quantity)
#
#     def calculate_and_adjust_buy_amount(self, symbol, price, remaining_budget, invest_portion, crypto_weight):
#         symb_info = self.client.get_symbol_info(symbol)
#         if symb_info is None:
#             raise ValueError(f"No symbol information available for {symbol}")
#
#         avail_money = remaining_budget * invest_portion * crypto_weight
#         money_to_buy = self.apply_price_filter(symb_info, avail_money)
#         if money_to_buy < 0:
#             return 0
#
#         proposed_quant = money_to_buy / float(price)
#         return self.apply_market_lot_size_buy(symb_info, proposed_quant)
#
#     def adjust_buy_amount(self, symbol, quantity, symb_info=None):
#         if symb_info is None:
#             symb_info = self.client.get_symbol_info(symbol)
#         if symb_info is None:
#             raise ValueError(f"No symbol information available for {symbol}")
#
#         return self.apply_market_lot_size_buy(symb_info, quantity)
#
#     def apply_price_filter(self, symb_info, avail_money):
#         res_dict = self.search_dict(symb_info["filters"], "filterType", "PRICE_FILTER")
#         money_to_buy = min(float(res_dict["tickSize"]), avail_money)
#         if avail_money < money_to_buy:
#             return -1
#         else:
#             return money_to_buy
#
#     def apply_market_lot_size_buy(self, symb_info, proposed_quant):
#         res_dict = self.search_dict(symb_info["filters"], "filterType", "MARKET_LOT_SIZE")
#         max_quant = float(res_dict['maxQty'])
#         quant_mx = min(proposed_quant, max_quant)
#
#         min_quant = float(res_dict['minQty'])
#         quantity = max(quant_mx, min_quant)
#
#         step_size = float(res_dict["stepSize"])
#         if (step_size == 0) or ((quantity % step_size) == 0):
#             return quantity
#         else:
#             d = decimal.Decimal(str(step_size))
#             decimal_n = abs(d.as_tuple().exponent)
#             return round(quantity, decimal_n)
#
#     def apply_market_lot_size_sell(self, symb_info, proposed_quant):
#         res_dict = self.search_dict(symb_info["filters"], "filterType", "LOT_SIZE")
#         max_quant = float(res_dict['maxQty'])
#         quant_mx = min(proposed_quant, max_quant)
#
#         min_quant = float(res_dict['minQty'])
#         quantity = max(quant_mx, min_quant)
#
#         step_size = float(res_dict["stepSize"])
#         if (step_size == 0) or ((quantity % step_size) == 0):
#             return quantity
#         else:
#             d = decimal.Decimal(str(step_size))
#             decimal_n = abs(d.as_tuple().exponent)
#             return round(quantity, decimal_n)
#
#     def search_dict(self, list_of_dicts, key, value):
#         for d in list_of_dicts:
#             if d[key] == value:
#                 return d
#         return {}
#
#
#
# #
# # import warnings
# #
# #
# # async def get_trade_details(client, symbol):
# #     info = await client.get_symbol_info(symbol)
# #     if info:
# #         precision = info['baseAssetPrecision']
# #         min_amount = info['filters'][2]['minQty']
# #         min_notional = info['filters'][3]['minNotional']
# #         return precision, min_amount, min_notional
# #     return None, None, None
# #
# #
# # def adjust_buy_amount(amount, price, precision, min_amount, min_notional):
# #     adjusted_amount = round(amount, precision)
# #     if adjusted_amount < float(min_amount):
# #         warnings.warn("Amount is below the minimum buy amount, adjusting to minimum.")
# #         return float(min_amount)
# #     if adjusted_amount * price < float(min_notional):
# #         warnings.warn("Trade value is below the minimum notional value, adjusting to minimum.")
# #         return round(float(min_notional) / price, precision)
# #     return adjusted_amount
# #
# #
# # def adjust_sell_amount(amount, precision, min_amount, min_notional):
# #     adjusted_amount = round(amount, precision)
# #     if adjusted_amount < float(min_amount):
# #         warnings.warn("Amount is below the minimum sell amount, adjusting to minimum.")
# #         return float(min_amount)
# #     # Note: You might need additional logic here for min notional in sell orders
# #     return adjusted_amount
# #
# #
# # # Main function
# # async def get_adjusted_trade_amount(client, symbol, amount, side):
# #     ticker = await client.get_symbol_ticker(symbol=symbol)
# #     price = float(ticker['price'])
# #     precision, min_amount, min_notional = await get_trade_details(client, symbol)
# #
# #     if precision is None:
# #         raise ValueError(f"Could not fetch trade details for {symbol}")
# #
# #     if side == 'buy':
# #         adjusted_quantity = adjust_buy_amount(amount, price, precision, min_amount, min_notional)
# #     elif side == 'sell':
# #         adjusted_quantity = adjust_sell_amount(amount, precision, min_amount, min_notional)
# #     else:
# #         raise ValueError("Side must be 'buy' or 'sell'")
# #
# #     formatted_amount = "{:.{}f}".format(adjusted_quantity, precision)
# #     return formatted_amount
# #
