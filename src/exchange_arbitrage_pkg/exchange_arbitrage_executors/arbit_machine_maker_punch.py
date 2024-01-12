from datetime import datetime
from typing import List, Tuple

from src.data_pkg.ts_db.ts_db_handler import DbHandler
from src.exchange_arbitrage_pkg.budget_manager.budget_assigner.simple_budget_assigner import uniform_budget_assigner
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_double import \
    ArbitrageMachinePunches
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.exchange_arbitrage_utils import find_best_backup_values, \
    BestSymbolStructure
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.exchange_arbitrage_utils import get_sec_symbol_and_price
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_eval_w_formula import SymbolEvaluatorFormula
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_evaluator import SymbolEvaluatorArbitrage, \
    SymbolEvaluatorArbitrageAbstract
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_base import TradeRunner
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter
from src.exchange_arbitrage_pkg.utils.python_utils.df_utils import convert_column_types
from src.exchange_code_bases.exchange_class.exchange_pair_class import ExchangePair


class ArbitrageMachineMakerPunch:
    def __init__(self,
                 exchange_pair: ExchangePair,
                 col_info_obj: ColumnInfoClass,
                 trade_hy_params_obj: TradeHyperParameter,
                 db_handler: DbHandler,
                 debug: bool):
        self.exchange_pair = exchange_pair
        self.exchange_pair.set_all_budgets(trade_hy_params_obj.initial_budget)
        self.col_info_obj = col_info_obj
        self.trade_hy_params_obj = trade_hy_params_obj
        self.db_handler = db_handler
        self.debug = debug
        self.symbol_evaluator_obj = SymbolEvaluatorFormula(column_info_obj=self.col_info_obj,
                                                           trade_hyper_parameters=self.trade_hy_params_obj,
                                                           exchange_pair=self.exchange_pair,
                                                           db_handler=self.db_handler,
                                                           debug=debug)
        self.is_good_to_trade_col = col_info_obj.symbol_eval_col_obj.is_good_to_trade_col
        self.best_sell_symbols_ex_1: List[BestSymbolStructure] = []
        self.best_sell_symbols_ex_2: List[BestSymbolStructure] = []
        self.best_backup_rank_symbols_ex_1: List[BestSymbolStructure] = []
        self.best_backup_rank_symbols_ex_2: List[BestSymbolStructure] = []
        self.runnable_ex_machine_num = min(self.trade_hy_params_obj.num_of_top_symbols,
                                           self.trade_hy_params_obj.trade_bucket_size)

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

    def _get_ex_pair(self):
        return self.exchange_pair

    def _create_arbit_machine_per_row(self, row, ex_pair, is_seller_first, secondary):
        if is_seller_first:
            name = ex_pair.name_first_seller
            src_exchange = ex_pair.get_second_exchange()
            dst_exchange = ex_pair.get_first_exchange()
        else:
            name = ex_pair.name_second_seller
            src_exchange = ex_pair.get_first_exchange()
            dst_exchange = ex_pair.get_second_exchange()

        return ArbitrageMachinePunches(name=name,
                                       src_exchange_platform=src_exchange,
                                       dst_exchange_platform=dst_exchange,
                                       row=row,
                                       col_info_obj=self.col_info_obj,
                                       ex_price_cols=ex_pair.get_all_price_cols(),
                                       budget=self.get_assigned_allowed_budget(src_exchange, row),
                                       min_acceptable_budget=self.trade_hy_params_obj.min_acceptable_budget,
                                       secondary_symbol=secondary.symbol,
                                       secondary_symbol_price=secondary.price,
                                       secondary_symbol_withdraw_fee=secondary.withdraw_fee,
                                       operation_executor=ex_pair.get_operation_executor(),
                                       wait_time_info=self.trade_hy_params_obj.wait_time_deposit,
                                       debug=self.debug)

    def get_arbit_machine_seller_FIRST(self, row):
        exchange_pair = self._get_ex_pair()
        # The seller (the first exchange) will be the destination exchange
        secondary = get_sec_symbol_and_price(self.best_sell_symbols_ex_2, self.best_backup_rank_symbols_ex_2)
        return self._create_arbit_machine_per_row(row=row,
                                                  ex_pair=exchange_pair,
                                                  is_seller_first=True,
                                                  secondary=secondary)

    def get_arbit_machine_seller_SECOND(self, row):
        exchange_pair = self._get_ex_pair()
        secondary = get_sec_symbol_and_price(self.best_sell_symbols_ex_2, self.best_backup_rank_symbols_ex_2)
        return self._create_arbit_machine_per_row(row=row,
                                                  ex_pair=exchange_pair,
                                                  is_seller_first=False,
                                                  secondary=secondary)

    def decide_arbitrage_machine(self, row):
        if row[self.col_info_obj.price_diff_col] > 0:  # Binance is more expensive => Binance is the seller
            # We need to check/buy the coin on Coinbase, then, move it to Binance. Then, sell it on Binance.
            return self.get_arbit_machine_seller_FIRST(row)
        elif row[self.col_info_obj.price_diff_col] < 0:  # Coinbase is more expensive => Coinbase is the seller
            # We need to check/buy the coin on Binance, then, move it to Coinbase. Then, sell it on Coinbase.
            return self.get_arbit_machine_seller_SECOND(row)
        else:
            return None

    def _create_arbitrage_machines(self, df_in):
        # ToDo: This should be the place to ge the secondary symbol and its price
        df = df_in.copy()
        arbitrage_machines = df.apply(self.decide_arbitrage_machine, axis=1)
        return arbitrage_machines[arbitrage_machines.notnull()].tolist()

    def _assign_budget_to_arbitrage_machines(self, df_ranked):
        runnable_ex_machine_num = min(self.trade_hy_params_obj.num_of_top_symbols, len(df_ranked))
        df_ranked[self.col_info_obj.symbol_eval_col_obj.budge_factor_col] = df_ranked.apply(
            lambda row: uniform_budget_assigner(row, runnable_ex_machine_num), axis=1)
        return df_ranked

    def _filter_bad_symbols(self, df_evaluated_ranked):
        df = df_evaluated_ranked.copy()
        df = df[df[self.col_info_obj.symbol_eval_col_obj.is_good_to_trade_col] == True]
        return df

    def _insert_evaluated_symbols_to_db(self, df_in):
        df = df_in.copy()
        df = convert_column_types(df)
        df[self.col_info_obj.current_time_col] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db_handler.insert_evaluated_symbols(df)

    async def _create_arbitrage_machine_for_one_bucket(self, df_in):
        # ToDo: Make a source and destination exchange list and iterate over them.
        # We just work on the first bucket for now.
        df_bucket = self.get_bucket_organized_df(df_in)
        # df_budgeted = self._assign_budget_to_arbitrage_machines(df_bucket)

        df_ranked = self.symbol_evaluator_obj \
            .evaluate_then_rank_best_symbols(df_in=df_bucket)

        # self.db_handler.insert_evaluated_symbols(df_ranked)
        self._insert_evaluated_symbols_to_db(df_ranked)
        if self.debug:
            print("The evaluated symbols are: ")
            print(df_ranked.to_string())

        df_filtered = self._filter_bad_symbols(df_ranked)

        if len(df_filtered) == 0:
            return []

        df_budgeted = self._assign_budget_to_arbitrage_machines(df_filtered)

        df_selected = df_budgeted.iloc[:self.runnable_ex_machine_num]
        if self.trade_hy_params_obj.num_rank_hard_cut_off not in [None, 0]:
            df_selected = df_budgeted.iloc[:self.trade_hy_params_obj.num_rank_hard_cut_off]

        self._update_best_sell_symbols_info_(df_selected)
        return self._create_arbitrage_machines(df_selected)

    def _extract_best_secondary(self, df_in, rank):
        # Adjust rank to be zero-indexed for DataFrame indexing
        rank_index = rank - 1

        # Divide the DataFrame into positive and negative groups
        df_positive = df_in[df_in[self.col_info_obj.price_diff_col] > 0]
        df_negative = df_in[df_in[self.col_info_obj.price_diff_col] < 0]

        # Find the best symbol for each group, based on the specified rank
        if len(df_positive) > rank_index:
            best_positive_values = BestSymbolStructure(
                symbol=df_positive.iloc[rank_index][self.col_info_obj.symbol_col],
                price=df_positive.iloc[rank_index][
                    self.exchange_pair.first_exchange.price_col],
                withdraw_fee=df_positive.iloc[rank_index][
                    self.col_info_obj.withdraw_fee_col])
        else:
            best_positive_values = BestSymbolStructure(None, None, None)

        if len(df_negative) > rank_index:
            best_negative_values = BestSymbolStructure(
                symbol=df_negative.iloc[rank_index][self.col_info_obj.symbol_col],
                price=df_negative.iloc[rank_index][
                    self.exchange_pair.second_exchange.price_col],
                withdraw_fee=df_negative.iloc[rank_index][
                    self.col_info_obj.withdraw_fee_col])
        else:
            best_negative_values = BestSymbolStructure(None, None, None)

        # Each of these 2 outputs is a tuple of (symbol, price)
        return best_positive_values, best_negative_values

    def _update_best_sell_symbols_info_(self, df_in):
        best_positive_values, \
            best_negative_values = self._extract_best_secondary(df_in,
                                                                self.trade_hy_params_obj.secondary_symbol_rank)
        best_backup_pos, best_backup_neg = find_best_backup_values(df_in=df_in,
                                                                   backup_rank_col=self.col_info_obj.bi_price_change_24h,
                                                                   rank=self.trade_hy_params_obj.secondary_symbol_rank,
                                                                   symbol_col=self.col_info_obj.symbol_col,
                                                                   price_col=self.exchange_pair.first_exchange.price_col,
                                                                   price_diff_col=self.col_info_obj.price_diff_col,
                                                                   withdraw_fee_col=self.col_info_obj.withdraw_fee_col)
        self.best_backup_rank_symbols_ex_1.append(best_backup_pos)
        self.best_backup_rank_symbols_ex_2.append(best_backup_neg)
        self.best_sell_symbols_ex_1.append(best_positive_values)
        self.best_sell_symbols_ex_2.append(best_negative_values)

    async def create_and_run_arbit_machines(self, df_in):  # The main function that gets the dataframe
        # self._update_best_sell_symbols_info_(df_in)
        #ToDo: IMPORTANT!!!!! You need to use one API per symbol.
        # There is a chance that the API is getting blocked due to frequent requests.
        arbitrage_machines = await self._create_arbitrage_machine_for_one_bucket(df_in)
        trade_runner_positive = TradeRunner(arbitrage_machines, self.debug)
        await trade_runner_positive.execute()
