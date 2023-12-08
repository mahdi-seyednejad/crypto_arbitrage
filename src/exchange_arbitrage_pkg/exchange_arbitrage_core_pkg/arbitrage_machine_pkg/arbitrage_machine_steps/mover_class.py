from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg import arbitrage_machine_steps as ems


def create_withdraw_trade(deposit_address, symbol, quantity, src_exchange_platform):
    if src_exchange_platform.name == ExchangeNames.Binance:
        # If the src is binance, it needs to know the network of the deposit address
        withdraw_trade = Trade(exchange_platform=src_exchange_platform,
                               trade_type='withdraw',
                               symbol=symbol,
                               side='send',
                               quantity=quantity,
                               address=deposit_address['address'],
                               network=deposit_address['network'])
    else:
        withdraw_trade = Trade(exchange_platform=src_exchange_platform,
                               trade_type='withdraw',
                               symbol=symbol,
                               side='send',
                               quantity=quantity,
                               address=deposit_address)
    return withdraw_trade


class Mover:
    def __init__(self, operation_executor, debug=False):
        self.operation_executor = operation_executor
        self.debug = debug
        self.checker = ems.checker_class.Checker(operation_executor, debug=debug)

    async def move_crypto(self,
                          src_exchange_platform,
                          dst_exchange_platform,
                          symbol,
                          quantity):
        current_symbol_balance = await self.checker.check_available_crypto(src_exchange_platform,
                                                                           symbol)
        min_quantity = min(quantity, current_symbol_balance)
        base_quantity_to_move = src_exchange_platform.withdrawal_factor * min_quantity
        deposit_trade = Trade(exchange_platform=dst_exchange_platform,
                              trade_type='deposit',
                              symbol=symbol,
                              side='receive',
                              quantity=None)
        deposit_address = await self.operation_executor.execute_trade(deposit_trade, self.debug)
        withdraw_trade = create_withdraw_trade(deposit_address=deposit_address,
                                               symbol=symbol,
                                               quantity=base_quantity_to_move,
                                               src_exchange_platform=src_exchange_platform)

        return await self.operation_executor.execute_trade(withdraw_trade, self.debug)

