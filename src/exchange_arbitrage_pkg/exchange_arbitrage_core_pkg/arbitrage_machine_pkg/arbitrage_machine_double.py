from src.exchange_arbitrage_pkg.broker_utils.quantity_calculation import calculate_quantity, calculate_quantity_new_2
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.cross_punch import \
    CrossPunch
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.hook_punch import \
    HookPunch
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.kunf_fu_punch import \
    KungFuPunch
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import WaitTimeDeposit
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
                 secondary_symbol,  # A good symbol with higher price on src
                 secondary_symbol_price,
                 secondary_symbol_withdraw_fee,
                 operation_executor,
                 wait_time_info: WaitTimeDeposit,
                 debug):
        self.name = name
        self.src_exchange_platform = src_exchange_platform
        self.dst_exchange_platform = dst_exchange_platform
        self.row = row
        self.col_info_obj = col_info_obj
        self.budget = budget
        self.ex_price_cols = ex_price_cols
        self.trade_list = []
        self.symbol = self.row[self.col_info_obj.symbol_col]
        self.dst_price_col = self.dst_exchange_platform.price_col
        self.secondary_symbol = secondary_symbol
        self.secondary_symbol_price = secondary_symbol_price
        self.secondary_symbol_withdraw_fee = secondary_symbol_withdraw_fee
        self.min_acceptable_budget = min_acceptable_budget
        self.operation_executor = operation_executor
        self.wait_time_info = wait_time_info
        self.withdraw_fee = row[self.col_info_obj.withdraw_fee_col]
        # What about the withdrawal fee on the secondary symbol?
        self.debug = debug

    def get_desired_quantity(self):
        return calculate_quantity(row=self.row,
                                  quantity_col=self.col_info_obj.order_book_col_obj.trading_volume_col,
                                  # self.col_info_obj.get_max_trade_qty_col(),
                                  price_cols=self.ex_price_cols,
                                  budget=self.budget)

    def _get_possible_desired_quantity(self,
                                       price,
                                       budget,
                                       withdraw_fee):
        return calculate_quantity_new_2(
            max_profitable_trading_volume=self.row[self.col_info_obj.order_book_col_obj.trading_volume_col],
            ex_price=price,
            withdraw_fee=withdraw_fee,
            min_acceptable_profit=1,
            ex_budget=budget)


    def is_on_expensive_platform(self, desired_quantity):
        dst_avail_crypto = self.dst_exchange_platform.get_available_amount_sync(self.symbol)
        return dst_avail_crypto['balance'] > desired_quantity

    # ToDo: If the strike does not need the seconday,
    # then, we just do the thing we were supposed to do with respect to the budget.
    # If it needs secondary, then, we look into the secondary symbol.
    # If we have it, then, we do things based on that.
    # If we do not have it, then, do nothing.

    def _strike_with_no_secondary(self):
        possible_qty_on_src = self._get_possible_desired_quantity(
            price=self.row[self.src_exchange_platform.price_col],
            budget=self.src_exchange_platform.get_budget_sync(),
            withdraw_fee=self.row[self.col_info_obj.withdraw_fee_col])

        if possible_qty_on_src > 0:  # Do we have enough budget to do the cross?
            strike = CrossPunch(symbol=self.symbol,
                                src_exchange_platform=self.src_exchange_platform,
                                dst_exchange_platform=self.dst_exchange_platform,
                                desired_quantity=possible_qty_on_src,
                                operation_executor=self.operation_executor,
                                withdraw_fee=self.withdraw_fee,
                                wait_time_info=self.wait_time_info,
                                debug=self.debug)
        else:
            reason_1 = f"There is NOT a secondary symbol."
            reason_2 = f"We do not have enough budget to do the cross. The budget is {self.src_exchange_platform.get_budget_sync()}"
            strike = KungFuPunch(symbol=self.symbol,
                                 src_exchange_platform=self.src_exchange_platform,
                                 dst_exchange_platform=self.dst_exchange_platform,
                                 desired_quantity=possible_qty_on_src,
                                 reason=[reason_1, reason_2],
                                 operation_executor=self.operation_executor,
                                 wait_time_info=self.wait_time_info,
                                 debug=self.debug)
            if self.debug:
                print(reason_1)
                print(reason_2)
        return strike

    def _strike_with_secondary(self):
        max_profitable_trading_volume = self.row[self.col_info_obj.order_book_col_obj.trading_volume_col]
        if self.is_on_expensive_platform(
                max_profitable_trading_volume):  # What if some parts of the primary crypto is on dst?
            secondary_quantity = convert_main_amount_to_secondary(max_profitable_trading_volume,
                                                                  self.row[self.dst_price_col],
                                                                  self.secondary_symbol_price)

            strike = HookPunch(primary_symbol=self.symbol,
                               secondary_symbol=self.secondary_symbol,
                               src_exchange_platform=self.src_exchange_platform,
                               dst_exchange_platform=self.dst_exchange_platform,
                               primary_desired_quantity=max_profitable_trading_volume,
                               secondary_quantity=secondary_quantity,
                               operation_executor=self.operation_executor,
                               primary_withdraw_fee=self.withdraw_fee,
                               secondary_withdraw_fee=self.secondary_symbol_withdraw_fee,
                               wait_time_info=self.wait_time_info,
                               debug=self.debug)
        else:
            possible_qty_on_src = self._get_possible_desired_quantity(
                price=self.row[self.src_exchange_platform.price_col],
                budget=self.src_exchange_platform.get_budget_sync(),
                withdraw_fee=self.row[self.col_info_obj.withdraw_fee_col])
            if possible_qty_on_src > 0:
                strike = CrossPunch(symbol=self.symbol,
                                    src_exchange_platform=self.src_exchange_platform,
                                    dst_exchange_platform=self.dst_exchange_platform,
                                    desired_quantity=possible_qty_on_src,
                                    operation_executor=self.operation_executor,
                                    withdraw_fee=self.withdraw_fee,
                                    wait_time_info=self.wait_time_info,
                                    debug=self.debug)
            else:
                possible_qty_on_dst = self._get_possible_desired_quantity(
                    price=self.secondary_symbol_price,
                    budget=self.dst_exchange_platform.get_budget_sync(),
                    withdraw_fee=self.secondary_symbol_withdraw_fee)

                if possible_qty_on_dst > 0:
                    strike = CrossPunch(symbol=self.symbol,
                                        src_exchange_platform=self.dst_exchange_platform,
                                        dst_exchange_platform=self.src_exchange_platform,
                                        desired_quantity=possible_qty_on_dst,
                                        operation_executor=self.operation_executor,
                                        withdraw_fee=self.withdraw_fee,
                                        wait_time_info=self.wait_time_info,
                                        debug=self.debug)
                else:
                    reason_1 = f"There is a secondary symbol: {self.secondary_symbol}. But..."
                    reason_2 = f"The primary symbol {self.symbol} is not on dst exchange ({self.dst_exchange_platform.name}). "
                    reason_3 = f"We do not have enough budget to do the cross from dst which is {self.dst_exchange_platform.get_budget_sync()}" \
                               f"The budget on dst is {self.src_exchange_platform.get_budget_sync()}"
                    strike = KungFuPunch(symbol=self.symbol,
                                         src_exchange_platform=self.src_exchange_platform,
                                         dst_exchange_platform=self.dst_exchange_platform,
                                         desired_quantity=possible_qty_on_src,
                                         reason=[reason_1, reason_2, reason_3],
                                         operation_executor=self.operation_executor,
                                         wait_time_info=self.wait_time_info,
                                         debug=self.debug)
                    if self.debug:
                        print(reason_1)
                        print(reason_2)
        return strike

    def create_arbitrage_function(self):
        if self.secondary_symbol is None:
            strike = self._strike_with_no_secondary()
        else:
            strike = self._strike_with_secondary()

        async def arbitrage_function_to_run_trades():
            await strike.punch()

        return arbitrage_function_to_run_trades
