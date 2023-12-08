import asyncio

import pandas as pd
from pandas import DataFrame
from typing import List, Optional, Dict

from src.exchange_code_bases.exchange_class import ExchangeAbstractClass
from src.exchange_arbitrage_pkg.optimization_metrics_pkg.bid_based_operation import calculate_bid_ask_spread
from src.exchange_arbitrage_pkg.optimization_metrics_pkg.liquidity_func import calculate_liquidity_from_order_book_depth
from src.exchange_arbitrage_pkg.optimization_metrics_pkg.market_impact import calculate_market_impact
from src.exchange_arbitrage_pkg.optimization_metrics_pkg.sell_buy_quantity_func import calculate_max_sell_quantity, \
    calculate_max_buy_quantity, get_max_sell_qty_by_diff
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter
from src.exchange_arbitrage_pkg.utils.outlier_detection import remove_outliers


class SymbolEvaluatorArbitrage:
    def __init__(self,
                 column_info_obj: ColumnInfoClass,
                 trade_hyper_parameters: TradeHyperParameter,
                 price_cols: List[str],
                 debug: bool):
        self.col_info = column_info_obj
        self.hype_params = trade_hyper_parameters

        self.bid_ask_spread_col = column_info_obj.symbol_eval_col_obj.bid_ask_spread_col
        self.liquidity_col = column_info_obj.symbol_eval_col_obj.liquidity_col
        self.max_sell_qty_col = column_info_obj.symbol_eval_col_obj.max_sell_qty_col
        self.max_buy_qty_col = column_info_obj.symbol_eval_col_obj.max_buy_qty_col
        self.market_impact_max_sell_col = column_info_obj.symbol_eval_col_obj.market_impact_max_sell_col

        self.max_trade_qty_col = column_info_obj.symbol_eval_col_obj.max_trade_qty_col
        self.quant_multiply_percent_col = column_info_obj.symbol_eval_col_obj.quant_multiply_percent_col
        self.max_gain_col = column_info_obj.symbol_eval_col_obj.max_gain_col
        self.min_price_col = column_info_obj.symbol_eval_col_obj.min_price_col
        self.market_impact_col = column_info_obj.symbol_eval_col_obj.market_impact_col
        # self.price_cols = [val for key, val in self.col_info.exchange_price_cols.items()]
        self.price_cols = price_cols
        self.order_book_df_dict = {}
        self.debug = debug

    def _calculate_liquidity(self, order_book):
        return calculate_liquidity_from_order_book_depth(order_book,
                                                         self.hype_params.price_range_percent)

    def _get_min_price(self, row):
        return min([row[col] for col in self.price_cols])

    def _get_max_price(self, row):
        return max([row[col] for col in self.price_cols])

    def _calculate_max_sell_quantity(self, order_book):
        return calculate_max_sell_quantity(order_book,
                                           self.hype_params.slippage_factor)

    def _get_max_sell_qty_by_min_price(self, order_book, row):
        return get_max_sell_qty_by_diff(order_book, self._get_min_price(row),
                                        self.hype_params.slippage_factor)

    def _calculate_max_buy_quantity(self, order_book, row):
        return calculate_max_buy_quantity(order_book,
                                          self._get_max_price(row),
                                          self.hype_params.slippage_factor)

    def add_market_impact_overall(self, df_in, row, index, exchange_index, exchange_name, order_book):
        df = df_in.copy()
        if row[self.col_info.price_diff_col] > 0:
            if exchange_index == 0:  # first exchange is more expensive => the seller
                df.loc[index, self.market_impact_col] = \
                    calculate_market_impact(order_book,
                                            df.loc[index, f'{exchange_name}_{self.max_sell_qty_col}'])
            else:
                pass
        else:
            if exchange_index == 0:
                pass
            else:
                df.loc[index, self.market_impact_col] = \
                    calculate_market_impact(order_book,
                                            df.loc[index, f'{exchange_name}_{self.max_sell_qty_col}'])
        return df

    def extract_symbol_metrics(self,
                               df_in,
                               index,
                               row,
                               exchange: ExchangeAbstractClass,
                               exchange_index: int,
                               order_book_df_dict: Dict[str, Optional[DataFrame]]):
        df = df_in.copy()
        exchange_name = exchange.name.value
        order_book_raw = exchange.get_order_book_sync(exchange.sync_client, row[self.col_info.symbol_col])
        order_book = remove_outliers(order_book_raw, self.hype_params.outlier_threshold)
        order_book.reset_index(inplace=True)
        order_book.drop(columns=['index'], inplace=True)

        order_book_df_dict[f'{exchange_name}_{row[self.col_info.symbol_col]}'] = order_book
        df.loc[index, f'{exchange_name}_{self.bid_ask_spread_col}'] = calculate_bid_ask_spread(order_book)
        df.loc[index, f'{exchange_name}_{self.liquidity_col}'] = self._calculate_liquidity(order_book)
        df.loc[index, f'{exchange_name}_{self.max_sell_qty_col}'] = self._get_max_sell_qty_by_min_price(order_book, row)
        df.loc[index, f'{exchange_name}_{self.max_buy_qty_col}'] = self._calculate_max_buy_quantity(order_book, row)
        df.loc[index, f'{exchange_name}_{self.market_impact_max_sell_col}'] = calculate_market_impact(
            order_book, df.loc[index, f'{exchange_name}_{self.max_sell_qty_col}'])
        df_market_impact = self.add_market_impact_overall(df, row, index, exchange_index, exchange_name, order_book)

        return df_market_impact, order_book_df_dict

    def evaluate_symbols_for_trade(self, df_in, exchange_list):
        df = df_in.copy()
        df[self.market_impact_col] = 0
        order_book_df_dict = {}
        for index, row in df.iterrows():
            for i, exchange in enumerate(exchange_list):
                df, order_book_df_dict = self.extract_symbol_metrics(df_in=df,
                                                                     index=index,
                                                                     row=row,
                                                                     exchange=exchange,
                                                                     exchange_index=i,
                                                                     order_book_df_dict=order_book_df_dict)
        return df  # Updated DataFrame with calculated metrics for both exchanges

    def extract_symbol_metrics_df(self, row, exchange: ExchangeAbstractClass, exchange_index: int):
        exchange_name_val = exchange.name.value
        order_book_raw = exchange.get_order_book_sync(exchange.sync_client, row[self.col_info.symbol_col])
        order_book = remove_outliers(order_book_raw, self.hype_params.outlier_threshold)
        order_book.reset_index(inplace=True)
        order_book.drop(columns=['index'], inplace=True)

        self.order_book_df_dict[f'{exchange_name_val}_{row[self.col_info.symbol_col]}'] = order_book
        row[f'{exchange_name_val}_{self.bid_ask_spread_col}'] = calculate_bid_ask_spread(order_book)
        row[f'{exchange_name_val}_{self.liquidity_col}'] = self._calculate_liquidity(order_book)
        row[f'{exchange_name_val}_{self.max_sell_qty_col}'] = self._get_max_sell_qty_by_min_price(order_book, row)
        row[f'{exchange_name_val}_{self.max_buy_qty_col}'] = self._calculate_max_buy_quantity(order_book, row)
        row[f'{exchange_name_val}_{self.market_impact_max_sell_col}'] = calculate_market_impact(
            order_book, row[f'{exchange_name_val}_{self.max_sell_qty_col}'])
        return row

    def evaluate_symbols_for_trade_df(self, df_in, exchange_list):
        df = df_in.copy()
        df[self.market_impact_col] = 0
        for i, exchange in enumerate(exchange_list):
            df = df.apply(lambda row: self.extract_symbol_metrics_df(row, exchange, i), axis=1)

        return df

    async def evaluate_symbols_for_trade_df_asymb(self, df_in, exchange_list):
        df = df_in.copy()
        df[self.market_impact_col] = 0

        async def process_row(row, exchange_list):
            for i, exchange in enumerate(exchange_list):
                row = await self.extract_symbol_metrics_df(row, exchange, i)
            return row

        # Process each row asynchronously
        tasks = [process_row(row, exchange_list) for _, row in df.iterrows()]
        processed_rows = await asyncio.gather(*tasks)

        # Reconstruct the DataFrame
        return pd.DataFrame(processed_rows, columns=df.columns)

    def add_min_price_and_gain(self, df_in):
        df = df_in.copy()
        min_price_series = df.apply(lambda x: min([x[col] for col in self.price_cols]), axis=1)
        df[self.min_price_col] = min_price_series

        df[self.max_gain_col] = df[self.col_info.current_price_diff_percentage_col] * \
                                df[self.max_trade_qty_col] * \
                                df[self.min_price_col]
        return df

    def calculate_max_trade_and_gain(self, df_in, exchange_list):
        df_evaluated = df_in.copy()

        def max_trade_qty(row):
            if row[self.col_info.price_diff_col] > 0:  # the first one (Binance) is more expensive.
                return min(row[f'{exchange_list[0].name.value}_{self.max_sell_qty_col}'],
                           row[f'{exchange_list[1].name.value}_{self.max_buy_qty_col}'])
            else:
                return min(row[f'{exchange_list[0].name.value}_{self.max_buy_qty_col}'],
                           row[f'{exchange_list[1].name.value}_{self.max_sell_qty_col}'])

        df_evaluated[self.max_trade_qty_col] = df_evaluated.apply(max_trade_qty, axis=1) \
            .astype(float).round(2)
        df_evaluated[self.quant_multiply_percent_col] = df_evaluated[self.max_trade_qty_col] * df_evaluated[
            self.col_info.current_price_diff_percentage_col]

        df_evaluated_gain = self.add_min_price_and_gain(df_evaluated)

        return df_evaluated_gain

    def evaluate_then_rank_best_symbols(self, df_in, exchange_pair):
        # exchange_names = [exchange.name.value for exchange in exchange_pair]
        exchange_names = exchange_pair.get_exchange_names_str_val()

        def get_average_liquidity(row):
            liquidity_cols = [f'{exchange_name}_{self.liquidity_col}' for exchange_name in exchange_names]
            average_liquidity = row[liquidity_cols].mean()
            return average_liquidity

        # df_evaluated = self.evaluate_symbols_for_trade(df_in, exchange_list)
        df_evaluated = self.evaluate_symbols_for_trade_df(df_in, exchange_pair.get_list_of_exchanges())
        df_evaluated[self.liquidity_col] = df_evaluated.apply(get_average_liquidity, axis=1)
        df_evaluated_gain = self.calculate_max_trade_and_gain(df_evaluated, exchange_pair.get_list_of_exchanges())
        # Updated sorting criteria
        sorting_col_tuples = [
            (self.max_gain_col, False),
            (self.liquidity_col, True),  # Higher liquidity is better
            (self.market_impact_col, True),  # Lower market impact is better
            (f'{exchange_names[0]}_{self.bid_ask_spread_col}', True),  # Higher liquidity is better
            (f'{exchange_names[1]}_{self.bid_ask_spread_col}', True),  # Higher liquidity is better
            # (self.bid_ask_spread_col, True),  # Lower spread is better
            (self.quant_multiply_percent_col, False),
            (self.max_trade_qty_col, False),
            (self.col_info.exchange_volume_cols.get("binance_volume_col", "binance_volume_24h"), False),
            (self.col_info.recency_col, False)]

        df_evaluated_gain.sort_values(
            by=[col[0] for col in sorting_col_tuples],
            ascending=[col[1] for col in sorting_col_tuples],
            inplace=True
        )

        if self.debug:
            cols = [col[0] for col in sorting_col_tuples] + [self.col_info.symbol_col,
                                                             'current_price_diff_percentage',
                                                             'price_diff_bi_cb']
            print("\n")
            print("Information after evaluation: ")
            num_row_to_show = 10
            selected_cols = ['current_time', 'symbol', 'binance_price', 'coinbase_price', 'price_diff_bi_cb',
                             'current_price_diff_percentage', self.col_info.bi_price_change_24h, 'recency']
            print("The extracted info is: ")
            print(df_evaluated_gain[cols].head(num_row_to_show).to_string())
            print("*" * 60)

        return df_evaluated_gain
