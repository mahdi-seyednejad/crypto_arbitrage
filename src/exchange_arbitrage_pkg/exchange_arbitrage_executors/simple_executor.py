from typing import List

from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_class_pkg.exchange_class import ExchangeMachine
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_evaluator import SymbolEvaluatorArbitrage
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_base import TradeRunner
from src.exchange_arbitrage_pkg.utils.binance_coinbase_convertor import extract_symbol
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.exchange_picker import pick_exchange
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter


class ArbitrageExecutor:
    def __init__(self,
                 exchange_list: List[ExchangeAbstractClass],
                 column_info_obj: ColumnInfoClass,
                 symbol_evaluator_obj: SymbolEvaluatorArbitrage,
                 trade_hy_params_obj: TradeHyperParameter,
                 debug: bool):
        self.exchange_list = exchange_list
        self.col_info_obj = column_info_obj
        self.symbol_evaluator_obj = symbol_evaluator_obj
        self.trade_hy_params_obj = trade_hy_params_obj
        self.debug = debug

        self.is_good_to_trade_col = column_info_obj.symbol_eval_col_obj.is_good_to_trade_col

    def _get_exchange(self, exchange_name):
        return pick_exchange(exchange_name, self.exchange_list)

    def get_bucket_organized_df(self, df_in):
        df = df_in.copy()
        sorting_col_tuples = [
            (self.col_info_obj.current_price_diff_percentage_col, False),  # (col_name, ascending)
            (self.col_info_obj.exchange_volume_cols.get("binance_volume_col", "binance_volume_24h"), False),
            (self.col_info_obj.recency_col, False)]
        df.sort_values(by=[col[0] for col in sorting_col_tuples],
                       ascending=[a[1] for a in sorting_col_tuples],
                       inplace=True)
        return df.head(self.trade_hy_params_obj.trade_bucket_size).copy()

    def _create_arbitrage_plan(self, df_in):
        df = df_in.copy()

        exchange_machines = []
        exchange_machine = None
        for index, row in df.iterrows():
            if row[self.col_info_obj.price_diff_col] > 0:  # Binance is more expensive => Binance is the seller
                exchange_machine = ExchangeMachine(name="Coinbase_to_Binance",
                                                   src_exchange_platform=self._get_exchange(ExchangeNames.Binance),
                                                   dst_exchange_platform=self._get_exchange(ExchangeNames.Coinbase),
                                                   row=row,
                                                   col_info_obj=self.col_info_obj,
                                                   budget=self.trade_hy_params_obj.initial_budget)

            elif row[self.col_info_obj.price_diff_col] < 0:  # Coinbase is more expensive => Coinbase is the seller
                exchange_machine = ExchangeMachine(name="Binance_to_Coinbase",
                                                   src_exchange_platform=self._get_exchange(ExchangeNames.Coinbase),
                                                   dst_exchange_platform=self._get_exchange(ExchangeNames.Binance),
                                                   row=row,
                                                   col_info_obj=self.col_info_obj,
                                                   budget=self.trade_hy_params_obj.initial_budget)
            if row[self.col_info_obj.price_diff_col] == 0 or exchange_machine is None:
                # No opportunity
                pass
            else:
                # exchange_machine.create_trades(row, self.col_info_obj, self.trade_hy_params_obj.initial_budget)
                exchange_machines.append(exchange_machine)

        return exchange_machines

    def run_per_bucket(self, df_in):
        # We just work on the first bucket for now.
        df_bucket = self.get_bucket_organized_df(df_in)
        df_ranked = self.symbol_evaluator_obj.evaluate_then_rank_best_symbols(df_bucket, self.exchange_list)
        # df_ranked = self.symbol_evaluator_obj.rank_best_symbols(df_symbol_eval)
        return self._create_arbitrage_plan(df_ranked)

    async def main_execute_from_df(self, df_in):  # The main function that gets the dataframe
        exchange_machines = self.run_per_bucket(df_in)
        trade_runner = TradeRunner(exchange_machines, self.debug)
        await trade_runner.execute()

# If you use a crypto for hft, and it is still on the top of the diff_df,
# then you can do it again.
# In this case, you have a loop over a crypto to keep buying and selling it.
