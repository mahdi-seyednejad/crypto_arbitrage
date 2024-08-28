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

binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())

debug = True
operation_executor = OperationExecutor(first_exchange=binance_exchange,
                                       second_exchange=coinbase_exchange,
                                       debug=debug)


def smoke_test_hook_punch_bi_to_cb():
    """
    When do we use Hook?
    We have a primary symbol that should go from src to dst exchanges. But, it is aklready on the dst.
    Primary symbol is on
    :return:
    :rtype:
    """

    primary_symbol = "FORTUSDT"
    quantity = 10

    sec_symbol = "LOKAUSDT"
    sec_quantity = 50


    '''
    This test means that we have primary symbol on coinbase. But, were were supposed to 
    buy it from binance and then send it to coinbase.
    So:
    1- we sell the primary on the dst exchange (coinbase) and then
    A- Reverse cross punch:
        2- buy the secondary on the same dst exchange.
        3- Then, we move the secondary from dst to src (a reverse cross punch). 
        4- Then, we sell the secondary on the src.  
    B- Primary cross punch:
        5- Buy primary on src
        6- Move primary from src to dst
        7- Sell primary on dst    
    '''

    strike = HookPunch(primary_symbol=primary_symbol,
                       secondary_symbol=sec_symbol,
                       src_exchange_platform=binance_exchange,
                       dst_exchange_platform=coinbase_exchange,
                       operation_executor=operation_executor,
                       primary_desired_quantity=quantity,
                       secondary_quantity=sec_quantity,
                       debug=True)

    order_log = asyncio.run(strike.punch())


def smoke_test_hook_punch_cb_to_bi():
    primary_symbol = "SUIUSDT"
    quantity = 10

    sec_symbol = "MANAUSDT"
    sec_quantity = 5

    strike = HookPunch(primary_symbol=primary_symbol,
                       secondary_symbol=sec_symbol,
                       src_exchange_platform=coinbase_exchange,
                       dst_exchange_platform=binance_exchange,
                       operation_executor=operation_executor,
                       primary_desired_quantity=quantity,
                       secondary_quantity=sec_quantity,
                       debug=True)

    order_log = asyncio.run(strike.punch())


if __name__ == '__main__':
    smoke_test_hook_punch_bi_to_cb()

    # smoke_test_cross_punch_cb_to_bi()
