from src.exchange_arbitrage_pkg.broker_utils.quantity_calculation import calculate_quantity
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_helpers import execute_trade
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass


class ExchangeMachine:
    def __init__(self,
                 name,
                 src_exchange_platform: ExchangeAbstractClass,
                 dst_exchange_platform: ExchangeAbstractClass,
                 row,
                 col_info_obj: ColumnInfoClass,
                 budget,
                 debug):
        self.name = name
        self.src_exchange_platform = src_exchange_platform
        self.dst_exchange_platform = dst_exchange_platform
        self.row = row
        self.col_info_obj = col_info_obj
        self.budget = budget
        self.debug = debug
        self.trade_list = []

    def create_arbitrage_function(self):
        symbol = self.row[self.col_info_obj.symbol_col]
        # self.src_exchange_platform.set_budget(self.src_exchange_platform.sync_client, self.budget)
        desired_quantity = calculate_quantity(self.row,
                                              self.col_info_obj,
                                              self.budget)

        async def arbitrage_function_to_run_trades():
            print(f"Preparing arbitrage for {symbol} with desired quantity {desired_quantity}")

            # Step 1: Check current balance
            # check_trade = Trade(self.src_exchange_platform, 'check', symbol, 'buy', None)
            check_trade = Trade(exchange_platform=self.src_exchange_platform,
                                trade_type='check',
                                symbol=symbol,
                                quantity=None)
            current_symbol_balance = await execute_trade(check_trade, self.debug)
            current_symbol_balance = float(current_symbol_balance)

            # Determine if buying is necessary and the amount to buy
            quantity_to_buy = max(0, desired_quantity - current_symbol_balance) ## Current balance comes here

            # Step 2: Buy (if needed)
            if quantity_to_buy > 0:
                print(f"Buying {quantity_to_buy} of {symbol} to reach desired quantity")
                # buy_trade = Trade(self.src_exchange_platform, 'buy', symbol, 'buy', quantity_to_buy)
                buy_trade = Trade(exchange_platform=self.src_exchange_platform,
                                  trade_type='buy',
                                  symbol=symbol,
                                  side='buy',
                                  quantity=quantity_to_buy)
                await execute_trade(buy_trade, self.debug)

            # Step 3: Get Deposit Address
            deposit_trade = Trade(self.dst_exchange_platform,
                                  'deposit',
                                  symbol,
                                  'receive', None)
            deposit_address = await execute_trade(deposit_trade, self.debug)
            # deposit_address = deposit_info['address']

            # Step 4: Withdraw to Deposit Address
            withdraw_trade = Trade(self.src_exchange_platform,
                                   'withdraw',
                                   symbol,
                                   'send',
                                   desired_quantity,
                                   address=deposit_address)
            await execute_trade(withdraw_trade, self.debug)

            print(f"Arbitrage completed for {symbol}")

        return arbitrage_function_to_run_trades

    def add_trade(self, trade):
        self.trade_list.append(trade)
