import asyncio
from concurrent.futures import ThreadPoolExecutor

import aiohttp

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_code_bases.advance_trade.cb_advance_trade_client.cbat_client import CbAdvanceTradeClient


class AsyncAdvanceTradeClient(CbAdvanceTradeClient):
    def __init__(self, api_auth_obj: APIAuthClass):
        super().__init__(api_auth_obj)
        self.thread_executor = ThreadPoolExecutor()
        self.client = None

    async def async_wrap(self, sync_function, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_executor,
                                          lambda: sync_function(*args, **kwargs))

    async def fetch_account_info(self):
        result = await self.async_wrap(super().fetch_account_info)
        return result # await self.async_wrap(super().fetch_account_info())

    # def get_budget(self, client: CryptoClient, currency):
    #     if self.budget is None:
    #         budget_result = client.fetch_budget(currency)
    #         self.budget = float(budget_result['balance'])
    #         return self.budget
    #     else:
    #         return self.budget
    #
    async def check_balance_coinbase(self, symbol):
        df = await self.async_wrap(super().fetch_account_info)
        try:
            # Assuming 'currency.code' is the column name for currency codes after normalization
            matching_account = df[df['currency.code'] == symbol.split("-")[0]]
            if not matching_account.empty:
                # Assuming 'balance.amount' is the column name for balance amounts
                return matching_account['balance.amount'].iloc[0], True
            else:
                return 0, False
        except Exception as e:
            print(f"Error checking balance for {symbol} on Coinbase Pro: {e}")
            return None, None

    def thread_clean_up(self):
        self.thread_executor.shutdown(wait=True)

    async def withdraw_to_address(self, address, amount, currency):
        return await self.async_wrap(super().withdraw_to_address, address, amount, currency)

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

    async def get_coinbase_symbol_details(client, symbol):
        df = await client.fetch_account_info()
        if df is not None:
            buy_precision = df['base_increment']
            min_buy_amount = df['base_min_size']
            min_notional = df['min_market_funds']
            return buy_precision, min_buy_amount, min_notional
        return None, None, None

