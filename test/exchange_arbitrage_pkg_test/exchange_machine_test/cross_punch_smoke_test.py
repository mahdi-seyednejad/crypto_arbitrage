import socket

from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import WaitTimeDeposit
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

def smoke_test_cross_punch_bi_to_cb():

    # symbol = "BTCUSDT"
    # quantity = 0.0001

    symbol = "REQUSDT"
    quantity = 360

    waite_time_obj = WaitTimeDeposit(check_interval=10,  # Get this to the punches
                                     timeout=800,
                                     amount_loss=0.05,
                                     second_chance=True)

    strike = CrossPunch(symbol=symbol,
                        src_exchange_platform=binance_exchange,
                        dst_exchange_platform=coinbase_exchange,
                        desired_quantity=quantity,
                        operation_executor=operation_executor,
                        withdraw_fee=10,
                        wait_time_info=waite_time_obj,
                        debug=debug)

    order_log = asyncio.run(strike.punch())
    print(order_log)


def smoke_test_cross_punch_cb_to_bi():
    symbol = "FLOWUSDT"
    quantity = 10
    waite_time_obj = WaitTimeDeposit(check_interval=10,  # Get this to the punches
                                     timeout=800,
                                     amount_loss=0.05,
                                     second_chance=True)


    operation_executor = OperationExecutor(first_exchange=binance_exchange,
                                           second_exchange=coinbase_exchange,
                                           debug=debug)

    strike = CrossPunch(symbol=symbol,
                        src_exchange_platform=coinbase_exchange,
                        dst_exchange_platform=binance_exchange,
                        desired_quantity=quantity,
                        operation_executor=operation_executor,
                        withdraw_fee=0.1,
                        wait_time_info=waite_time_obj,
                        debug=True)

    order_log = asyncio.run(strike.punch())


if __name__ == '__main__':
    smoke_test_cross_punch_bi_to_cb()

    # smoke_test_cross_punch_cb_to_bi()

