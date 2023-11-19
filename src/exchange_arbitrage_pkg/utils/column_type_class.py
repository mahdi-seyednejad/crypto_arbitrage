from typing import Dict

bi_cb_exchange_price_cols = {"binance_price_col": "binance_price",
                             "coinbase_price_col": "coinbase_price"}


class ColumnSymbolEvalClass:
    def __init__(self,
                 max_sell_qty_col='max_sell_quantity',
                 max_buy_qty_col='max_buy_quantity',
                 bid_ask_spread_col='bid_ask_spread',
                 liquidity_col='liquidity',
                 market_impact_max_sell_col='market_impact_max_sell',
                 market_impact_col='market_impact',
                 is_good_to_trade_col='is_good_to_trade',
                 max_trade_qty_col='max_trade_quantity',
                 quant_multiply_percent_col='quant_multiply_percent',
                 optional_prefix: str = '',
                 ):
        self.max_sell_qty_col = f"{optional_prefix}_{max_sell_qty_col}"
        self.bid_ask_spread_col = f"{optional_prefix}_{bid_ask_spread_col}"
        self.liquidity_col = f"{optional_prefix}_{liquidity_col}"
        self.market_impact_max_sell_col = f"{optional_prefix}_{market_impact_max_sell_col}"
        self.market_impact_col = f"{optional_prefix}_{market_impact_col}"
        self.is_good_to_trade_col = f"{optional_prefix}_{is_good_to_trade_col}"
        self.max_buy_qty_col = f"{optional_prefix}_{max_buy_qty_col}"
        self.max_trade_qty_col = f"{optional_prefix}_{max_trade_qty_col}"
        self.quant_multiply_percent_col = f"{optional_prefix}_{quant_multiply_percent_col}"
        self.min_price_col = f"{optional_prefix}_min_price"  # min(binance_price_col, coinbase_price_col)
        self.max_gain_col = f"{optional_prefix}_max_gain"  # diff percent * max_trade_qty_col * current_price_diff_percentage_col


class ColumnInfoClass:
    def __init__(self,
                 symbol_col="symbol",
                 volume_col="volume",
                 exchange_price_cols: Dict[str, str] = None, # These things should be kept in the exchange. Not here
                 exchange_volume_cols: Dict[str, str] = None,
                 price_diff_col="price_diff_bi_cb",
                 current_price_diff_percentage_col="current_price_diff_percentage",
                 price_change_24h_col="price_change_24h",
                 recency_col="recency",
                 current_time_col="current_time",
                 bi_price_change_24h="binance_priceChangePercent_24h",
                 is_good_to_trade_col="is_good_to_trade_col",
                 symbol_eval_col_obj: ColumnSymbolEvalClass = ColumnSymbolEvalClass()
                 ):
        self.symbol_col = symbol_col
        self.volume_col = volume_col
        self.price_diff_col = price_diff_col
        self.current_price_diff_percentage_col = current_price_diff_percentage_col
        self.price_change_24h_col = price_change_24h_col
        self.recency_col = recency_col
        self.current_time_col = current_time_col
        self.bi_price_change_24h = bi_price_change_24h
        self.is_good_to_trade_col = is_good_to_trade_col
        self.symbol_eval_col_obj = symbol_eval_col_obj

        if exchange_volume_cols is None:
            self.exchange_volume_cols = {"binance_volume_col": "binance_volume_24h"}
        else:
            self.exchange_volume_cols = exchange_volume_cols

        if exchange_price_cols is None:
            self.exchange_price_cols = bi_cb_exchange_price_cols
        else:
            self.exchange_price_cols = exchange_price_cols

# class OutputColumnClass:
#     def __init__(self, output_columns, bi_price_change_24h):
#         self.output_columns = output_columns
#         self.bi_price_change_24h = bi_price_change_24h
#
#
# class ColumnTypeClass:
#     def __init__(self,
#                  initial_columns: InitialColumnClass,
#                  output_columns:OutputColumnClass,
#                  **kwargs):
#         self.initial_columns = initial_columns
#         self.output_columns = output_columns
#         self.kwargs = kwargs
