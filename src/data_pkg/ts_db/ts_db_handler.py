from typing import Dict, Optional

from src.data_pkg.ts_db.table_names_ds import TableNames
from src.data_pkg.ts_db.time_scale_db_operations import TimeScaleClass


class DbHandler:
    def __init__(self,
                 time_column: str,
                 table_names: TableNames,
                 symbol_col="symbol",
                 date_as_index: bool = True,
                 debug=True):
        self.ts_obj: TimeScaleClass = TimeScaleClass()
        self.time_column = time_column
        self.date_as_index = date_as_index
        self.stream_diff_table = table_names.get_stream_table_name()
        self.agg_diff_table = table_names.get_agg_table_name()
        self.evaluated_symbols_table = table_names.get_evaluated_symbols_table_name()
        self.order_book_table = table_names.get_order_book_table_name()
        self.symbol_col = symbol_col
        self.debug = debug

    def _insert_a_df_to_db(self, df, table_name):
        self.ts_obj.insert_df_to_tsdb(df_in=df,
                                      table_name=table_name,
                                      time_column=self.time_column,
                                      date_as_index=self.date_as_index,
                                      primary_keys=[self.symbol_col],
                                      debug=self.debug)

    def insert_stream_diff_data_df(self, df):
        self._insert_a_df_to_db(df, self.stream_diff_table)
        # self.ts_obj.insert_df_to_tsdb(df_in=df,
        #                               table_name=self.stream_diff_table,
        #                               time_column=self.time_column,
        #                               date_as_index=self.date_as_index,
        #                               symbol_col=self.symbol_col,
        #                               debug=self.debug)

    def insert_agg_diff_data_df(self, df):
        self._insert_a_df_to_db(df, self.agg_diff_table)
        # self.ts_obj.insert_df_to_tsdb(df_in=df,
        #                               table_name=self.agg_diff_table,
        #                               time_column=self.time_column,
        #                               date_as_index=self.date_as_index,
        #                               symbol_col=self.symbol_col,
        #                               debug=self.debug)

    def insert_evaluated_symbols(self, df):
        self._insert_a_df_to_db(df, self.evaluated_symbols_table)
        # self.ts_obj.insert_df_to_tsdb(df_in=df,
        #                               table_name=self.evaluated_symbols_table,
        #                               time_column=self.time_column,
        #                               date_as_index=self.date_as_index,
        #                               symbol_col=self.symbol_col,
        #                               debug=self.debug)

    def insert_order_book_info_df(self, df):
        self._insert_a_df_to_db(df, self.order_book_table)

        # self.ts_obj.insert_df_to_tsdb(df_in=df,
        #                               table_name=self.order_book_table,
        #                               time_column=self.time_column,
        #                               date_as_index=self.date_as_index,
        #                               symbol_col=self.symbol_col,
        #                               debug=self.debug)

    # def insert_single_row(self, row):
    #     self.ts_obj.insert_single_row_tsdb(row,
    #                                        self.table_name,
    #                                        self.time_column,
    #                                        self.symbol,
    #                                        self.date_as_index,
    #                                        self.bar_length,
    #                                        self.debug)
    #
    # def insert_decision_info(self, decision_dict, time_key):
    #     decision_info_db_row = {k: v for k, v in decision_dict.items() if 'symbol' not in k}
    #     self.ts_obj.insert_dict_to_tsdb(data_dict=decision_info_db_row,
    #                                     table_name=self.decision_table,
    #                                     time_key=time_key,
    #                                     time_column="Date",
    #                                     symbol=self.symbol,
    #                                     interval=self.bar_length,
    #                                     debug=self.debug)
