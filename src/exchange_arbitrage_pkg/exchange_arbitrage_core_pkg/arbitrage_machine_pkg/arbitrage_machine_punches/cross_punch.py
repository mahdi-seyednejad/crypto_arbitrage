from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_punches.ex_machine_punch_abstract import \
    ArbitrageMachinePunchSAbstract
from src.exchange_arbitrage_pkg.utils.exchange_picker import pick_exchange
from src.exchange_arbitrage_pkg.utils.price_utils.should_buy_func import should_buy_binance_Async
from src.exchange_code_bases.exchange_class.base_exchange_class import ExchangeAbstractClass

'''
This is the main arbitrage class that buys/moves/ abd sells crypto.
'''


class CrossPunch(ArbitrageMachinePunchSAbstract):
    def __init__(self,
                 symbol,
                 src_exchange_platform: ExchangeAbstractClass,
                 # ToDo: Later, we can assign a table to each exchange containing fees of each symbol
                 dst_exchange_platform: ExchangeAbstractClass,
                 desired_quantity,
                 operation_executor,
                 withdraw_fee,
                 wait_time_info,
                 debug):
        super().__init__(symbol,
                         src_exchange_platform,
                         dst_exchange_platform,
                         desired_quantity,
                         operation_executor,
                         wait_time_info,
                         debug)
        self.punch_name = 'CrossPunch'
        self.withdraw_fee = withdraw_fee
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

    async def _check_to_own(self, order_log):
        #ToDo: Get an optio to see if it is allowed to use the crypto we already have.
        current_symbol_balance = await self.checker.check_available_crypto(self.src_exchange_platform,
                                                                           self.symbol)
        # Step 2: Doe we need to buy?
        should_buy, quantity_to_buy = await self.decide_to_buy_amount(current_symbol_balance)

        # Step 2-1: Buy (if needed)
        order_buy = 'No Need to Buy'
        ## Check if the quantity to buy is greater than both the threshold and the minimum notional value
        if should_buy:
            # if quantity_to_buy > 0:
            if self.debug:
                print(f"Buying {quantity_to_buy} of {self.symbol} to reach desired quantity= {self.desired_quantity} on"
                      f" {self.src_exchange_platform.name}.")
            order_buy, amount_bought = await self.buyer.buy_crypto(exchange_platform=self.src_exchange_platform,
                                                                   symbol=self.symbol,
                                                                   quantity=quantity_to_buy,
                                                                   current_price=self.src_current_price)
            if self.debug:
                print(f"In cross punch, on {self.src_exchange_platform.name}, bought {amount_bought} of {self.symbol}")
                print(f"Successfully bought {amount_bought} of {self.symbol}")
            # ToDo: Check to see how much was successfully bought
            # if amount_bought == -1:  # It was bought successfully
            #     return -1
        order_log[f'order_buy_{self.symbol}'] = order_buy
        # Step 3: move the crypto from src to the dst exchange

        current_symbol_balance = await self.checker.check_available_crypto(self.src_exchange_platform,
                                                                           self.symbol)
        return current_symbol_balance, order_log

    async def _move_it(self, current_symbol_balance, order_log):
        balance_after_check_buy = float(current_symbol_balance)
        amount_to_move = min(balance_after_check_buy, self.desired_quantity) - self.withdraw_fee
        order_move = await self.mover.move_crypto(self.src_exchange_platform,
                                                  self.dst_exchange_platform,
                                                  self.symbol,
                                                  amount_to_move)
        order_log[f'order_move_{self.symbol}'] = order_move
        return amount_to_move, order_log

    async def _wait_then_sell(self, amount_to_move, order_log):
        #ToDo: This needs to be another component.
        if order_log[f'order_move_{self.symbol}'] is None:
            if self.debug:
                print(f"Could not move {self.symbol} from {self.src_exchange_platform.name} to "
                      f"{self.dst_exchange_platform.name}")
                order_log[f'order_sell_{self.symbol}'] = {'Could not move the crypto from src to dst'}
            return order_log
        else:
            # Step 4: Sell the crypto on the dst exchange
            was_received = await self.dst_exchange_platform \
                .wait_til_receive_Async(symbol=self.symbol,
                                        expected_amount=amount_to_move,
                                        check_interval=self.wait_time_info.check_interval,
                                        timeout=self.wait_time_info.timeout,
                                        amount_loss=self.wait_time_info.amount_loss,
                                        second_chance=self.wait_time_info.second_chance,
                                        debug=self.debug)

            if was_received:
                order_sell = await self.seller.sell_crypto(self.dst_exchange_platform,
                                                           self.symbol,
                                                           amount_to_move)
            else:
                print(f"Did not receive {self.desired_quantity} of {self.symbol} "
                      f"on {self.dst_exchange_platform.name} in time.")
                order_sell = None
            order_log[f'order_sell_{self.symbol}'] = order_sell
        return order_log

    async def punch(self):
        order_log_init = {}
        current_symbol_balance, order_log_own = await self._check_to_own(order_log_init)
        amount_to_move, order_log_move = await self._move_it(current_symbol_balance, order_log_own)
        order_log = await self._wait_then_sell(amount_to_move, order_log_move)
        self.order_log_chain.append(order_log)
        if self.debug:
            print("Updated order_log in CrossPunch:")
            print(f"The last order log is: \n{order_log}")
            print(f"The order log chain is: \n{self.order_log_chain}")
        return order_log


