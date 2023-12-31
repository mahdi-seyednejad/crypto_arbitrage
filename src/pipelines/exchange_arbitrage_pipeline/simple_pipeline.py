##########   Force to use IPv4   #########
import socket

from src.data_pkg.ts_db.table_names_ds import TableNames
from src.data_pkg.ts_db.ts_db_handler import DbHandler
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_eval_w_formula import SymbolEvaluatorFormula

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only
##########################################


import asyncio
from typing import Type, Optional, Dict

from src.exchange_arbitrage_pkg.diff_df_maker_pkg.diff_df_maker_class import PriceDiffExtractor
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, BinanceAPIKeysHFT01
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.arbit_machine_maker_punch import ArbitrageMachineMakerPunch
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_code_bases.exchange_class.exchange_pair_class import ExchangePair
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_evaluator import SymbolEvaluatorArbitrage
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter, \
    WaitTimeDeposit


class SimplePipeline:
    def __init__(self,
                 sample_size: Optional[int],
                 trade_hyper_parameters: TradeHyperParameter,
                 storage_dir: Optional[str],
                 table_names: TableNames,
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
        self.db_handler = DbHandler(
            time_column=self.column_info_obj.current_time_col,
            date_as_index=False,
            table_names=table_names,
            debug=True)
        self.symbol_evaluator_obj = SymbolEvaluatorFormula(column_info_obj=self.column_info_obj,
                                                           trade_hyper_parameters=self.trade_hyper_parameters,
                                                           exchange_pair=self.exchange_pair,
                                                           db_handler=self.db_handler,
                                                           debug=self.debug)

    def get_diff_df_maker_obj(self, diff_df_maker_class: Type[PriceDiffExtractor]):
        return diff_df_maker_class(first_exchange_obj=self.binance_exchange,
                                   second_exchange_obj=self.coinbase_exchange,
                                   col_info=self.column_info_obj,
                                   diff_db_handler=self.db_handler,
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
        executor_object = ArbitrageMachineMakerPunch(exchange_pair=self.exchange_pair,
                                                     col_info_obj=self.column_info_obj,
                                                     symbol_evaluator_obj=self.symbol_evaluator_obj,
                                                     trade_hy_params_obj=self.trade_hyper_parameters,
                                                     db_handler=self.db_handler,
                                                     debug=self.debug)
        await self.run_arbitrage_on_diff_df(diff_df_maker_obj,
                                            executor_object.create_and_run_arbit_machines)


if __name__ == '__main__':
    DEBUG = True
    Sample_Size = None  # Just for testing

    tr_hype_param = TradeHyperParameter(trade_bucket_size=20,
                                        order_book_fetch_level=100,
                                        acceptable_slippage=0.5,
                                        price_range_percent=0.5,
                                        initial_budget=None,
                                        outlier_threshold=2.1,
                                        fetch_period=30,
                                        run_number=10,
                                        num_of_top_symbols=2,
                                        budget_factor=0.5,
                                        acceptable_amount_diff_percent=0.5,
                                        min_acceptable_budget=10,
                                        secondary_symbol_rank=2,
                                        num_rank_hard_cut_off=4,
                                        wait_time_deposit=WaitTimeDeposit(check_interval=10, # Get this to the punches
                                                                          timeout=800,
                                                                          amount_loss=0.05,
                                                                          second_chance=True))

    my_table_names = TableNames()

    pipeline = SimplePipeline(trade_hyper_parameters=tr_hype_param,
                              sample_size=Sample_Size,
                              storage_dir=None,
                              table_names=my_table_names,
                              debug=DEBUG)
    asyncio.run(pipeline.run())

# ToDO: Idea: Predict the price diff based on exchanges 1,2, to apply on echange 1,3
# ToDo: make a list of exchange machines and their status: running, blocked, waiting, etc.
