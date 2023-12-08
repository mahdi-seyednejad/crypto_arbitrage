import socket

from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only


import asyncio

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, \
    BinanceAPIKeysHFT01
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.cross_punch import \
    CrossPunch
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
# from src.exchange_code_bases.exchange_class import BinanceExchange


def smoke_test_cross_punch_bi_to_cb():
    binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())

    symbol = "BTCUSDT"
    quantity = 0.0001

    strike = CrossPunch(symbol=symbol,
                        src_exchange_platform=binance_exchange,
                        dst_exchange_platform=coinbase_exchange,
                        desired_quantity=quantity,
                        debug=True)

    order_log = asyncio.run(strike.punch())


def smoke_test_cross_punch_cb_to_bi():
    binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())

    symbol = "FLOWUSDT"
    quantity = 10

    strike = CrossPunch(symbol=symbol,
                        src_exchange_platform=coinbase_exchange,
                        dst_exchange_platform=binance_exchange,
                        desired_quantity=quantity,
                        # quantity_deduction_percent=0.05,
                        debug=True)

    order_log = asyncio.run(strike.punch())


if __name__ == '__main__':
    smoke_test_cross_punch_bi_to_cb()

    # smoke_test_cross_punch_cb_to_bi()

