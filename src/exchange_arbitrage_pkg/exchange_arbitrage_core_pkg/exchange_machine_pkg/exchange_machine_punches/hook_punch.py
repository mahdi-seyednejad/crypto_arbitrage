'''
The desired crypto is on the more expensive exchange. We eed to move it.
'''
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine_punches.cross_punch import \
    CrossPunch
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine_punches.ex_machine_punch_abstract import \
    ExchangeMachinePunchSAbstract


class HookPunch(ExchangeMachinePunchSAbstract):
    def __init__(self,
                 symbol,
                 secondary_symbol,
                 src_exchange_platform,  # A
                 dst_exchange_platform,  # B
                 desired_quantity,
                 secondary_quantity,
                 debug):
        super().__init__(symbol,
                         src_exchange_platform,
                         dst_exchange_platform,
                         desired_quantity,
                         debug)
        self.punch_name = 'CrossPunch'
        self.secondary_symbol = secondary_symbol
        self.secondary_quantity = secondary_quantity
        self.main_cross = CrossPunch(symbol=symbol,
                                     src_exchange_platform=src_exchange_platform,
                                     dst_exchange_platform=dst_exchange_platform,
                                     desired_quantity=desired_quantity,
                                     debug=debug)
        self.secondary_cross = CrossPunch(symbol=secondary_symbol,
                                          src_exchange_platform=dst_exchange_platform,
                                          dst_exchange_platform=src_exchange_platform,
                                          desired_quantity=secondary_quantity,
                                          debug=debug)

    async def punch(self):
        # Step1: Sell the main crypto on the dst exchange (it is already there to be sold)
        order_sell = self.seller.sell_crypto(self.dst_exchange_platform,
                                             self.symbol,
                                             self.desired_quantity)
        order_log = {f'order_sell_{self.symbol}': order_sell}
        # Do the cross  on teh secondary crypto
        # Step 2: cross the secondary crypto
        order_cross_secondary = await self.secondary_cross.punch()
        order_log[f'order_cross_{self.secondary_symbol}'] = order_cross_secondary

        # Step 3: Sell the secondary crypto on the src exchange
        order_sell = self.seller.sell_crypto(self.src_exchange_platform,
                                             self.secondary_symbol,
                                             self.secondary_quantity)
        order_log[f'order_sell{self.symbol}'] = order_sell
        # Step 4: Cross the main symbol to the dst exchange
        order_cross_main = await self.main_cross.punch()
        order_log[f'order_cross_{self.symbol}'] = order_cross_main
        self.order_log_chain.append(order_log)
        return order_log
