from typing import List, Tuple

from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.budget_manager.budget_assigner.simple_budget_assigner import uniform_budget_assigner
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine import \
    ArbitrageMachine
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass
from src.exchange_arbitrage_pkg.exchange_class.exchange_pair_class import ExchangePair
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_evaluator import SymbolEvaluatorArbitrage
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_base import TradeRunner
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.exchange_picker import pick_exchange
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter


class ArbitrageMachineMaker:
    def __init__(self,
                 exchange_pair: ExchangePair,
                 col_info_obj: ColumnInfoClass,
                 symbol_evaluator_obj: SymbolEvaluatorArbitrage,
                 trade_hy_params_obj: TradeHyperParameter,
                 debug: bool):
        self.exchange_pair = exchange_pair
        self.exchange_pair.set_all_budgets(trade_hy_params_obj.initial_budget)
        self.col_info_obj = col_info_obj
        self.symbol_evaluator_obj = symbol_evaluator_obj
        self.trade_hy_params_obj = trade_hy_params_obj
        self.debug = debug
        self.is_good_to_trade_col = col_info_obj.symbol_eval_col_obj.is_good_to_trade_col
        self.best_sell_symbols_ex_1: List[Tuple[str, float]] = []
        self.best_sell_symbols_ex_2: List[Tuple[str, float]] = []

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

    def get_assigned_allowed_budget(self, src_exchange, row):
        available_budget = src_exchange.get_budget_sync()
        allowed_budget = self.trade_hy_params_obj.budget_factor * available_budget
        return allowed_budget * row[self.col_info_obj.symbol_eval_col_obj.budge_factor_col]

    def get_arbit_machine_seller_FIRST(self, row):
        # The seller (the first exchange) will be the destination exchange
        src_exchange = self.exchange_pair.get_second_exchange()
        return ArbitrageMachine(name=self.exchange_pair.name_first_seller,
                                src_exchange_platform=src_exchange,
                                dst_exchange_platform=self.exchange_pair.get_first_exchange(),
                                row=row,
                                col_info_obj=self.col_info_obj,
                                ex_price_cols=self.exchange_pair.get_all_price_cols(),
                                budget=self.get_assigned_allowed_budget(src_exchange, row),
                                debug=self.debug)

    def get_arbit_machine_seller_SECOND(self, row):
        # The seller (the second exchange) will be the destination exchange
        src_exchange = self.exchange_pair.get_first_exchange()
        return ArbitrageMachine(name=self.exchange_pair.name_second_seller,
                                src_exchange_platform=self.exchange_pair.get_first_exchange(),
                                dst_exchange_platform=self.exchange_pair.get_second_exchange(),
                                row=row,
                                col_info_obj=self.col_info_obj,
                                ex_price_cols=self.exchange_pair.get_all_price_cols(),
                                budget=self.get_assigned_allowed_budget(src_exchange, row),
                                debug=self.debug)

    def _create_arbitrage_machines(self, df_in):
        df = df_in.copy()

        arbitrage_machines = []
        arbitrage_machine = None
        for index, row in df.iterrows():
            if row[self.col_info_obj.price_diff_col] > 0:  # Binance is more expensive => Binance is the seller
                # We need to check/buy the coin on Coinbase, then, move it to Binance. Then, sell it on Binance.
                arbitrage_machine = self.get_arbit_machine_seller_FIRST(row)

            elif row[self.col_info_obj.price_diff_col] < 0:  # Coinbase is more expensive => Coinbase is the seller
                # We need to check/buy the coin on Binance, then, move it to Coinbase. Then, sell it on Coinbase.
                arbitrage_machine = self.get_arbit_machine_seller_SECOND(row)
            if row[self.col_info_obj.price_diff_col] == 0 or arbitrage_machine is None:
                # No opportunity
                pass
            else:
                # arbitrage_machine.create_trades(row, self.col_info_obj, self.trade_hy_params_obj.initial_budget)
                arbitrage_machines.append(arbitrage_machine)

        return arbitrage_machines

    def _assign_budget_to_arbitrage_machines(self, df_ranked):
        runnable_ex_machine_num = min(self.trade_hy_params_obj.num_of_top_symbols, len(df_ranked))
        df_ranked[self.col_info_obj.symbol_eval_col_obj.budge_factor_col] = df_ranked.apply(
            lambda row: uniform_budget_assigner(row, runnable_ex_machine_num), axis=1)
        return df_ranked

    async def create_arbitrage_machine_for_one_bucket(self, df_in):
        # We just work on the first bucket for now.
        df_bucket = self.get_bucket_organized_df(df_in)
        df_ranked = self.symbol_evaluator_obj.evaluate_then_rank_best_symbols(df_bucket, self.exchange_list)
        runnable_ex_machine_num = min(self.trade_hy_params_obj.num_of_top_symbols, len(df_bucket))
        df_budgeted = self._assign_budget_to_arbitrage_machines(df_ranked)
        df_selected = df_budgeted.iloc[:runnable_ex_machine_num]
        return self._create_arbitrage_machines(df_selected)

    async def break_df_to_positive_negative(self, df_in):
        df = df_in.copy()
        positive_df = df[df[self.col_info_obj.price_diff_col] > 0]
        negative_df = df[df[self.col_info_obj.price_diff_col] < 0]
        return positive_df, negative_df

    def find_best_symbols(self, df_in):
        # Divide the DataFrame into positive and negative groups
        df_positive = df_in[df_in[self.col_info_obj.price_diff_col] > 0]
        df_negative = df_in[df_in[self.col_info_obj.price_diff_col] < 0]

        # Find the best symbol for each group
        best_positive_values = (df_positive.iloc[0][self.col_info_obj.symbol_col],
                                df_positive.iloc[0][self.exchange_pair.first_exchange.price_col]) \
                            if not df_positive.empty else (None, None)

        best_negative_values = (df_negative.iloc[0][self.col_info_obj.symbol_col],
                                df_negative.iloc[0][self.exchange_pair.second_exchange.price_col]) \
                            if not df_negative.empty else (None, None)

        # Each of these 2 outputs is a tuple of (symbol, price)
        return best_positive_values, best_negative_values

    def update_best_sell_symbols_info_(self, df_in):
        best_positive_values, best_negative_values = self.find_best_symbols(df_in)
        self.best_sell_symbols_ex_1.append(best_positive_values)
        self.best_sell_symbols_ex_2.append(best_negative_values)

    async def create_and_run_arbit_machines(self, df_in):  # The main function that gets the dataframe
        self.update_best_sell_symbols_info_(df_in)
        arbitrage_machines = await self.create_arbitrage_machine_for_one_bucket(df_in)
        trade_runner_positive = TradeRunner(arbitrage_machines, self.debug)
        await trade_runner_positive.execute()
        # Todo: Define how many exchange machine you are going to run per tr

    # def _create_arbitrage_machines(self, df_in):
    #     df = df_in.copy()
    #
    #     arbitrage_machines = []
    #     arbitrage_machine = None
    #     for index, row in df.iterrows():
    #         if row[self.col_info_obj.price_diff_col] > 0:  # Binance is more expensive => Binance is the seller
    #             # We need to check/buy the coin on Coinbase, then, move it to Binance. Then, sell it on Binance.
    #             src_exchange = self._get_exchange(ExchangeNames.Coinbase)
    #             available_budget = src_exchange.get_budget_sync()
    #             arbitrage_machine = ArbitrageMachine(name="Coinbase_to_Binance",
    #                                                  src_exchange_platform=src_exchange,
    #                                                  dst_exchange_platform=self._get_exchange(ExchangeNames.Binance),
    #                                                  row=row,
    #                                                  col_info_obj=self.col_info_obj,
    #                                                  budget=self.get_assigned_allowed_budget(available_budget, row),
    #                                                  debug=self.debug)
    #
    #         elif row[self.col_info_obj.price_diff_col] < 0:  # Coinbase is more expensive => Coinbase is the seller
    #             # We need to check/buy the coin on Binance, then, move it to Coinbase. Then, sell it on Coinbase.
    #             src_exchange = self._get_exchange(ExchangeNames.Binance)
    #             available_budget = src_exchange.get_budget_sync()
    #             arbitrage_machine = ArbitrageMachine(name="Binance_to_Coinbase",
    #                                                  src_exchange_platform=src_exchange,
    #                                                  dst_exchange_platform=self._get_exchange(ExchangeNames.Coinbase),
    #                                                  row=row,
    #                                                  col_info_obj=self.col_info_obj,
    #                                                  budget=self.get_assigned_allowed_budget(available_budget, row),
    #                                                  debug=self.debug)
    #         if row[self.col_info_obj.price_diff_col] == 0 or arbitrage_machine is None:
    #             # No opportunity
    #             pass
    #         else:
    #             # arbitrage_machine.create_trades(row, self.col_info_obj, self.trade_hy_params_obj.initial_budget)
    #             arbitrage_machines.append(arbitrage_machine)
    #
    #     return arbitrage_machines

    # ToDO: What if all budget is in one platform: Move them using bitcoin to the other platform.
    # If a hhigher price crypto is already on the ghier price platform, then you can sell it, move the money to the cheaper platform. Then, buy, mive, sell.
    # YOu can so it as much as it is on the top of the diff_df.

# If you use a crypto for hft, and it is still on the top of the diff_df,
# then you can do it again.
# In this case, you have a loop over a crypto to keep buying and selling it.
# Last binancve bought: PONDUSDT
