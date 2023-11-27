from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_helpers import execute_trade


class Buyer:
    def __init__(self, debug=False):
        self.debug = debug

    async def buy_crypto(self,
                         exchange_platform,
                         symbol,
                         quantity):
        buy_trade = Trade(exchange_platform=exchange_platform,
                          trade_type='buy',
                          symbol=symbol,
                          side='buy',
                          quantity=quantity)
        order = await execute_trade(buy_trade, self.debug)
        amount_bought = exchange_platform.get_order_output_quantity(order)
        return amount_bought

