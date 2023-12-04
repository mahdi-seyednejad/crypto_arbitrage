from abc import ABC, abstractmethod
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg import exchange_machine_steps as ems


class ExchangeMachinePunchSAbstract(ABC):
    def __init__(self,
                 symbol,
                 src_exchange_platform,
                 dst_exchange_platform,
                 desired_quantity,
                 debug):
        self.punch_name = 'AbstractPunch'
        self.symbol = symbol
        self.src_exchange_platform = src_exchange_platform
        self.dst_exchange_platform = dst_exchange_platform
        self.checker = ems.checker_class.Checker(debug=debug)
        self.seller = ems.seller_class.Seller(debug=debug)
        self.buyer = ems.buyer_class.Buyer(debug=debug)
        self.mover = ems.mover_class.Mover(debug=debug)
        self.desired_quantity = desired_quantity
        self.order_log_chain = []
        self.debug = debug

        self.src_current_price = self.src_exchange_platform.get_current_price(self.symbol)
        self.dst_current_price = self.dst_exchange_platform.get_current_price(self.symbol)

    @abstractmethod
    async def punch(self):
        pass
