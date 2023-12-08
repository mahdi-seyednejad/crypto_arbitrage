import asyncio

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeysHFT01
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_steps import Seller
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange


def seller_obj_smoke_test():
    seller = Seller(debug=True)
    binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
    symbol = "ACHUSDT"
    quantity = 46
    order_res = asyncio.run(seller.sell_crypto(exchange_platform=binance_exchange,
                                               symbol=symbol,
                                               quantity=quantity))


if __name__ == '__main__':
    seller_obj_smoke_test()
