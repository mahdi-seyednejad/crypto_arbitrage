from abc import ABC, abstractmethod
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg import arbitrage_machine_steps as ems
from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import WaitTimeDeposit
from src.exchange_code_bases.exchange_class.base_exchange_class import ExchangeAbstractClass


class ArbitrageMachinePunchSAbstract(ABC):
    def __init__(self,
                 symbol,
                 src_exchange_platform: ExchangeAbstractClass,
                 dst_exchange_platform: ExchangeAbstractClass,
                 desired_quantity: float,
                 operation_executor: OperationExecutor,
                 wait_time_info: WaitTimeDeposit,
                 debug: bool):
        self.punch_name = 'AbstractPunch'
        self.symbol = symbol
        self.src_exchange_platform = src_exchange_platform
        self.dst_exchange_platform = dst_exchange_platform
        self.checker = ems.checker_class.Checker(operation_executor=operation_executor, debug=debug)
        self.seller = ems.seller_class.Seller(operation_executor=operation_executor, debug=debug)
        self.buyer = ems.buyer_class.Buyer(operation_executor=operation_executor, debug=debug)
        self.mover = ems.mover_class.Mover(operation_executor=operation_executor, debug=debug)
        self.desired_quantity = desired_quantity
        self.order_log_chain = []
        self.wait_time_info = wait_time_info
        self.debug = debug

        self.src_current_price = self.src_exchange_platform.get_current_price(self.symbol)
        self.dst_current_price = self.dst_exchange_platform.get_current_price(self.symbol)

    @abstractmethod
    async def punch(self):
        pass


