# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# import cbpro
# import pandas as pd
#
# from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
# from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
# from src.exchange_code_bases.exchange_class.base_exchange_class import ExchangeAbstractClass
# from src.exchange_arbitrage_pkg.utils.binance_coinbase_convertor import convert__symbol_bi_to_cb
#
#
# class CoinbaseBaseSyncClient(cbpro.AuthenticatedClient):
#     def get_deposit_address(self, currency):
#         # Fetch all accounts
#         accounts = self.get_accounts()
#
#         # Find the account with the matching currency
#         account_id = None
#         for acc in accounts:
#             if acc.get('currency') == currency:
#                 account_id = acc.get('id')
#                 break
#
#         if account_id is None:
#             raise Exception(f"No account found for currency {currency}")
#
#         # Fetch the deposit information for the identified account
#         deposit_info = self.get_deposit_address(account_id)
#         return deposit_info
#
#
# class CoinbaseAsyncClient(CoinbaseBaseSyncClient):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.thread_executor = ThreadPoolExecutor()
#
#     async def async_wrap(self, sync_function, *args, **kwargs):
#         loop = asyncio.get_event_loop()
#         return await loop.run_in_executor(self.thread_executor,
#                                           lambda: sync_function(*args, **kwargs))
#
#     def thread_clean_up(self):
#         self.thread_executor.shutdown(wait=True)
#
#     def get_accounts(self):
#         return self.async_wrap(super().get_accounts)
#
#     def place_order(self, product_id, side, order_type, price=None, size=None):
#         return self.async_wrap(super().place_order, product_id=product_id, side=side, type=order_type, price=price,
#                                size=size)
#
#     def crypto_withdraw(self, amount, currency, crypto_address):
#         return self.async_wrap(super().crypto_withdraw, amount=amount, currency=currency, crypto_address=crypto_address)
#
#     async def get_deposit_address(self, currency):
#         # First, find the account ID for the given currency
#         accounts = await self.async_wrap(super().get_accounts)
#         account_id = next((acc['id'] for acc in accounts if acc['currency'] == currency), None)
#
#         if account_id is None:
#             raise Exception(f"Account not found for currency: {currency}")
#
#         # Now, fetch the deposit information for this account
#         deposit_info = await self.async_wrap(super().get_deposit_address, account_id)
#         return deposit_info
#
#
# class CoinbaseExchange(ExchangeAbstractClass):
#     def __init__(self, api_auth_obj: APIAuthClass):
#         super().__init__(ExchangeNames.Coinbase, api_auth_obj)
#         self.vol_col_key = "coinbase_volume_col"
#
#         self.public_client = cbpro.PublicClient()
#         if self.api_auth_obj.is_testnet:
#             sandbox_url = "https://api-public.sandbox.pro.coinbase.com"
#             self.client = CoinbaseBaseSyncClient(key=self.api_auth_obj.api_key,
#                                                  b64secret=self.api_auth_obj.secret_key,
#                                                  passphrase=self.api_auth_obj.pass_phrase,
#                                                  api_url=sandbox_url)
#
#             self.async_client = CoinbaseAsyncClient(key=self.api_auth_obj.api_key,
#                                                     b64secret=self.api_auth_obj.secret_key,
#                                                     passphrase=self.api_auth_obj.pass_phrase,
#                                                     api_url=sandbox_url)
#
#         else:
#             self.client = CoinbaseBaseSyncClient(key=self.api_auth_obj.api_key,
#                                                  b64secret=self.api_auth_obj.secret_key,
#                                                  passphrase=self.api_auth_obj.pass_phrase)
#
#             self.async_client = CoinbaseAsyncClient(key=self.api_auth_obj.api_key,
#                                                     b64secret=self.api_auth_obj.secret_key,
#                                                     passphrase=self.api_auth_obj.pass_phrase)
#
#     def create_async_client(self):
#         return CoinbaseAsyncClient(key=self.api_auth_obj.api_key,
#                                    b64secret=self.api_auth_obj.secret_key,
#                                    passphrase=self.api_auth_obj.pass_phrase)
#
#     def get_order_book_sync(self, client, symbol, level=2):
#         symbol = convert__symbol_bi_to_cb(symbol)
#         if client is None:
#             client = self.client
#         order_book = client.get_product_order_book(product_id=symbol, level=level)
#
#         # Adding 'side' column and combining bids and asks
#         bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'volume', 'num_orders'])
#         bids_df['side'] = 'buy'
#         asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'volume', 'num_orders'])
#         asks_df['side'] = 'sell'
#
#         # Combine and convert types
#         combined_df = pd.concat([bids_df, asks_df])
#         combined_df[['price', 'volume']] = combined_df[['price', 'volume']].apply(pd.to_numeric)
#
#         return combined_df
#
#     def get_order_book_bids_and_ask_df(self, symbol, level=2):
#         # Fetch order book from Coinbase
#         order_book = self.client.get_product_order_book(product_id=symbol, level=level)
#
#         # Create DataFrames for bids and asks
#         bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'quantity', 'num_orders'])
#         asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'quantity', 'num_orders'])
#
#         # Convert price and quantity to numeric types
#         bids_df[['price', 'quantity']] = bids_df[['price', 'quantity']].apply(pd.to_numeric)
#         asks_df[['price', 'quantity']] = asks_df[['price', 'quantity']].apply(pd.to_numeric)
#
#         return bids_df, asks_df
