from typing import Dict


class ColumnOrderBookClass:
    def __init__(self,
                 symbol_col='symbol',
                 price_col='price',
                 volume_col='volume',
                 side_col='side',
                 exchange_name_col='exchange_name',
                 num_orders_col='num_orders',
                 trans_fee_col='transaction_fee',
                 profit_col='profit',
                 spent_money_col='spent_money',
                 sold_money_col='sold_money',
                 trading_volume_col='trading_volume',
                 download_time_col='download_time'
                 ):
        self.symbol_col = symbol_col
        self.price_col = price_col
        self.volume_col = volume_col
        self.side_col = side_col
        self.exchange_name_col = exchange_name_col
        self.num_orders_col = num_orders_col
        self.trans_fee_col = trans_fee_col
        self.profit_col = profit_col
        self.spent_money_col = spent_money_col
        self.sold_money_col = sold_money_col
        self.trading_volume_col = trading_volume_col
        self.download_time_col = download_time_col

    def get_order_eval_out_cols(self):
        return [self.profit_col, self.spent_money_col, self.sold_money_col, self.trading_volume_col]


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
                 budge_factor_col='budget_factor',
                 budget_col='budget',
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
        self.budge_factor_col = f"{optional_prefix}_{budge_factor_col}"
        self.budget_col = f"{optional_prefix}_{budget_col}"


class ColumnInfoClass:
    def __init__(self,
                 symbol_col="symbol",
                 volume_col="volume",
                 base_coin_id_col="base_coin_id",
                 src_exchange_name_col="src_exchange_name",
                 dst_exchange_name_col="dst_exchange_name",
                 # exchange_price_cols: Dict[str, str] = None, # These things should be kept in the exchange. Not here
                 exchange_volume_cols: Dict[str, str] = None,
                 price_diff_col="price_diff_bi_cb",
                 current_price_diff_percentage_col="current_price_diff_percentage",
                 price_change_24h_col="price_change_24h",
                 recency_col="recency",
                 current_time_col="system_time",
                 bi_price_change_24h="binance_price_change_percent_24h",
                 is_good_to_trade_col="is_good_to_trade_col",
                 withdraw_fee_col="withdraw_fee",
                 symbol_eval_col_obj: ColumnSymbolEvalClass = ColumnSymbolEvalClass(),
                 order_book_col_obj: ColumnOrderBookClass = ColumnOrderBookClass()
                 ):
        self.symbol_col = symbol_col
        self.volume_col = volume_col
        self.base_coin_id_col = base_coin_id_col
        self.src_exchange_name_col = src_exchange_name_col
        self.dst_exchange_name_col = dst_exchange_name_col
        self.price_diff_col = price_diff_col
        self.current_price_diff_percentage_col = current_price_diff_percentage_col
        self.price_change_24h_col = price_change_24h_col
        self.recency_col = recency_col
        self.current_time_col = current_time_col
        self.bi_price_change_24h = bi_price_change_24h
        self.is_good_to_trade_col = is_good_to_trade_col
        self.withdraw_fee_col = withdraw_fee_col
        self.symbol_eval_col_obj = symbol_eval_col_obj

        if exchange_volume_cols is None:
            self.exchange_volume_cols = {"binance_volume_col": "binance_volume_24h"}
        else:
            self.exchange_volume_cols = exchange_volume_cols

        self.order_book_col_obj = order_book_col_obj

    def get_max_trade_qty_col(self):
        return self.symbol_eval_col_obj.max_trade_qty_col
