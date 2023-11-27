from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg import exchange_machine_steps as ems

'''
This is the main arbitrage class that buys/moves/ abd sells crypto.
'''
class CrossAgent:
    def __init__(self,
                 symbol,
                 src_exchange_platform,
                 dst_exchange_platform,
                 desired_quantity,
                 debug):
        self.symbol = symbol
        self.src_exchange_platform = src_exchange_platform
        self.dst_exchange_platform = dst_exchange_platform
        self.checker = ems.checker_class.Checker(debug=debug)
        self.seller = ems.seller_class.Seller(debug=debug)
        self.buyer = ems.buyer_class.Buyer(debug=debug)
        self.mover = ems.mover_class.Mover(debug=debug)
        self.desired_quantity = desired_quantity
        self.order_log_chain = []

        self.debug = debug

    async def arbitrage_cross(self):
        # Step 1: Check Available Crypto
        current_symbol_balance = await self.checker.check_available_crypto(self.src_exchange_platform,
                                                                           self.symbol)
        # Determine if buying is necessary and the amount to buy
        quantity_to_buy = max(0, self.desired_quantity - current_symbol_balance)  ## Current balance comes here

        # Step 2: Buy (if needed)
        # If we do not have enough of that crypto, we need to buy it as much as our budget allows
        order_buy = 'No Need to Buy'
        if quantity_to_buy > 0:
            if self.debug:
                print(f"Buying {quantity_to_buy} of {self.symbol} to reach desired quantity")
            order_buy, amount_bought = await self.buyer.buy_crypto(self.src_exchange_platform,
                                                                   self.symbol,
                                                                   quantity_to_buy)
            if self.debug:
                print(f"Successfully bought {amount_bought} of {self.symbol}")
            # ToDo: Check to see how much was successfully bought
            if amount_bought == -1:  # It was bought successfully
                return -1
        order_log = {f'order_buy_{self.symbol}': order_buy}
        # Step 3: move the crypto from src to the dst exchange
        order_move = self.mover.move_crypto(self.src_exchange_platform,
                                            self.dst_exchange_platform,
                                            self.symbol,
                                            self.desired_quantity)
        order_log[f'order_move_{self.symbol}'] = order_move
        # Step 4: Sell the crypto on the dst exchange
        order_sell = self.seller.sell_crypto(self.dst_exchange_platform,
                                             self.symbol,
                                             self.desired_quantity)
        order_log[f'order_sell_{self.symbol}'] = order_sell
        self.order_log_chain.append(order_log)

