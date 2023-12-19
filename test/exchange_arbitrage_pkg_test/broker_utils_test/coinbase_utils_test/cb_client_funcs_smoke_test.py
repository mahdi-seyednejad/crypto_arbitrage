import socket

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only

import asyncio

from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_trade_codes import withdraw, \
    get_deposit_address_binance
from src.exchange_arbitrage_pkg.broker_utils.coinbase_utils.coinbase_trade_code import get_deposit_address_coinbase, \
    withdraw_coinbase
from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor
from src.exchange_arbitrage_pkg.utils.binance_coinbase_convertor import convert__symbol_bi_to_cb

from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeysHFT01, CoinbaseAPIKeys
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange

binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())


async def busy_waiting_cb_test():
    symbol = "BTRSTUSDT"
    desired_quantity = 52.26

    cb_async_client = await coinbase_exchange.create_async_client()
    was_received = await coinbase_exchange.wait_til_receive_Async(symbol=symbol,
                                                                  expected_amount=desired_quantity,
                                                                  check_interval=5,
                                                                  timeout=420,
                                                                  amount_loss=0.05)

    print(f"Was received: {was_received}")

if __name__ == '__main__':
    asyncio.run(busy_waiting_cb_test())

