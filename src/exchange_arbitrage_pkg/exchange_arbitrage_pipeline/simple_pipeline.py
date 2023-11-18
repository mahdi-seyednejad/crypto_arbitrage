import asyncio

import cbpro
from typing import Type, Optional

from src.exchange_arbitrage_pkg.bi_cb_exchanger_arbitrage_client import CryptoExArbitrageWithClient
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeys
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.simple_executor import ArbitrageExecutor
from src.exchange_arbitrage_pkg.exchange_class.binance_exchange import BinanceExchange
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter


class SimplePipeline:
    def __init__(self,
                 sample_size: Optional[int],
                 trade_hyper_parameters: TradeHyperParameter,
                 storage_dir: Optional[str],
                 debug: bool):
        self.DEBUG = debug
        self.sample_size = sample_size  # Just for testing
        self.trade_hyper_parameters = trade_hyper_parameters
        self.storage_dir = storage_dir
        self.binance_exchange = BinanceExchange(BinanceAPIKeys())
        self.coinbase_exchange = cbpro.PublicClient()

    def get_exchange_arbit_obj(self, exchange_arbit_class: Type[CryptoExArbitrageWithClient]):
        return exchange_arbit_class(binance_exchange_obj=self.binance_exchange,
                                    coinbase_client_sync=self.coinbase_exchange,
                                    experiment_sample_size=self.sample_size,
                                    debug=self.DEBUG)

    def run_executor(self, exchange_arbitrage_obj, arbitrage_function):
        # It calls the "run" method from the exchange arbitrage object
        asyncio.run(
            exchange_arbitrage_obj.run(run_number=10,
                                       apply_function=arbitrage_function,
                                       storage_dir=None))

    def run(self):
        exchange_arbit_obj = self.get_exchange_arbit_obj(exchange_arbit_class=CryptoExArbitrageWithClient)

        self.run_executor(exchange_arbit_obj,
                          ArbitrageExecutor().execute_from_df)


if __name__ == '__main__':
    debug = True
    sample_size = 10  # Just for testing

    tr_hype_param = TradeHyperParameter(trade_bucket_size=5)
    pipeline = SimplePipeline(trade_hyper_parameters=tr_hype_param,
                              sample_size=sample_size,
                              storage_dir=None,
                              debug=debug)
    pipeline.run()
