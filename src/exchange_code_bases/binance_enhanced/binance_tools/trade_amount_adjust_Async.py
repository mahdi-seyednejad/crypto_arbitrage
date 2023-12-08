import decimal


class BinanceAmountAdjusterAsync:
    def __init__(self, client):
        self.client = client

    async def adjust_sell_amount(self, symbol, quantity):
        symb_info = await self.client.get_symbol_info(symbol)
        if symb_info is None:
            raise ValueError(f"No symbol information available for {symbol}")

        return await self.apply_market_lot_size_sell(symb_info, quantity)

    async def apply_market_lot_size_sell(self, symb_info, proposed_quant):
        res_dict = await self.search_dict(symb_info["filters"], "filterType", "LOT_SIZE")
        max_quant = float(res_dict['maxQty'])
        quant_mx = min(proposed_quant, max_quant)

        min_quant = float(res_dict['minQty'])
        quantity = max(quant_mx, min_quant)

        step_size = float(res_dict["stepSize"])
        if (step_size == 0) or ((quantity % step_size) == 0):
            return quantity
        else:
            d = decimal.Decimal(str(step_size))
            decimal_n = abs(d.as_tuple().exponent)
            return round(quantity, decimal_n)

    async def apply_price_filter(self, symb_info, avail_money):
        res_dict = await self.search_dict(symb_info["filters"], "filterType", "PRICE_FILTER")
        money_to_buy = min(float(res_dict["tickSize"]), avail_money)
        if avail_money < money_to_buy:
            return -1
        else:
            return money_to_buy

    async def calculate_and_adjust_buy_amount(self, symbol, price, remaining_budget, invest_portion, crypto_weight):
        symb_info = await self.client.get_symbol_info(symbol)
        if symb_info is None:
            raise ValueError(f"No symbol information available for {symbol}")

        avail_money = remaining_budget * invest_portion * crypto_weight
        money_to_buy = await self.apply_price_filter(symb_info, avail_money)

        if money_to_buy < 0:
            return 0
        proposed_quant = money_to_buy / float(price)
        return await self.adjust_buy_amount(symbol=symbol,
                                            quantity=proposed_quant,
                                            symb_info=symb_info)

    async def apply_market_lot_size_buy(self, symb_info, proposed_quant, price):
        res_dict = await self.search_dict(symb_info["filters"], "filterType", "LOT_SIZE")
        max_quant = float(res_dict['maxQty'])
        quant_mx = min(proposed_quant, max_quant)

        min_quant = float(res_dict['minQty'])
        quantity_initial = max(quant_mx, min_quant)

        # Ensure quantity meets the minimum notional value
        min_notional_value = await self.get_min_notional_value(symb_info)
        if price * quantity_initial < min_notional_value:
            quantity = 1.05 * (min_notional_value / price)
        else:
            quantity = quantity_initial

        # Adjust for step size (which is 1 in your case, so round to nearest integer)
        step_size = float(res_dict["stepSize"])
        adjusted_quant = max(round(quantity / step_size) * step_size, min_quant)
        if price * quantity < min_notional_value:
            return -adjusted_quant
        return adjusted_quant

    async def adjust_buy_amount(self, symbol, quantity, symb_info=None):
        if symb_info is None:
            symb_info = await self.client.get_symbol_info(symbol)
        if symb_info is None:
            raise ValueError(f"No symbol information available for {symbol}")

        ticker = await self.client.get_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])

        amount_lot_sized = await self.apply_market_lot_size_buy(symb_info=symb_info,
                                                                proposed_quant=quantity,
                                                                price=price)
        # min_notional_value = await self.get_min_notional_value(symb_info)
        # buy_notional_value = amount_lot_sized * price
        #
        # if buy_notional_value < min_notional_value:
        #     min_buy = 1.1 * (min_notional_value / price)
        #     min_amount_lot_sized = await self.apply_market_lot_size_buy(symb_info=symb_info,
        #                                                                 proposed_quant=min_buy)
        #     return -min_amount_lot_sized

        return amount_lot_sized

    async def search_dict(self, list_of_dicts, key, value):
        for d in list_of_dicts:
            if d[key] == value:
                return d
        return {}

    async def get_min_notional_value(self, symb_info):
        res_dict = await self.search_dict(symb_info["filters"], "filterType", "MIN_NOTIONAL")
        return float(res_dict['minNotional'])
