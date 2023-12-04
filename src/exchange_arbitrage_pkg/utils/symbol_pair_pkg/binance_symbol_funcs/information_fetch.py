from binance.client import Client


async def get_trade_details(client, symbol):
    info = await client.get_symbol_info(symbol)
    if info:
        buy_precision = info['baseAssetPrecision']
        min_buy_amount = info['filters'][2]['minQty']
        min_notional = info['filters'][3]['minNotional']
        return buy_precision, min_buy_amount, min_notional
    return None, None, None


def adjust_buy_amount(amount, price, buy_precision, min_buy_amount, min_notional):
    adjusted_amount = round(amount, buy_precision)
    if adjusted_amount < float(min_buy_amount):
        raise ValueError("Amount is below the minimum buy amount")
    if adjusted_amount * price < float(min_notional):
        raise ValueError("Trade value is below the minimum notional value")
    return adjusted_amount


async def get_adjusted_trade_amount(client, symbol, amount):
    ticker = await client.get_symbol_ticker(symbol="BTCUSDT")
    price = float(ticker['price'])
    buy_precision, min_buy_amount, min_notional = await get_trade_details(client, symbol)

    if buy_precision is None:
        raise ValueError(f"Could not fetch trade details for {symbol}")

    adjusted_amount = adjust_buy_amount(amount, price, buy_precision, min_buy_amount, min_notional)
    return adjusted_amount

