import socket

from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.hook_punch import \
    HookPunch
from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor
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

def withdraw_checker_test():

    binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
    crypto_withdraws = binance_exchange.sync_client.client.get_withdraw_history(coin='FORT')
    crypto_deposit = binance_exchange.sync_client.client.get_deposit_history(coin='FORT')

    print(crypto_deposit)

if __name__ == '__main__':
    withdraw_checker_test()