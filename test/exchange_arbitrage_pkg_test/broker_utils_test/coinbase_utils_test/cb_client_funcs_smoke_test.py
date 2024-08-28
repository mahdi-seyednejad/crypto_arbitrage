import socket

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only

import asyncio

from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeysHFT01, CoinbaseAPIKeys
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange

binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())

def test_get_order_book():
    limit=50
    old_way = coinbase_exchange.get_latest_prices_sync(sample_size=limit)
    # print(old_way)
    prices = coinbase_exchange.sync_client.get_prices_as_df(price_col='cb_at_price', limit=100)
    # print(prices)
    product_id = "BTC-USD"
    product_ticker = coinbase_exchange.sync_client.get_product_ticker(product_id=product_id)
    print(product_ticker)


async def busy_waiting_cb_test():
    symbol = "BTRSTUSDT"
    desired_quantity = 52.26

    cb_async_client = await coinbase_exchange.create_async_client()
    was_received = await coinbase_exchange.wait_til_receive_Async(symbol=symbol,
                                                                  expected_amount=desired_quantity,
                                                                  check_interval=5,
                                                                  timeout_in=420,
                                                                  amount_loss=0.05,
                                                                  second_chance=True,
                                                                  num_of_wait_tries=4,
                                                                  debug=True)

    print(f"Was received: {was_received}")

if __name__ == '__main__':
    asyncio.run(busy_waiting_cb_test())

