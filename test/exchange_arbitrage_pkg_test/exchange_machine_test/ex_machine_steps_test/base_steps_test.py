import asyncio

import socket

from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only


from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeysHFT01, CoinbaseAPIKeys
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_steps import Mover
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange

binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
operation_executor = OperationExecutor(first_exchange=binance_exchange,
                                       second_exchange=coinbase_exchange,
                                       debug=True)

def smoke_test_movers_cb_to_bi():
    symbol = "AXLUSDT"
    quantity = 29

    mover = Mover(operation_executor=operation_executor,
                  debug=True)

    order_res = asyncio.run(mover.move_crypto(src_exchange_platform=coinbase_exchange,
                                              dst_exchange_platform=binance_exchange,
                                              symbol=symbol,
                                              quantity=quantity))
    print(order_res)


def smoke_test_movers_bi_to_cb():
    symbol = "BTCUSDT"
    quantity = 0.0001

    mover = Mover(operation_executor=operation_executor,
                  debug=True)

    order_res = asyncio.run(mover.move_crypto(src_exchange_platform=binance_exchange,
                                              dst_exchange_platform=coinbase_exchange,
                                              symbol=symbol,
                                              quantity=quantity))
    print(order_res)

def smoke_test_persistent_movers_cb_to_bi():
    symbol = "LOKAUSDT"
    quantity = 50

    mover = Mover(operation_executor=operation_executor,
                  debug=True)

    order_res = asyncio.run(mover.move_crypto(src_exchange_platform=coinbase_exchange,
                                              dst_exchange_platform=binance_exchange,
                                              symbol=symbol,
                                              quantity=quantity))
    print(order_res)


if __name__ == '__main__':
    smoke_test_persistent_movers_cb_to_bi()
    # smoke_test_movers_cb_to_bi()
    # smoke_test_movers_bi_to_cb()
