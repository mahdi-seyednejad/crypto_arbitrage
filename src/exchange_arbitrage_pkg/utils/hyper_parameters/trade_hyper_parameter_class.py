from typing import Optional


class WaitTimeDeposit:
    def __init__(self,
                 check_interval: int = 5,
                 timeout: int = 500,
                 amount_loss: float = 0.05,
                 second_chance: bool = True):
        """
        :param check_interval:
        :type check_interval:
        :param timeout:
        :type timeout:
        :param amount_loss:
        :type amount_loss:
        """
        self.check_interval = check_interval
        self.timeout = timeout
        self.amount_loss = amount_loss
        self.second_chance = second_chance


# ToDo: Put the diff df maker parameters here.
# class DiffDataFrameParams:
#
class DiffMakerRunConfig:
    def __init__(self,
                 sleep_time: int = 2,
                 run_number: Optional[int] = 10,
                 sample_size: Optional[int] = 50,
                 storage_dir: Optional[str] = None):
        self.sleep_time = sleep_time
        self.run_number = run_number
        self.sample_size = sample_size
        self.storage_dir = storage_dir


class TradeHyperParameter:
    def __init__(self,
                 trade_bucket_size: int,  # Number of the top of the diff df to be calculated for trading.
                 order_book_fetch_level: int,
                 acceptable_slippage: float = 0.5,
                 price_range_percent: float = 0.5,
                 initial_budget: Optional[float] = 1000.0,
                 outlier_threshold: float = 2.5,
                 fetch_period: int = 2,  # in seconds: How long sleep before fetching prices and creating new diff df
                 # run_number: Optional[int] = 10,  # How many times to run the diff df generator loop/ None means forever
                 num_of_top_symbols=1,  # Number of top evaluated symbols to be able to run their exchange machine
                 budget_factor=0.5,  # How much of the budget to be used for each exchange machine
                 acceptable_amount_diff_percent=0.5,  # How much of the budget to be used for each exchange machine
                 min_acceptable_budget=10,  # Minimum budget on an exchange to run a cross exchange machine
                 secondary_symbol_rank=2,  # The rank of the secondary symbol in the top symbols list.
                 num_rank_hard_cut_off=None,
                 wait_time_deposit: Optional[WaitTimeDeposit] = WaitTimeDeposit(),
                 diff_maker_config: DiffMakerRunConfig = DiffMakerRunConfig(),
                 ):
        """
        :param trade_bucket_size: Number of the top of the diff df to be calculated for trading.
        :type trade_bucket_size: int
        :param order_book_fetch_level:
        :type order_book_fetch_level:
        :param acceptable_slippage:
        :type acceptable_slippage:
        :param price_range_percent:
        :type price_range_percent:
        :param initial_budget:
        :type initial_budget:
        :param outlier_threshold:
        :type outlier_threshold:
        :param fetch_period:
        :type fetch_period:
        :param run_number:
        :type run_number:
        :param num_of_top_symbols:
        :type num_of_top_symbols:
        :param budget_factor:
        :type budget_factor:
        :param acceptable_amount_diff_percent:
        :type acceptable_amount_diff_percent:
        :param min_acceptable_budget:
        :type min_acceptable_budget:
        :param secondary_symbol_rank:
        :type secondary_symbol_rank:
        :param num_rank_hard_cut_off:  Number of symbols being considered to have a arbitrage machines after
            symbol evaluation process. If None, it won't be applied.
            It is useful for following just one arbitrage machine in one experiment.
        :type num_rank_hard_cut_off:
        """

        self.trade_bucket_size = trade_bucket_size
        self.order_book_fetch_level = order_book_fetch_level
        self.slippage_factor = acceptable_slippage
        self.price_range_percent = price_range_percent
        self.initial_budget = initial_budget
        self.outlier_threshold = outlier_threshold
        self.fetch_period = fetch_period
        # self.run_number = run_number
        self.num_of_top_symbols = num_of_top_symbols
        self.budget_factor = budget_factor
        self.acceptable_amount_diff_percent = acceptable_amount_diff_percent
        self.min_acceptable_budget = min_acceptable_budget
        self.secondary_symbol_rank = secondary_symbol_rank
        self.num_rank_hard_cut_off = num_rank_hard_cut_off
        self.wait_time_deposit = wait_time_deposit
        self.diff_maker_config = diff_maker_config
