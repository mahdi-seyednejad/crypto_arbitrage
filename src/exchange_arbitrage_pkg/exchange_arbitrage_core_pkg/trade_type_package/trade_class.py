from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_info_class import TradeInformation

class Trade:
    def __init__(self, exchange_platform, trade_type, symbol,
                 side, quantity, price=None,
                 stop_price=None, address=None):
        self.exchange_platform = exchange_platform
        self.trade_type = trade_type
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.address = address


# class Trade:
#     def __init__(self,
#                  exchange_platform: ExchangeNames,
#                  operation: str,
#                  symbol: str,
#                  side: str,
#                  quantity: float,
#                  **kwargs
#                  ):
#         self.exchange_platform = exchange_platform
#         self.operation = operation
#         self.symbol = symbol
#
#         self.side = side
#         self.quantity = quantity
#


