from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_helpers import execute_trade


class Checker:
    def __init__(self, debug=False):
        self.debug = debug

    async def check_available_crypto(self,
                                     exchange_platform,
                                     symbol):
        check_trade = Trade(exchange_platform=exchange_platform,
                            trade_type='check',
                            symbol=symbol,
                            quantity=None)
        current_symbol_balance = await execute_trade(check_trade, self.debug)
        return float(current_symbol_balance)
