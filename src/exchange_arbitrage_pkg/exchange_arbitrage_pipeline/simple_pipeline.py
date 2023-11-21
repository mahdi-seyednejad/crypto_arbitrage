import asyncio

import cbpro
from typing import Type, Optional

from src.exchange_arbitrage_pkg.bi_cb_exchanger_arbitrage_client import CryptoExArbitrageWithClient
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeys, CoinbaseProAPIKeys
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.simple_executor import ArbitrageExecutor
from src.exchange_arbitrage_pkg.exchange_class.binance_exchange import BinanceExchange
from src.exchange_arbitrage_pkg.exchange_class.coinbase_exchange import CoinbaseExchange
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_evaluator import SymbolEvaluatorArbitrage
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter


class SimplePipeline:
    def __init__(self,
                 sample_size: Optional[int],
                 trade_hyper_parameters: TradeHyperParameter,
                 storage_dir: Optional[str],
                 debug: bool):
        self.debug = debug
        self.sample_size = sample_size  # Just for testing
        self.trade_hyper_parameters = trade_hyper_parameters
        self.storage_dir = storage_dir
        self.binance_exchange = BinanceExchange(BinanceAPIKeys())
        self.coinbase_exchange = CoinbaseExchange(CoinbaseProAPIKeys())
        self.exchange_list = [self.binance_exchange, self.coinbase_exchange]

        self.column_info_obj = ColumnInfoClass()
        self.symbol_evaluator_obj = SymbolEvaluatorArbitrage(column_info_obj=self.column_info_obj,
                                                             trade_hyper_parameters=self.trade_hyper_parameters)

    def get_exchange_arbit_obj(self, exchange_arbit_class: Type[CryptoExArbitrageWithClient]):
        return exchange_arbit_class(binance_exchange_obj=self.binance_exchange,
                                    coinbase_exchange_obj=self.coinbase_exchange,
                                    column_obj=self.column_info_obj,
                                    experiment_sample_size=self.sample_size,
                                    debug=self.debug)

    # def run_executor(self, exchange_arbitrage_obj, arbitrage_function):
    #     # It calls the "run" method from the exchange arbitrage object
    #     asyncio.run(
    #         exchange_arbitrage_obj.run(run_number=10,
    #                                    apply_function=arbitrage_function,
    #                                    storage_dir=None))
    async def run_executor(self, exchange_arbitrage_obj, arbitrage_function):
        await exchange_arbitrage_obj.run(
            run_number=10,
            apply_function=arbitrage_function,
            storage_dir=None
        )

    # def run(self):
    #     exchange_arbit_obj = self.get_exchange_arbit_obj(exchange_arbit_class=CryptoExArbitrageWithClient)
    #
    #     executor_object = ArbitrageExecutor(exchange_list=self.exchange_list,
    #                                         column_info_obj=self.column_info_obj,
    #                                         symbol_evaluator_obj=self.symbol_evaluator_obj,
    #                                         trade_hy_params_obj=self.trade_hyper_parameters,
    #                                         debug=self.debug)
    #     self.run_executor(exchange_arbit_obj,
    #                       executor_object.main_execute_from_df)
    #
    async def run(self):
        exchange_arbit_obj = self.get_exchange_arbit_obj(exchange_arbit_class=CryptoExArbitrageWithClient)

        executor_object = ArbitrageExecutor(exchange_list=self.exchange_list,
                                            column_info_obj=self.column_info_obj,
                                            symbol_evaluator_obj=self.symbol_evaluator_obj,
                                            trade_hy_params_obj=self.trade_hyper_parameters,
                                            debug=self.debug)
        await self.run_executor(exchange_arbit_obj,
                          executor_object.main_execute_from_df)


if __name__ == '__main__':
    DEBUG = True
    Sample_Size = 100  # Just for testing

    tr_hype_param = TradeHyperParameter(trade_bucket_size=5,
                                        order_book_fetch_level=100,
                                        acceptable_slippage=0.5,
                                        price_range_percent=0.5,
                                        initial_budget=1000.0,
                                        outlier_threshold=2.1,)
    col_obj = ColumnInfoClass()

    pipeline = SimplePipeline(trade_hyper_parameters=tr_hype_param,
                              sample_size=Sample_Size,
                              storage_dir=None,
                              debug=DEBUG)
    asyncio.run(pipeline.run())

