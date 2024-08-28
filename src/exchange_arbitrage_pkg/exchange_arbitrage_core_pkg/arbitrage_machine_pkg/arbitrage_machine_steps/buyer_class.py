from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor


class Buyer:
    def __init__(self, operation_executor: OperationExecutor, debug=False):
        self.operation_executor = operation_executor
        self.debug = debug

    async def buy_crypto(self,
                         exchange_platform,
                         symbol,
                         quantity,
                         current_price=None):
        if current_price is None:
            current_price = exchange_platform.get_current_price(symbol)
        buy_trade = Trade(exchange_platform=exchange_platform,
                          trade_type='buy',
                          symbol=symbol,
                          side='buy',
                          quantity=quantity,
                          current_price=current_price)
        order = await self.operation_executor.execute_trade(buy_trade, self.debug)
        # Check if the order is a tuple and select the first element if it is
        if isinstance(order, tuple):
            order = order[0]
        amount_bought = exchange_platform.get_order_output_quantity(order, current_price)
        return order, amount_bought

