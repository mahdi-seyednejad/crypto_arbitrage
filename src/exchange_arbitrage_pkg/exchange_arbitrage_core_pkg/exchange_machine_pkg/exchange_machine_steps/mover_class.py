from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_class import Trade
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_helpers import execute_trade


class Mover:
    def __init__(self, debug=False):
        self.debug = debug

    async def move_crypto(self,
                          src_exchange_platform,
                          dst_exchange_platform,
                          symbol,
                          quantity):
        deposit_trade = Trade(dst_exchange_platform,
                              'deposit',
                              symbol,
                              'receive', None)
        deposit_address = await execute_trade(deposit_trade, self.debug)
        # deposit_address = deposit_info['address']

        # Step 4: Withdraw to Deposit Address
        withdraw_trade = Trade(src_exchange_platform,
                               'withdraw',
                               symbol,
                               'send',
                               quantity,
                               address=deposit_address)
        return await execute_trade(withdraw_trade, self.debug)
