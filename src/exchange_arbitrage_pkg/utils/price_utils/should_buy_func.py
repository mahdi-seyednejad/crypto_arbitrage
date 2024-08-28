async def should_buy_binance_Async(client, symbol, desired_quantity, available_balance):
    # Fetch current price
    ticker = await client.get_symbol_ticker(symbol=symbol)
    current_price = float(ticker["price"])

    # Fetch trading information for the symbol
    info = await client.get_symbol_info(symbol)
    min_notional = float(next(filter(lambda f: f['filterType'] == 'MIN_NOTIONAL', info['filters']))['minNotional'])

    # Calculate quantity to buy and its notional value
    quantity_to_buy = max(0, desired_quantity - available_balance)
    notional_value_to_buy = quantity_to_buy * current_price

    # Decision based on minimum notional
    if notional_value_to_buy >= min_notional:
        return True, quantity_to_buy
    else:
        return False, -1


def should_buy_binance_sync(client, symbol, desired_quantity, available_balance):
    # Fetch current price
    current_price = float(client.get_symbol_ticker(symbol=symbol)["price"])

    # Fetch trading information for the symbol
    info = client.get_symbol_info(symbol)
    min_notional = float(next(filter(lambda f: f['filterType'] == 'MIN_NOTIONAL', info['filters']))['minNotional'])

    # Calculate quantity to buy and its notional value
    quantity_to_buy = max(0, desired_quantity - available_balance)
    notional_value_to_buy = quantity_to_buy * current_price

    # Decision based on minimum notional
    if notional_value_to_buy >= min_notional:
        return True, quantity_to_buy
    else:
        return False, -1