# from typing import Optional, Type
# from abc import ABC, abstractmethod
#
# from src.data_pkg.ts_db.table_names_ds import TableNames
# from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter
#
#
# class PipelineAbstract(ABC):
#     def __init__(self,
#                  sample_size: Optional[int],
#                  trade_hyper_parameters: TradeHyperParameter,
#                  storage_dir: Optional[str],
#                  table_names: TableNames,
#                  debug: bool):
#         self.debug = debug
#         self.sample_size = sample_size  # Just for testing
#         self.trade_hyper_parameters = trade_hyper_parameters
#         self.storage_dir = storage_dir
#         self.binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
#         self.coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
#         self.exchange_pair = ExchangePair(first_exchange=self.binance_exchange,
#                                           second_exchange=self.coinbase_exchange)
#         self.price_cols = self.exchange_pair.get_all_price_cols()
#         self.column_info_obj = ColumnInfoClass()
#         self.db_handler = DbHandler(
#             time_column=self.column_info_obj.current_time_col,
#             date_as_index=False,
#             table_names=table_names,
#             debug=True)
#         self.symbol_evaluator_obj = SymbolEvaluatorFormula(column_info_obj=self.column_info_obj,
#                                                            trade_hyper_parameters=self.trade_hyper_parameters,
#                                                            exchange_pair=self.exchange_pair,
#                                                            db_handler=self.db_handler,
#                                                            debug=self.debug)
#
#     @abstractmethod
#     def get_diff_df_maker_obj(self, diff_df_maker_class: Type[PriceDiffExtractor]):
#         pass
#
#     @abstractmethod
#     async def run_arbitrage_on_diff_df(self, exchange_arbitrage_obj: PriceDiffExtractor,
#                                        arbitrage_function):
#
#     async def run(self):
#         diff_df_maker_obj = self.get_diff_df_maker_obj(diff_df_maker_class=PriceDiffExtractor)
#         executor_object = ArbitrageMachineMakerPunch(exchange_pair=self.exchange_pair,
#                                                      col_info_obj=self.column_info_obj,
#                                                      symbol_evaluator_obj=self.symbol_evaluator_obj,
#                                                      trade_hy_params_obj=self.trade_hyper_parameters,
#                                                      db_handler=self.db_handler,
#                                                      debug=self.debug)
#         await self.run_arbitrage_on_diff_df(diff_df_maker_obj,
#                                             executor_object.create_and_run_arbit_machines)
#
#
#
#
#
