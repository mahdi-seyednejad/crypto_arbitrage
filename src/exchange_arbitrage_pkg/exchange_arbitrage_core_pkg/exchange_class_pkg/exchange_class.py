from src.exchange_arbitrage_pkg.broker_utils.quantity_calculation import calculate_quantity
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_helpers import execute_trade
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass


class ExchangeMachine:
    def __init__(self,
                 name,
                 src_exchange_platform,
                 dst_exchange_platform,
                 row,
                 col_info_obj: ColumnInfoClass,
                 budget):
        self.name = name
        self.src_exchange_platform = src_exchange_platform
        self.dst_exchange_platform = dst_exchange_platform
        self.row = row
        self.col_info_obj = col_info_obj
        self.budget = budget

        self.trade_list = []

    def create_arbitrage_function(self):
        symbol = self.row[self.col_info_obj.symbol_col]
        desired_quantity = calculate_quantity(self.row, self.col_info_obj, self.budget)

        async def ATrade(debug=False):
            print(f"Preparing arbitrage for {symbol} with desired quantity {desired_quantity}")

            # Step 1: Check current balance
            check_trade = Trade(self.src_exchange_platform, 'check', symbol, 'buy', None)
            current_balance = await execute_trade(check_trade, debug)
            current_quantity = current_balance.get(symbol, 0)  # Get the current quantity of the symbol

            # Determine if buying is necessary and the amount to buy
            quantity_to_buy = max(0, desired_quantity - current_quantity)

            # Step 2: Buy (if needed)
            if quantity_to_buy > 0:
                print(f"Buying {quantity_to_buy} of {symbol} to reach desired quantity")
                buy_trade = Trade(self.src_exchange_platform, 'buy', symbol, 'buy', quantity_to_buy)
                await execute_trade(buy_trade, debug)

            # Step 3: Get Deposit Address
            deposit_trade = Trade(self.dst_exchange_platform, 'deposit', symbol, 'receive', None)
            deposit_info = await execute_trade(deposit_trade, debug)
            deposit_address = deposit_info['address']

            # Step 4: Withdraw to Deposit Address
            withdraw_trade = Trade(self.src_exchange_platform, 'withdraw', symbol, 'send', desired_quantity,
                                   address=deposit_address)
            await execute_trade(withdraw_trade, debug)

            print(f"Arbitrage completed for {symbol}")

        return ATrade

    def add_trade(self, trade):
        self.trade_list.append(trade)

    def add_source_exchange_trades(self, src_exchange_platform, symbol, quantity):
        self.add_trade(Trade(src_exchange_platform, 'check', symbol, 'buy', quantity))

        # Withdraw the symbol from the Binance account
        self.add_trade(Trade(src_exchange_platform, 'withdraw', symbol, 'send', quantity))

    def add_destination_exchange_trades(self, dst_exchange_platform, symbol, quantity):
        # Deposit the symbol to the Coinbase account
        self.add_trade(Trade(dst_exchange_platform, 'deposit', symbol, 'receive', quantity))

        # Sell the symbol on Coinbase
        self.add_trade(Trade(dst_exchange_platform, 'sell', symbol, 'sell', quantity))

    def create_trades(self, row, col_info_obj: ColumnInfoClass, budget):
        # Check if the symbol is available, if not buy it
        symbol = row[col_info_obj.symbol_col]
        quantity = calculate_quantity(row, col_info_obj, budget)

        self.add_source_exchange_trades(self.src_exchange_platform, symbol, quantity)
        self.add_destination_exchange_trades(self.dst_exchange_platform, symbol, quantity)

    # def create_trades(self, src_exchange_platform, dst_exchange_platform, symbol):
    #     # Check if the symbol is available, if not buy it
    #     quantity = calculate_quantity(symbol=symbol)
    #
    #     self.add_source_exchange_trades(src_exchange_platform, symbol, quantity)
    #     self.add_destination_exchange_trades(dst_exchange_platform, symbol, quantity)
    #     # self.add_trade(Trade(ExchangeNames.Binance, 'check', symbol, 'buy', quantity))
        #
        # # Withdraw the symbol from the Binance account
        # self.add_trade(Trade(ExchangeNames.Binance, 'withdraw', symbol, 'send', quantity))
        #
        # # Deposit the symbol to the Coinbase account
        # self.add_trade(Trade(ExchangeNames.Coinbase, 'deposit', symbol, 'receive', quantity))
        #
        # # Sell the symbol on Coinbase
        # self.add_trade(Trade(ExchangeNames.Coinbase, 'sell', symbol, 'sell', quantity))
        #
        # # Optionally, more details can be added to each trade such as price, stop price etc.


