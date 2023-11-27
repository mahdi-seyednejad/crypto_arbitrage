from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_helpers import execute_trade


class Seller:
    def __init__(self, debug=False):
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
        return await execute_trade(sell_trade, self.debug)
