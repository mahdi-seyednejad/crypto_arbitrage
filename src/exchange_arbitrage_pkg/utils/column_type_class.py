from typing import Dict

exchange_price_cols = {"binance_price_col": "binance_price",
                       "coinbase_price_col": "coinbase_price"}

class ColumnClass:
    def __init__(self,
                 symbol_col="symbol",
                 exchange_price_cols: Dict[str, str] = None,
                 price_diff_col="price_diff_bi_cb",
                 current_price_diff_percentage_col="current_price_diff_percentage",
                 price_change_24h_col="price_change_24h",
                 recency_col="recency",
                 current_time_col="current_time",
                 bi_price_change_24h="binance_priceChangePercent_24h"):
        self.symbol_col = symbol_col
        self.exchange_price_cols = exchange_price_cols
        self.price_diff_col = price_diff_col
        self.current_price_diff_percentage_col = current_price_diff_percentage_col
        self.price_change_24h_col = price_change_24h_col
        self.recency_col = recency_col
        self.current_time_col = current_time_col
        self.bi_price_change_24h = bi_price_change_24h

        if self.exchange_price_cols is None:
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


