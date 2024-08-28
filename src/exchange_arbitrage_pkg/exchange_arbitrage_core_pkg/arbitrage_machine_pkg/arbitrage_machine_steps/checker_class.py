from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade


class Checker:
    def __init__(self, operation_executor,  debug=False):
        self.operation_executor = operation_executor
        self.debug = debug

    async def check_available_crypto(self,
                                     exchange_platform,
                                     symbol):
        check_trade = Trade(exchange_platform=exchange_platform,
                            trade_type='check',
                            symbol=symbol,
                            quantity=None)
        current_symbol_balance = await self.operation_executor\
            .execute_trade(check_trade,
                           self.debug)
        if current_symbol_balance is None:
            print(f"!!! Error !!! : {exchange_platform.name} did not return the balance of {symbol}")
            return 0.0
        return float(current_symbol_balance)
