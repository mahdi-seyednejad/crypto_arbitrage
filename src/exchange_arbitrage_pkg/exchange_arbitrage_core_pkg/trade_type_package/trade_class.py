from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_info_class import TradeInformation
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass


class Trade:
    def __init__(self, exchange_platform: ExchangeAbstractClass,
                 trade_type, symbol,
                 side=None, quantity=None, price=None,
                 stop_price=None, address=None, network=None,
                 current_price=None):
        self.exchange_platform = exchange_platform
        self.trade_type = trade_type
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.address = address
        self.network = network
        self.current_price = current_price


