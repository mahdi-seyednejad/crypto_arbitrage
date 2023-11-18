import asyncio

from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_trade_codes import buy_binance, sell_binance, \
    get_deposit_address_binance, check_balance, withdraw
from src.exchange_arbitrage_pkg.broker_utils.coinbase_utils.coinbase_trade_code import check_balance_coinbase, \
    buy_sell_coinbase, withdraw_coinbase, get_deposit_address_coinbase

async def execute_binance_trade(client, trade, debug):
    if trade.trade_type == 'check':
        result = await check_balance(client, trade.symbol)
    elif trade.trade_type == 'withdraw':
        result = await withdraw(client, trade.symbol, trade.quantity, trade.address, debug=debug)
    elif trade.trade_type == 'buy':
        result = await buy_binance(client, trade.symbol, trade.quantity, trade.price, debug)
    elif trade.trade_type == 'sell':
        result = await sell_binance(client, trade.symbol, trade.quantity, trade.price, debug)
    elif trade.trade_type == 'deposit':
        result = await get_deposit_address_binance(client, trade.symbol, debug)
    else:
        print(f"Unsupported trade type: {trade.trade_type}")
        result = None
    return (trade.trade_type, result)


async def execute_coinbase_trade(client, trade, debug):
    if trade.trade_type == 'check':
        result = await check_balance_coinbase(client, trade.symbol)
    elif trade.trade_type == 'withdraw':
        result = await withdraw_coinbase(client, trade.symbol, trade.quantity, trade.address)
    elif trade.trade_type in ['buy', 'sell']:
        result = await buy_sell_coinbase(client, trade.symbol, trade.side, trade.quantity, trade.price)
    elif trade.trade_type == 'deposit':
        result = await get_deposit_address_coinbase(client, trade.symbol)
    else:
        print(f"Unsupported trade type: {trade.trade_type}")
        result = None
    return (trade.trade_type, result)



