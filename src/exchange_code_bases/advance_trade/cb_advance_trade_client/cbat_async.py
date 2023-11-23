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
        return await self.async_wrap(super().fetch_account_info)

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



# class AsyncAdvanceTradeClient(CbAdvanceTradeClient):
#     def __init__(self, api_auth_obj: APIAuthClass):
#         super().__init__(api_auth_obj)
#         self.session = aiohttp.ClientSession()
#
#     async def fetch_account_info(self):
#         url = f'{self.base_url}/v2/accounts'
#         async with self.session.get(url, auth=self.auth) as response:
#             return await response.json()
#

