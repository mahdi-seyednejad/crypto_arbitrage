from src.exchange_arbitrage_pkg.optimization_metrics_pkg.bid_based_operation import calculate_bid_ask_spread
from src.exchange_arbitrage_pkg.optimization_metrics_pkg.liquidity_func import calculate_liquidity_from_order_book_depth
from src.exchange_arbitrage_pkg.optimization_metrics_pkg.sell_quantity_func import calculate_max_sell_quantity


class SymbolEvaluatorArbitrage:
    def __init__(self,
                 acceptable_slippage,
                 price_range_percent):
        self.acceptable_slippage = acceptable_slippage
        self.price_range_percent = price_range_percent

    def _calculate_liquidity(self, order_book):
        return calculate_liquidity_from_order_book_depth(order_book, self.price_range_percent)

    def _calculate_max_sell_quantity(self, order_book):
        return calculate_max_sell_quantity(order_book, self.acceptable_slippage)

    def evaluate_symbols_for_trade(self,
                                   df_in,
                                   order_book_fetcher,
                                   symbol_col):
        '''
        We want to calculate max sell quantity,
        and other things to make decision either to trade a crypto or not.
        :param df_in:
        :type df_in:
        :param order_book_fetcher:
        :type order_book_fetcher:
        :param symbol_col:
        :type symbol_col:
        :return:
        :rtype:
        '''
        df = df_in.copy()
        df['order_book'] = df.apply(lambda row: order_book_fetcher(row[symbol_col]), axis=1)
        df['bid_ask_spread'] = df['order_book'].apply(calculate_bid_ask_spread)
        df['liquidity'] = df['order_book'].apply(self._calculate_liquidity)
        df['max_sell_quantity'] = df['order_book'].apply(self._calculate_max_sell_quantity)
        return df


