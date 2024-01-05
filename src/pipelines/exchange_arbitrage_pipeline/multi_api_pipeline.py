##########   Force to use IPv4   #########
import socket

from src.data_pkg.ts_db.table_names_ds import TableNames
from src.exchange_arbitrage_pkg.broker_config.ex_multi_api_class import BINANCE_MULTI_API_OBJ, CBAT_MULTI_API_OBJ
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.arbit_machinemaker_multi_api import \
    ArbitMachineMakerMultiApi
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_code_bases.exchange_class.exchange_pair_multi_api import CollectableExPair
from src.pipelines.exchange_arbitrage_pipeline.simple_pipeline import SimplePipeline

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only
##########################################

from typing import Optional
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter


class MultiAPIPipeline(SimplePipeline):
    def __init__(self,
                 trade_hyper_parameters: TradeHyperParameter,
                 table_names: TableNames,
                 debug: bool):
        super().__init__(trade_hyper_parameters=trade_hyper_parameters,
                         table_names=table_names,
                         debug=debug)
        binance_apis = [BinanceExchange(api_obj) for api_obj in BINANCE_MULTI_API_OBJ.get_ex_api_list()]
        coinbase_apis = [AdvanceTradeExchange(api_obj) for api_obj in CBAT_MULTI_API_OBJ.get_ex_api_list()]
        self.collectable_ex_pair = CollectableExPair(binance_apis, coinbase_apis)

    def _get_arbitrage_maker_obj(self):
        return ArbitMachineMakerMultiApi(exchange_pair_collection=self.collectable_ex_pair,
                                         col_info_obj=self.column_info_obj,
                                         trade_hy_params_obj=self.trade_hyper_parameters,
                                         db_handler=self.db_handler,
                                         debug=self.debug)

    async def run_pipeline(self):
        diff_df_maker_obj = self._get_diff_df_maker_obj()
        arbitrage_maker_obj = self._get_arbitrage_maker_obj()
        counter = 0
        while True:
            if self.debug:
                print("Try number: ", counter+1)
            diff_df = await diff_df_maker_obj.obtain_and_process_diff_df(counter=counter,
                                                                         sleep_time=self.sleep_time,
                                                                         storage_dir=self.storage_dir)
            await arbitrage_maker_obj.create_and_run_arbit_machines(diff_df)
            counter += 1
            if self.trade_hyper_parameters.diff_maker_config.run_number is not None:
                if counter >= self.trade_hyper_parameters.diff_maker_config.run_number:
                    break
