from typing import List

from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine import ExchangeMachine
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_evaluator import SymbolEvaluatorArbitrage
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_base import TradeRunner
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.exchange_picker import pick_exchange
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter


class ExchangeMachineMaker:
    def __init__(self,
                 exchange_list: List[ExchangeAbstractClass],
                 col_info_obj: ColumnInfoClass,
                 symbol_evaluator_obj: SymbolEvaluatorArbitrage,
                 trade_hy_params_obj: TradeHyperParameter,
                 debug: bool):
        self.exchange_list = exchange_list
        for exchange in self.exchange_list:
            exchange.set_budget(exchange.sync_client, trade_hy_params_obj.initial_budget)
        self.col_info_obj = col_info_obj
        self.symbol_evaluator_obj = symbol_evaluator_obj
        self.trade_hy_params_obj = trade_hy_params_obj
        self.debug = debug
        self.is_good_to_trade_col = col_info_obj.symbol_eval_col_obj.is_good_to_trade_col

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

    def get_assigned_allowed_budget(self, total_budget, row):
        allowed_budget = self.trade_hy_params_obj.budget_factor * total_budget
        return allowed_budget * row[self.col_info_obj.symbol_eval_col_obj.budge_factor_col]

    def _create_exchange_machines(self, df_in):
        df = df_in.copy()

        exchange_machines = []
        exchange_machine = None
        for index, row in df.iterrows():
            if row[self.col_info_obj.price_diff_col] > 0:  # Binance is more expensive => Binance is the seller
                # We need to check/buy the coin on Coinbase, then, move it to Binance. Then, sell it on Binance.
                src_exchange = self._get_exchange(ExchangeNames.Coinbase)
                available_budget = src_exchange.get_budget_sync()
                exchange_machine = ExchangeMachine(name="Coinbase_to_Binance",
                                                   src_exchange_platform=src_exchange,
                                                   dst_exchange_platform=self._get_exchange(ExchangeNames.Binance),
                                                   row=row,
                                                   col_info_obj=self.col_info_obj,
                                                   budget=self.get_assigned_allowed_budget(available_budget, row),
                                                   debug=self.debug)

            elif row[self.col_info_obj.price_diff_col] < 0:  # Coinbase is more expensive => Coinbase is the seller
                # We need to check/buy the coin on Binance, then, move it to Coinbase. Then, sell it on Coinbase.
                src_exchange = self._get_exchange(ExchangeNames.Binance)
                available_budget = src_exchange.get_budget_sync()
                exchange_machine = ExchangeMachine(name="Binance_to_Coinbase",
                                                   src_exchange_platform=src_exchange,
                                                   dst_exchange_platform=self._get_exchange(ExchangeNames.Coinbase),
                                                   row=row,
                                                   col_info_obj=self.col_info_obj,
                                                   budget=self.get_assigned_allowed_budget(available_budget, row),
                                                   debug=self.debug)
            if row[self.col_info_obj.price_diff_col] == 0 or exchange_machine is None:
                # No opportunity
                pass
            else:
                # exchange_machine.create_trades(row, self.col_info_obj, self.trade_hy_params_obj.initial_budget)
                exchange_machines.append(exchange_machine)

        return exchange_machines

    def _assign_budget_to_exchange_machines(self, row, runnable_ex_machine_num):
        #ToDo: Need to work in this function. Now, we just send a uniform budget to runnable_ex_machines
        return 1/runnable_ex_machine_num

    async def create_ex_machine_for_one_bucket(self, df_in):
        # We just work on the first bucket for now.
        df_bucket = self.get_bucket_organized_df(df_in)
        df_ranked = self.symbol_evaluator_obj.evaluate_then_rank_best_symbols(df_bucket, self.exchange_list)
        runnable_ex_machine_num = min(self.trade_hy_params_obj.num_of_top_symbols, len(df_bucket))

        df_ranked[self.col_info_obj.symbol_eval_col_obj.budge_factor_col] = df_ranked.apply(
            lambda row: self._assign_budget_to_exchange_machines(row, runnable_ex_machine_num), axis=1)
        # df_ranked = self.symbol_evaluator_obj.rank_best_symbols(df_symbol_eval)
        df_selected = df_ranked.iloc[:runnable_ex_machine_num]
        return self._create_exchange_machines(df_selected)

    async def break_df_to_positive_negative(self, df_in):
        df = df_in.copy()
        positive_df = df[df[self.col_info_obj.price_diff_col] > 0]
        negative_df = df[df[self.col_info_obj.price_diff_col] < 0]
        return positive_df, negative_df

    async def main_execute_ex_machines(self, df_in):  # The main function that gets the dataframe
        positive_df, negative_df = await self.break_df_to_positive_negative(df_in)
        # Everytime that we call this, we need to coordinate with the budget manager.

        positive_exchange_machines = await self.create_ex_machine_for_one_bucket(positive_df)
        negative_exchange_machines = await self.create_ex_machine_for_one_bucket(negative_df)
        # selected_exchange_machines = exchange_machines[:runnable_ex_machine_num]
        trade_runner_positive = TradeRunner(positive_exchange_machines, self.debug)
        trade_runner_negative = TradeRunner(negative_exchange_machines, self.debug)
        await trade_runner_positive.execute()
        await trade_runner_negative.execute()
        # Todo: Define how many exchange machine you are going to run per tr

    #ToDO: What if all budget is in one platform: Move them using bitcoin to the other platform.
    # If a hhigher price crypto is already on the ghier price platform, then you can sell it, move the money to the cheaper platform. Then, buy, mive, sell.
    # YOu can so it as much as it is on the top of the diff_df.

# If you use a crypto for hft, and it is still on the top of the diff_df,
# then you can do it again.
# In this case, you have a loop over a crypto to keep buying and selling it.
# Last binancve bought: PONDUSDT