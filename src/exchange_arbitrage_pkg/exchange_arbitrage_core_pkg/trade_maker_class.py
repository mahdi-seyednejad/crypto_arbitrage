from abc import ABC, abstractmethod

from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_info_class import TradeInformation


class TradeMakerClass(ABC):
    def __init__(self, trade_maker_config=None):
            self.trade_maker_config = trade_maker_config

    @abstractmethod
    def get_trade_object(self,
                         # trade_info: TradeInformation,
                         trade_type,
                         symbol, side,
                         quantity,
                         price=None,
                         stop_price=None
                         ) -> Trade:
        pass



