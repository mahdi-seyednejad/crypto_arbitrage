import asyncio

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeysHFT01, CoinbaseAPIKeys
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_steps import Seller
from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange


binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
operation_executor = OperationExecutor(first_exchange=binance_exchange,
                                       second_exchange=coinbase_exchange,
                                       debug=True)


def seller_obj_smoke_test():
    seller = Seller(operation_executor=operation_executor,
                    debug=True)
    # symbol = "ACHUSDT"
    # quantity = 46
    symbol = "FORTUSDT"
    amount = 56.66218455999999
    order_res = asyncio.run(seller.sell_crypto(exchange_platform=binance_exchange,
                                               symbol=symbol,
                                               quantity=amount))


if __name__ == '__main__':
    seller_obj_smoke_test()
