from typing import List

from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.ex_machine_punch_abstract import \
    ArbitrageMachinePunchSAbstract
from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor


class KungFuPunch(ArbitrageMachinePunchSAbstract):
    '''
    The punch does nothing. It is there to prevent some errors.
    '''

    def __init__(self,
                 symbol,
                 src_exchange_platform,
                 dst_exchange_platform,
                 desired_quantity,
                 reason: List[str],
                 operation_executor: OperationExecutor,
                 wait_time_info,
                 debug):
        super().__init__(symbol=symbol,
                         src_exchange_platform=src_exchange_platform,
                         dst_exchange_platform=dst_exchange_platform,
                         desired_quantity=desired_quantity,
                         operation_executor=operation_executor,
                         wait_time_info=wait_time_info,
                         debug=debug)
        self.punch_name = 'KungFuPunch'
        self.reason = reason

    async def punch(self):
        if self.debug:
            print(f"reason for KungFuPunch: {self.reason}")
        return {'KungFuPunch': 'Did nothing.'}
