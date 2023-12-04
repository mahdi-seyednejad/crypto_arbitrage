import asyncio
from typing import Type, Optional

from src.exchange_arbitrage_pkg.bi_cb_exchanger_arbitrage_client import PriceDiffExtractor
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeys, CoinbaseProAPIKeys, \
    CoinbaseAPIKeys
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.ex_machine_maker import ArbitrageMachineMaker
from src.exchange_arbitrage_pkg.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_arbitrage_pkg.exchange_class.binance_exchange import BinanceExchange
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_evaluator import SymbolEvaluatorArbitrage
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.exchange_picker import get_all_price_cols
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
        # self.coinbase_exchange = CoinbaseExchange(CoinbaseProAPIKeys())
        self.coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
        self.exchange_list = [self.binance_exchange, self.coinbase_exchange]
        self.price_cols = get_all_price_cols(exchange_list=self.exchange_list)
        self.column_info_obj = ColumnInfoClass()
        self.symbol_evaluator_obj = SymbolEvaluatorArbitrage(column_info_obj=self.column_info_obj,
                                                             trade_hyper_parameters=self.trade_hyper_parameters,
                                                             price_cols=self.price_cols,
                                                             debug=self.debug)

    def get_exchange_arbit_obj(self, exchange_arbit_class: Type[PriceDiffExtractor]):
        return exchange_arbit_class(binance_exchange_obj=self.binance_exchange,
                                    coinbase_exchange_obj=self.coinbase_exchange,
                                    column_obj=self.column_info_obj,
                                    experiment_sample_size=self.sample_size,
                                    debug=self.debug)

    async def run_executor(self, exchange_arbitrage_obj: PriceDiffExtractor, arbitrage_function):
        await exchange_arbitrage_obj.run(
            run_number=self.trade_hyper_parameters.run_number,
            apply_function=arbitrage_function,
            storage_dir=None
        )

    async def run(self):
        exchange_arbit_obj = self.get_exchange_arbit_obj(exchange_arbit_class=PriceDiffExtractor)

        executor_object = ArbitrageMachineMaker(exchange_list=self.exchange_list,
                                                col_info_obj=self.column_info_obj,
                                                symbol_evaluator_obj=self.symbol_evaluator_obj,
                                                trade_hy_params_obj=self.trade_hyper_parameters,
                                                debug=self.debug)
        await self.run_executor(exchange_arbit_obj,
                                executor_object.create_and_run_arbit_machines)


if __name__ == '__main__':
    DEBUG = True
    Sample_Size = 100  # Just for testing

    tr_hype_param = TradeHyperParameter(trade_bucket_size=5,
                                        order_book_fetch_level=100,
                                        acceptable_slippage=0.5,
                                        price_range_percent=0.5,
                                        initial_budget=None,
                                        outlier_threshold=2.1,
                                        fetch_period=30,
                                        run_number=10,
                                        budget_factor=0.5)
    col_obj = ColumnInfoClass()

    pipeline = SimplePipeline(trade_hyper_parameters=tr_hype_param,
                              sample_size=Sample_Size,
                              storage_dir=None,
                              debug=DEBUG)
    asyncio.run(pipeline.run())

# ToDo: make a list of exchange machines and their status: running, blocked, waiting, etc.