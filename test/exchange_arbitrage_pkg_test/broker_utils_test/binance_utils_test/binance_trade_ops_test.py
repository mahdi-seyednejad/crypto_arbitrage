import socket
# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only


import asyncio

from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_trade_codes import withdraw_binance, \
    get_deposit_address_binance
from src.exchange_code_bases.advance_trade.coinbase_utils.coinbase_trade_code import get_deposit_address_coinbase, \
    withdraw_coinbase
from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor
from src.exchange_arbitrage_pkg.utils.binance_coinbase_convertor import convert__symbol_bi_to_cb

from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeysHFT01, CoinbaseAPIKeys
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange

binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
operation_executor = OperationExecutor(first_exchange=binance_exchange,
                                       second_exchange=coinbase_exchange,
                                       debug=True)


async def binance_withdraw_smoke_test():
    symbol = "BICOUSDT"
    quantity = 116.14
    debug = True
    coinbase_client = await coinbase_exchange.create_async_client()
    symbol_cb = convert__symbol_bi_to_cb(symbol)
    cb_dep_info = await get_deposit_address_coinbase(client=coinbase_client,
                                                     symbol=symbol_cb,
                                                     debug=debug)

    address = cb_dep_info['address']
    network = cb_dep_info['network']

    converted_network = operation_executor.network_convertor_obj.convert(crypto=symbol,
                                                                         network_name=network)

    binance_client = await binance_exchange.create_async_client()
    order_res = await withdraw_binance(client=binance_client,
                               symbol=symbol,
                               quantity=quantity,
                               address=address,
                               network=converted_network,
                               debug=debug)
    print(order_res)


async def coinbase_withdraw_smoke_test():
    symbol = "FORTUSDT"
    quantity = 0.001
    debug = True
    binance_client = await binance_exchange.create_async_client()
    coinbase_client = await coinbase_exchange.create_async_client()
    bi_dep_add = await get_deposit_address_binance(client=binance_client,
                                                   symbol=symbol,
                                                   debug=debug)

    symbol_cb = convert__symbol_bi_to_cb(symbol)
    order_res = await withdraw_coinbase(client=coinbase_client,
                                        symbol=symbol_cb,
                                        amount=quantity,
                                        crypto_address=bi_dep_add,
                                        debug=debug)
    print(order_res)


def test_pairs():
    info = binance_exchange.sync_client.client.get_exchange_info()
    pairs = [symbol['symbol'] for symbol in info['symbols'] if 'USD' not in symbol['symbol']]
    for pair in pairs:
        print(pair)

if __name__ == '__main__':
    # asyncio.run(binance_withdraw_smoke_test())
    asyncio.run(coinbase_withdraw_smoke_test())

