##########   Force to use IPv4   #########
import socket

from src.data_pkg.ts_db.table_names_ds import TableNames
from src.data_pkg.ts_db.ts_db_handler import DbHandler
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_eval_w_formula import SymbolEvaluatorFormula
from src.pipelines.exchange_arbitrage_pipeline.simple_pipeline import SimplePipeline

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
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter


class SymbolEvalTesterByPipeline(SimplePipeline):
    def __init__(self,
                 sample_size: Optional[int],
                 trade_hyper_parameters: TradeHyperParameter,
                 storage_dir: Optional[str],
                 table_names: TableNames,
                 debug: bool):
        super().__init__(sample_size=sample_size,
                         trade_hyper_parameters=trade_hyper_parameters,
                         storage_dir=storage_dir,
                         table_names=table_names,
                         debug=debug)

        self.symbol_evaluator_obj = SymbolEvaluatorFormula(column_info_obj=self.column_info_obj,
                                                           trade_hyper_parameters=self.trade_hyper_parameters,
                                                           debug=self.debug)


def get_symbol_evaluator():
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
                                        num_of_top_symbols=2,
                                        budget_factor=0.5,
                                        acceptable_amount_diff_percent=0.5,
                                        min_acceptable_budget=10,
                                        secondary_symbol_rank=2)

    my_table_names = TableNames()

    pipeline = SymbolEvalTesterByPipeline(trade_hyper_parameters=tr_hype_param,
                                          sample_size=Sample_Size,
                                          storage_dir=None,
                                          table_names=my_table_names,
                                          debug=DEBUG)
    return pipeline.symbol_evaluator_obj, pipeline


def symbol_eval_smoke_test():
    symbol_evaluator_obj, pipeline = get_symbol_evaluator()
    symbol = "BTCUSDT"
    order_book = symbol_evaluator_obj.get_order_books(symbol=symbol, exchange_pair=pipeline.exchange_pair)
    print(order_book.head(10).to_string())


if __name__ == '__main__':
    symbol_eval_smoke_test()






