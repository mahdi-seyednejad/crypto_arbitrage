from typing import Optional


# class TradeBucket:

class TradeHyperParameter:
    def __init__(self,
                 trade_bucket_size: int,  # Number of the top of the diff df to be calculated for trading.
                 order_book_fetch_level: int,
                 acceptable_slippage: float = 0.5,
                 price_range_percent: float = 0.5,
                 initial_budget: Optional[float] = 1000.0,
                 outlier_threshold: float = 2.5,
                 fetch_period: int = 2, # in seconds: How long sleep before fetching prices and creating new diff df
                 run_number: Optional[int] = 10, # How many times to run the diff df generator loop/ None means forever
                 num_of_top_symbols=1, # Number of top evaluated symbols to be able to run their exchange machine
                 budget_factor=0.5, # How much of the budget to be used for each exchange machine
                 ):
        self.trade_bucket_size = trade_bucket_size
        self.order_book_fetch_level = order_book_fetch_level
        self.slippage_factor = acceptable_slippage
        self.price_range_percent = price_range_percent
        self.initial_budget = initial_budget
        self.outlier_threshold = outlier_threshold
        self.fetch_period = fetch_period
        self.run_number = run_number
        self.num_of_top_symbols = num_of_top_symbols
        self.budget_factor = budget_factor

