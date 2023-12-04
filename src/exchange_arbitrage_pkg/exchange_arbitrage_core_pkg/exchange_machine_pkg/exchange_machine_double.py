from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine import ArbitrageMachine
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine_punches.cross_punch import \
    CrossPunch
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine_punches.hook_punch import \
    HookPunch
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.price_utils.amount_conversion import convert_main_amount_to_secondary


class ArbitrageMachinePunches(ArbitrageMachine):
    def __init__(self,
                 name,
                 src_exchange_platform: ExchangeAbstractClass,
                 dst_exchange_platform: ExchangeAbstractClass,
                 row,
                 col_info_obj: ColumnInfoClass,
                 budget,
                 secondary_symbol,
                 secondary_symbol_price,
                 debug):
        super().__init__(name, src_exchange_platform, dst_exchange_platform, row, col_info_obj, budget, debug)
        self.secondary_symbol = secondary_symbol
        self.secondary_symbol_price = secondary_symbol_price

    def is_on_expensive_platform(self):
        # Check it
        return self.row[self.col_info_obj.price_diff_col] > 0

    def create_arbitrage_function(self):
        desired_quantity = self.get_desired_quantity()

        if self.is_on_expensive_platform(): # In this example, the dst is the expensive platform
            secondary_quantity = convert_main_amount_to_secondary(desired_quantity,
                                                                  self.row[self.col_info_obj.current_price_col],
                                                                  self.secondary_symbol_price)
            strike = HookPunch(symbol=self.symbol,
                               secondary_symbol=self.secondary_symbol,
                               src_exchange_platform=self.src_exchange_platform,
                               dst_exchange_platform=self.dst_exchange_platform,
                               desired_quantity=desired_quantity,
                               secondary_quantity=secondary_quantity,
                               debug=self.debug)
        else:
            strike = CrossPunch(symbol=self.secondary_symbol,
                                src_exchange_platform=self.src_exchange_platform,
                                dst_exchange_platform=self.dst_exchange_platform,
                                desired_quantity=desired_quantity,
                                debug=self.debug)

        async def arbitrage_function_to_run_trades():
            await strike.punch()

        return arbitrage_function_to_run_trades
