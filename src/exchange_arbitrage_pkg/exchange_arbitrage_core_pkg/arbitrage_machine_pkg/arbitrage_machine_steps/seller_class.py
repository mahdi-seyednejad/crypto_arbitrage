from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor


class Seller:
    def __init__(self, operation_executor: OperationExecutor, debug=False):
        self.operation_executor = operation_executor
        self.debug = debug

    async def sell_crypto(self,
                          exchange_platform,
                          symbol,
                          quantity):
        sell_trade = Trade(exchange_platform=exchange_platform,
                           trade_type='sell',
                           symbol=symbol,
                           side='sell',
                           quantity=quantity)
        return await self.operation_executor.execute_trade(sell_trade,
                                                           self.debug)


