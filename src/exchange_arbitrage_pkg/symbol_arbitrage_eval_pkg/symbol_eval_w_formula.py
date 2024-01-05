from datetime import datetime

import pandas as pd

from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_symbol_utils import get_base_currency_bi_cb
from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_evaluator import SymbolEvaluatorArbitrageAbstract
from src.exchange_arbitrage_pkg.utils.outlier_detection import remove_outliers
from src.exchange_arbitrage_pkg.utils.python_utils.df_utils import convert_column_types
from test.exchange_arbitrage_pkg_test.symbol_arbit_eval_test.volume_computer import compute_symbol_eval_vector


class SymbolEvaluatorFormula(SymbolEvaluatorArbitrageAbstract):

    def get_fees_and_net_info(self, network_paired_cols):
        paired_fee_info_df = self.exchange_pair.get_paired_fee_info_df()
        network_selected_cols = [v for k, v in network_paired_cols.items()]
        is_net_default = paired_fee_info_df[network_paired_cols['net_is_default_col']]
        fee_withdraw_df = paired_fee_info_df.loc[is_net_default][network_selected_cols]
        return fee_withdraw_df

    def include_fee_df(self, df_in):
        network_paired_cols = self.exchange_pair.operation_executor.network_convertor_obj.paired_cols
        fee_withdraw_df_raw = self.get_fees_and_net_info(network_paired_cols)
        fee_withdraw_df = convert_column_types(fee_withdraw_df_raw)
        diff_df_containing_fees = pd.merge(df_in,
                                           fee_withdraw_df,
                                           left_on=self.col_info.base_coin_id_col,
                                           right_on=network_paired_cols['coin_id_col'],
                                           how='left')
        diff_df_containing_fees.rename(
            columns={network_paired_cols['net_withdraw_fee_col']: self.col_info.withdraw_fee_col},
            inplace=True)
        return diff_df_containing_fees

    def add_base_coin_id_col(self, df_in):
        df_in[self.col_info.base_coin_id_col] = df_in[self.col_info.symbol_col].apply(get_base_currency_bi_cb)
        return df_in

    def include_fee_and_other_info(self, df_in):
        df_w_coin_id = self.add_base_coin_id_col(df_in.copy())
        df_with_network_fee =  self.include_fee_df(df_w_coin_id)
        return df_with_network_fee

    def get_order_books(self, symbol, exchange_pair):
        # Initialize an empty list for collecting DataFrame objects
        orbk_cols = self.col_info.order_book_col_obj
        order_books_list = []

        for exchange in exchange_pair.get_all_exchanges():
            order_book_raw = exchange.get_order_book_sync(exchange.sync_client, symbol)
            order_book = remove_outliers(order_book_raw, self.hype_params.outlier_threshold)

            # Reset index and drop the original index column
            order_book.reset_index(inplace=True, drop=True)

            # Add a new column with the symbol
            order_book[orbk_cols.symbol_col] = symbol
            order_book[orbk_cols.exchange_name_col] = exchange.name.value
            order_book[orbk_cols.trans_fee_col] = exchange.get_transaction_fee_rate()

            # Append this order book to the list
            order_books_list.append(order_book)

        # Concatenate all DataFrames in the list
        all_exchanges_order_books = pd.concat(order_books_list, ignore_index=True)

        return all_exchanges_order_books

    def insert_in_database(self, df_in):
        df = df_in.copy()
        df[self.col_info.current_time_col] = self.current_time
        df[self.col_info.order_book_col_obj.download_time_col] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:23]
        df = convert_column_types(df)
        self.db_handler.insert_order_book_info_df(df)

    def score_symbol(self, row):
        #ToDo: >>>> You can pass a new ex_pair for each row
        symbol = row[self.col_info.symbol_col]
        new_order_books = self.get_order_books(symbol, self.exchange_pair)
        self.all_symbols_order_book_df = pd.concat([self.all_symbols_order_book_df, new_order_books], ignore_index=True)
        self.insert_in_database(new_order_books)
        return compute_symbol_eval_vector(order_book_df=new_order_books,
                                          withdrawal_fee=row[self.col_info.withdraw_fee_col],  # Change it !!!!!
                                          src_exchange_name=row[self.col_info.src_exchange_name_col],  # Change it!!!!!
                                          dst_exchange_name=row[self.col_info.dst_exchange_name_col],  # Change it!!!!!
                                          src_transaction_fee_rate=self.exchange_pair.pick_exchange(row[self.col_info.src_exchange_name_col]).get_transaction_fee_rate(),
                                          dst_transaction_fee_rate=self.exchange_pair.pick_exchange(row[self.col_info.dst_exchange_name_col]).get_transaction_fee_rate(),
                                          col_info=self.col_info)
    # withdrawal_fee_col = self.exchange_pair.operation_executor.network_convertor_obj.paired_cols['net_withdraw_fee_col']
    #ToDo: If the account has a symbol already, then, iyt just needs to look in to the sell part (buy sside on the dst).
    # There is a chance that the volume to buy may be much lower that the value that we can sell.
    # Then, if we have it, we do not need to worry about the low available volume to buy it.

    def _include_symbol_goodness(self, df_in):
        df = df_in.copy()
        condition = (df[self.col_info.order_book_col_obj.profit_col] > 0)
        df[self.col_info.symbol_eval_col_obj.is_good_to_trade_col] = condition
        return df

    def evaluate_then_rank_best_symbols(self, df_in):
        df = df_in.copy()
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df = self.include_fee_and_other_info(df)
        order_book_eval_out_cols = self.col_info.order_book_col_obj.get_order_eval_out_cols()
        df[order_book_eval_out_cols] = df.apply(self.score_symbol,
                                                axis=1,
                                                result_type='expand')
        df_sorted = df.sort_values(by=self.col_info.order_book_col_obj.profit_col,
                                   ascending=False)
        df_result = self._include_symbol_goodness(df_sorted)
        return df_result


