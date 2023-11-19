from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_helpers import execute_binance_trade, \
    execute_coinbase_trade


async def move_crypto_from_coinbase_to_binance(coinbase_exchange, binance_exchange, symbol, quantity, debug):
    # Create async clients for each exchange
    coinbase_async_client = await coinbase_exchange.create_async_client()
    binance_async_client = await binance_exchange.create_async_client()

    # Get Binance deposit address for the symbol
    deposit_trade = Trade(binance_exchange, 'deposit', symbol, None, None)
    _, deposit_info = await execute_binance_trade(binance_async_client, deposit_trade, debug)
    binance_deposit_address = deposit_info['address']

    # Withdraw from Coinbase to Binance deposit address
    withdraw_trade = Trade(coinbase_exchange, 'withdraw', symbol, None, quantity, None, None, binance_deposit_address)
    withdraw_result = await execute_coinbase_trade(coinbase_async_client, withdraw_trade, debug)

    return withdraw_result

