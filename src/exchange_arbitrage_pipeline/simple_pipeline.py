import asyncio
from typing import Type, Optional

from src.exchange_arbitrage_pkg.diff_df_maker_class import PriceDiffExtractor
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, BinanceAPIKeysHFT01
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.arbit_machine_maker_punch import ArbitrageMachineMakerPunch
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_code_bases.exchange_class.exchange_pair_class import ExchangePair
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
        self.binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
        self.coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
        self.exchange_pair = ExchangePair(first_exchange=self.binance_exchange,
                                          second_exchange=self.coinbase_exchange)
        self.price_cols = self.exchange_pair.get_all_price_cols()
        self.column_info_obj = ColumnInfoClass()
        self.symbol_evaluator_obj = SymbolEvaluatorArbitrage(column_info_obj=self.column_info_obj,
                                                             trade_hyper_parameters=self.trade_hyper_parameters,
                                                             price_cols=self.price_cols,
                                                             debug=self.debug)

    def get_diff_df_maker_obj(self, diff_df_maker_class: Type[PriceDiffExtractor]):
        return diff_df_maker_class(binance_exchange_obj=self.binance_exchange,
                                   coinbase_exchange_obj=self.coinbase_exchange,
                                   col_info=self.column_info_obj,
                                   experiment_sample_size=self.sample_size,
                                   debug=self.debug)

    async def run_arbitrage_on_diff_df(self, exchange_arbitrage_obj: PriceDiffExtractor,
                                       arbitrage_function):
        await exchange_arbitrage_obj.run(
            run_number=self.trade_hyper_parameters.run_number,
            apply_function=arbitrage_function,
            storage_dir=None
        )

    async def run(self):
        diff_df_maker_obj = self.get_diff_df_maker_obj(diff_df_maker_class=PriceDiffExtractor)

        # executor_object = ArbitrageMachineMaker(exchange_pair=self.exchange_pair,
        #                                         col_info_obj=self.column_info_obj,
        #                                         symbol_evaluator_obj=self.symbol_evaluator_obj,
        #                                         trade_hy_params_obj=self.trade_hyper_parameters,
        #                                         debug=self.debug)
        executor_object = ArbitrageMachineMakerPunch(exchange_pair=self.exchange_pair,
                                                     col_info_obj=self.column_info_obj,
                                                     symbol_evaluator_obj=self.symbol_evaluator_obj,
                                                     trade_hy_params_obj=self.trade_hyper_parameters,
                                                     debug=self.debug)
        await self.run_arbitrage_on_diff_df(diff_df_maker_obj,
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

    pipeline = SimplePipeline(trade_hyper_parameters=tr_hype_param,
                              sample_size=Sample_Size,
                              storage_dir=None,
                              debug=DEBUG)
    asyncio.run(pipeline.run())

#ToDO: Idea: Predict the price diff based on exchanges 1,2, to apply on echange 1,3
# ToDo: make a list of exchange machines and their status: running, blocked, waiting, etc.
