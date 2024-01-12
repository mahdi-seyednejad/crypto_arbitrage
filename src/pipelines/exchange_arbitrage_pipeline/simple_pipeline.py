##########   Force to use IPv4   #########
import socket

from src.data_pkg.ts_db.table_names_ds import TableNames
from src.data_pkg.ts_db.ts_db_handler import DbHandler
from src.exchange_arbitrage_pkg.utils.debug_object import DebugClass

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only
##########################################


from src.exchange_arbitrage_pkg.diff_df_maker_pkg.diff_df_maker_class import PriceDiffExtractor
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, BinanceAPIKeysHFT01
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.arbit_machine_maker_punch import ArbitrageMachineMakerPunch
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_code_bases.exchange_class.exchange_pair_class import ExchangePair
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter


class SimplePipeline:
    def __init__(self,
                 trade_hyper_parameters: TradeHyperParameter,
                 table_names: TableNames,
                 debug_obj: DebugClass):
        self.debug_obj = debug_obj
        self.trade_hyper_parameters = trade_hyper_parameters
        self.sample_size = self.trade_hyper_parameters.diff_maker_config.sample_size  # Just for testing
        self.storage_dir = self.trade_hyper_parameters.diff_maker_config.storage_dir
        self.sleep_time = self.trade_hyper_parameters.diff_maker_config.sleep_time

        self.exchange_pair = ExchangePair(first_exchange=BinanceExchange(BinanceAPIKeysHFT01()),
                                          second_exchange=AdvanceTradeExchange(CoinbaseAPIKeys()))
        self.price_cols = self.exchange_pair.get_all_price_cols()
        self.column_info_obj = ColumnInfoClass()
        self.db_handler = DbHandler(
            time_column=self.column_info_obj.current_time_col,
            date_as_index=False,
            table_names=table_names,
            debug=self.debug_obj.db_handler_debug)

    def _get_diff_df_maker_obj(self):
        return PriceDiffExtractor(exchange_pair=self.exchange_pair,
                                  col_info=self.column_info_obj,
                                  diff_db_handler=self.db_handler,
                                  experiment_sample_size=self.sample_size,
                                  debug=self.debug_obj.price_diff_debug)

    def _get_arbitrage_maker_obj(self):
        return ArbitrageMachineMakerPunch(exchange_pair=self.exchange_pair,
                                          col_info_obj=self.column_info_obj,
                                          trade_hy_params_obj=self.trade_hyper_parameters,
                                          db_handler=self.db_handler,
                                          debug=self.debug_obj.arbitrage_machine_debug)

    async def run_pipeline(self):
        diff_df_maker_obj = self._get_diff_df_maker_obj()
        arbitrage_maker_obj = self._get_arbitrage_maker_obj()
        counter = 0
        while True:
            diff_df = await diff_df_maker_obj.obtain_and_process_diff_df(counter=counter,
                                                                         sleep_time=self.sleep_time,
                                                                         storage_dir=self.storage_dir)
            await arbitrage_maker_obj.create_and_run_arbit_machines(diff_df)
            counter += 1
            if self.trade_hyper_parameters.diff_maker_config.run_number is not None:
                if counter >= self.trade_hyper_parameters.diff_maker_config.run_number:
                    break


# ToDO: Idea: Predict the price diff based on exchanges 1,2, to apply on echange 1,3
# ToDo: make a list of exchange machines and their status: running, blocked, waiting, etc.
