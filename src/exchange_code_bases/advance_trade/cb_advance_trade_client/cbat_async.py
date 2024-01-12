import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_code_bases.advance_trade.cb_advance_trade_client.cbat_client import CbAdvanceTradeClient


class AsyncAdvanceTradeClient(CbAdvanceTradeClient):
    def __init__(self, api_auth_obj: APIAuthClass):
        super().__init__(api_auth_obj)
        self.thread_executor = ThreadPoolExecutor()
        self.client = None

    @classmethod
    async def create_async(cls, api_auth_obj: APIAuthClass):
        self = AsyncAdvanceTradeClient(api_auth_obj)
        # Any asynchronous initializations can go here
        return self

    async def async_wrap(self, sync_function, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_executor,
                                          lambda: sync_function(*args, **kwargs))

    async def fetch_account_info(self):
        result = await self.async_wrap(super().fetch_account_info)
        return result  # await self.async_wrap(super().fetch_account_info())

    async def check_balance_coinbase(self, symbol):
        df = await self.async_wrap(super().fetch_account_info)
        try:
            # Assuming 'currency.code' is the column name for currency codes after normalization
            matching_account = df[df['currency.code'] == symbol.split("-")[0]]
            if not matching_account.empty:
                # Assuming 'balance.amount' is the column name for balance amounts
                return float(matching_account['balance.amount'].iloc[0]), True
            else:
                return 0, False
        except Exception as e:
            print(f"Error checking balance for {symbol} on Coinbase Pro: {e}")
            return None, None

    def thread_clean_up(self):
        self.thread_executor.shutdown(wait=True)

    async def withdraw_to_address(self, address, amount, currency):
        return await self.async_wrap(super().withdraw_to_address, address, amount, currency)

    async def withdraw_to_address_persistent(self, address, amount, currency, amount_adjuster, max_attempts):
        return await self.async_wrap(super().withdraw_to_address_persistent, address, amount,
                                     currency, amount_adjuster, max_attempts)

    async def fetch_deposit_address(self, currency):
        return await self.async_wrap(super().fetch_deposit_address, currency)

    async def fetch_budget(self, currency='USD'):
        return await self.async_wrap(super().fetch_budget, currency)

    async def create_order(self, order_type, amount, currency, price=None):
        return await self.async_wrap(super().create_order, order_type, amount, currency, price)

    async def fetch_available_cryptos(self):
        return await self.async_wrap(super().fetch_available_cryptos)

    async def fetch_all_available_base_assets(self):
        return await self.async_wrap(super().fetch_all_available_base_assets)

    async def fetch_order_book(self, product_id, level=2):
        return await self.async_wrap(super().fetch_order_book, product_id, level)

    async def wait_for_deposit_confirmation(self,
                                            symbol,
                                            expected_amount,
                                            check_interval,
                                            timeout,
                                            amount_loss,
                                            debug):
        """
        Waits for the deposit to be confirmed on the destination exchange.
        :param symbol: Symbol of the cryptocurrency to check.
        :param expected_amount: The amount of cryptocurrency expected to be deposited.
        :param check_interval: Time in seconds between each balance check.
        :param timeout: Maximum time in seconds to wait for the deposit.
        :param amount_loss: The amount of moved crypto that might be lost in the transfer (due to commission, etc)
        :return: True if deposit is confirmed, False if timed out.
        """
        start_time = asyncio.get_event_loop().time()
        while True:
            current_balance, has_bought_before = await self.check_balance_coinbase(symbol)
            min_expected_amount = expected_amount * (1 - amount_loss)
            if debug:
                print(f"Current balance for {symbol} on Binance: {current_balance}")
                print(f"Expected balance for {symbol} on Binance: {min_expected_amount}")
            if has_bought_before:
                if current_balance >= min_expected_amount:
                    return True

            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > timeout:
                print(f"Timeout reached while waiting for deposit of {symbol}")
                return False

            await asyncio.sleep(check_interval)

    async def get_prices_as_df(self, price_col, limit=None):
        result = await self.async_wrap(super().get_prices_as_df, price_col, limit)
        return result

