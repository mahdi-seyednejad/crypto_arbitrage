
# class TradeBucket:

class TradeHyperParameter:
    def __init__(self,
                 trade_bucket_size: int,  # Number of the top of the diff df to be calculated for trading.
                 order_book_fetch_level: int,
                 acceptable_slippage: float = 0.5,
                 price_range_percent: float = 0.5,
                 initial_budget: float = 1000.0,
                 ):
        self.trade_bucket_size = trade_bucket_size
        self.order_book_fetch_level = order_book_fetch_level
        self.acceptable_slippage = acceptable_slippage
        self.price_range_percent = price_range_percent
        self.initial_budget = initial_budget

