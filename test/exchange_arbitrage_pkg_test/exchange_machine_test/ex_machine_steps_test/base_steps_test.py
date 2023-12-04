import asyncio

import socket

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only



from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeysHFT01, CoinbaseAPIKeys
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine_steps import Mover
from src.exchange_arbitrage_pkg.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_arbitrage_pkg.exchange_class.binance_exchange import BinanceExchange


def test_movers():
    binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
    symbol = "VOXELUSDT"
    quantity = 29

    mover = Mover(debug=True)
    order_res = asyncio.run(mover.move_crypto(src_exchange_platform=coinbase_exchange,
                                              dst_exchange_platform=binance_exchange,
                                              symbol=symbol,
                                              quantity=quantity))
    print(order_res)
