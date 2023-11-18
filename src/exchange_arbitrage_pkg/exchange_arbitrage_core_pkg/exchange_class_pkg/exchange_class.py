from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.broker_utils.quantity_calculation import calculate_quantity
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade


class ExchangeMachine:
    def __init__(self,
                 name,
                 src_exchange_platform,
                 dst_exchange_platform,
                 client):
        self.name = name
        self.client = client
        self.src_exchange_platform = src_exchange_platform
        self.dst_exchange_platform = dst_exchange_platform

        self.trade_pairs = []

    def add_trade(self, trade):
        self.trade_pairs.append(trade)

    def add_source_exchange_trades(self, src_exchange_platform, symbol, quantity):
        self.add_trade(Trade(src_exchange_platform, 'check', symbol, 'buy', quantity))

        # Withdraw the symbol from the Binance account
        self.add_trade(Trade(src_exchange_platform, 'withdraw', symbol, 'send', quantity))

    def add_destination_exchange_trades(self, dst_exchange_platform, symbol, quantity):
        # Deposit the symbol to the Coinbase account
        self.add_trade(Trade(dst_exchange_platform, 'deposit', symbol, 'receive', quantity))

        # Sell the symbol on Coinbase
        self.add_trade(Trade(dst_exchange_platform, 'sell', symbol, 'sell', quantity))

    def create_trades(self, symbol):
        # Check if the symbol is available, if not buy it
        quantity = calculate_quantity(symbol=symbol)

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


