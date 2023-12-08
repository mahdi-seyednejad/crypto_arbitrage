from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.ex_machine_punch_abstract import \
    ExchangeMachinePunchSAbstract
from src.exchange_arbitrage_pkg.utils.exchange_picker import pick_exchange
from src.exchange_arbitrage_pkg.utils.price_utils.should_buy_func import should_buy_binance_Async
from src.exchange_code_bases.exchange_class.base_exchange_class import ExchangeAbstractClass

'''
This is the main arbitrage class that buys/moves/ abd sells crypto.
'''


class CrossPunch(ExchangeMachinePunchSAbstract):
    def __init__(self,
                 symbol,
                 src_exchange_platform: ExchangeAbstractClass,
                 dst_exchange_platform: ExchangeAbstractClass,
                 desired_quantity,
                 debug):
        super().__init__(symbol,
                         src_exchange_platform,
                         dst_exchange_platform,
                         desired_quantity,
                         debug)
        self.punch_name = 'CrossPunch'
        # self.quantity_deduction_percent = quantity_deduction_percent
        # self.threshold_quantity = self.desired_quantity * self.quantity_deduction_percent

    async def decide_to_buy_amount(self, current_symbol_balance):
        # Determine if buying is necessary and the amount to buy
        binance_exchange = pick_exchange(exchange_name=ExchangeNames.Binance,
                                         exchange_list=[self.src_exchange_platform,
                                                        self.dst_exchange_platform])
        acync_client = await binance_exchange.create_async_client()
        # We use the restriction from Binance and apply on both exchanges
        should_buy, quantity_to_buy = await should_buy_binance_Async(client=acync_client,
                                                                     symbol=self.symbol,
                                                                     desired_quantity=self.desired_quantity,
                                                                     available_balance=current_symbol_balance)
        return should_buy, quantity_to_buy

    async def punch(self):
        # Calculate the threshold quantity

        # Step 1: Check Available Crypto
        current_symbol_balance = await self.checker.check_available_crypto(self.src_exchange_platform,
                                                                           self.symbol)
        # Step 2: Doe we need to buy?
        should_buy, quantity_to_buy = await self.decide_to_buy_amount(current_symbol_balance)

        # Step 2-1: Buy (if needed)
        order_buy = 'No Need to Buy'
        # Check if the quantity to buy is greater than both the threshold and the minimum notional value
        if should_buy:
            # if quantity_to_buy > 0:
            if self.debug:
                print(f"Buying {quantity_to_buy} of {self.symbol} to reach desired quantity")
            order_buy, amount_bought = await self.buyer.buy_crypto(exchange_platform=self.src_exchange_platform,
                                                                   symbol=self.symbol,
                                                                   quantity=quantity_to_buy,
                                                                   current_price=self.src_current_price)
            if self.debug:
                print(f"Successfully bought {amount_bought} of {self.symbol}")
            # ToDo: Check to see how much was successfully bought
            if amount_bought == -1:  # It was bought successfully
                return -1
        order_log = {f'order_buy_{self.symbol}': order_buy}
        # Step 3: move the crypto from src to the dst exchange

        current_symbol_balance = await self.checker.check_available_crypto(self.src_exchange_platform,
                                                                           self.symbol)
        balance_after_check_buy = float(current_symbol_balance)
        amount_to_move = min(balance_after_check_buy, self.desired_quantity)
        order_move = await self.mover.move_crypto(self.src_exchange_platform,
                                                  self.dst_exchange_platform,
                                                  self.symbol,
                                                  amount_to_move)
        order_log[f'order_move_{self.symbol}'] = order_move
        # Step 4: Sell the crypto on the dst exchange
        was_received = await self.dst_exchange_platform.wait_til_receive_Async(symbol=self.symbol,
                                                                               expected_amount=self.desired_quantity,
                                                                               check_interval=5,
                                                                               timeout=420,
                                                                               amount_loss=0.05)

        if was_received:
            order_sell = await self.seller.sell_crypto(self.dst_exchange_platform,
                                                       self.symbol,
                                                       amount_to_move)
            order_log[f'order_sell_{self.symbol}'] = order_sell
            self.order_log_chain.append(order_log)
        else:
            print(f"Did not receive {self.desired_quantity} of {self.symbol} in time")
            order_log[f'order_sell_{self.symbol}'] = None
        return order_log
