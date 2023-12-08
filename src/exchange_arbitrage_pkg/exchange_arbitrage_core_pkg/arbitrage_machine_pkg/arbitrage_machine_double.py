from src.exchange_arbitrage_pkg.broker_utils.quantity_calculation import calculate_quantity
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.cross_punch import \
    CrossPunch
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.hook_punch import \
    HookPunch
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.price_utils.amount_conversion import convert_main_amount_to_secondary
from src.exchange_code_bases.exchange_class.base_exchange_class import ExchangeAbstractClass


class ArbitrageMachinePunches:
    def __init__(self,
                 name,
                 src_exchange_platform: ExchangeAbstractClass,
                 dst_exchange_platform: ExchangeAbstractClass,
                 row,
                 col_info_obj: ColumnInfoClass,
                 ex_price_cols,
                 budget,
                 min_acceptable_budget,
                 secondary_symbol, # A good symbol with higher price on src
                 secondary_symbol_price,
                 debug):
        self.name = name
        self.src_exchange_platform = src_exchange_platform
        self.dst_exchange_platform = dst_exchange_platform
        self.row = row
        self.col_info_obj = col_info_obj
        self.budget = budget
        self.debug = debug
        self.ex_price_cols = ex_price_cols
        self.trade_list = []
        self.symbol = self.row[self.col_info_obj.symbol_col]
        self.dst_price_col = self.dst_exchange_platform.price_col
        self.secondary_symbol = secondary_symbol
        self.secondary_symbol_price = secondary_symbol_price
        self.min_acceptable_budget = min_acceptable_budget

    def get_desired_quantity(self):
        return calculate_quantity(row=self.row,
                                  max_trade_qty_col=self.col_info_obj.get_max_trade_qty_col(),
                                  price_cols=self.ex_price_cols,
                                  budget=self.budget)

    def is_on_expensive_platform(self):
        # Check it
        return self.row[self.col_info_obj.price_diff_col] > 0

    def create_arbitrage_function(self):
        desired_quantity = self.get_desired_quantity()
        secondary_quantity = convert_main_amount_to_secondary(desired_quantity,
                                                              self.row[self.dst_price_col],
                                                              self.secondary_symbol_price)

        if self.is_on_expensive_platform(): # In this example, the dst is the expensive platform

            strike = HookPunch(symbol=self.symbol,
                               secondary_symbol=self.secondary_symbol,
                               src_exchange_platform=self.src_exchange_platform,
                               dst_exchange_platform=self.dst_exchange_platform,
                               desired_quantity=desired_quantity,
                               secondary_quantity=secondary_quantity,
                               debug=self.debug)
        else:
            if self.src_exchange_platform.get_budget_sync() > self.min_acceptable_budget:
                #  A regular case that the symbol is on the src exchange
                strike = CrossPunch(symbol=self.symbol,
                                    src_exchange_platform=self.src_exchange_platform,
                                    dst_exchange_platform=self.dst_exchange_platform,
                                    desired_quantity=desired_quantity,
                                    debug=self.debug)
            else:
                # There is not enough budget to run the main cross. We need to use the secondary symbol using
                # cross punch to move the money around.
                strike = CrossPunch(symbol=self.secondary_symbol,
                                    src_exchange_platform=self.dst_exchange_platform,
                                    dst_exchange_platform=self.src_exchange_platform,
                                    desired_quantity=secondary_quantity,
                                    debug=self.debug)

        ## There is another senario: The money is in the dst exchange. We need to move it to the src exchange.

        async def arbitrage_function_to_run_trades():
            await strike.punch()

        return arbitrage_function_to_run_trades
