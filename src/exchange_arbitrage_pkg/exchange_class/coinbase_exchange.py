import asyncio
from concurrent.futures import ThreadPoolExecutor
import cbpro

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass


class CoinbaseBaseSyncClient(cbpro.AuthenticatedClient):
    def get_deposit_address(self, currency):
        # Fetch all accounts
        accounts = self.get_accounts()

        # Find the account with the matching currency
        account_id = None
        for acc in accounts:
            if acc.get('currency') == currency:
                account_id = acc.get('id')
                break

        if account_id is None:
            raise Exception(f"No account found for currency {currency}")

        # Fetch the deposit information for the identified account
        deposit_info = self.get_deposit_address(account_id)
        return deposit_info


class CoinbaseAsyncClient(CoinbaseBaseSyncClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread_executor = ThreadPoolExecutor()

    async def async_wrap(self, sync_function, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_executor,
                                          lambda: sync_function(*args, **kwargs))

    def thread_clean_up(self):
        self.thread_executor.shutdown(wait=True)

    def get_accounts(self):
        return self.async_wrap(super().get_accounts)

    def place_order(self, product_id, side, order_type, price=None, size=None):
        return self.async_wrap(super().place_order, product_id=product_id, side=side, type=order_type, price=price,
                               size=size)

    def crypto_withdraw(self, amount, currency, crypto_address):
        return self.async_wrap(super().crypto_withdraw, amount=amount, currency=currency, crypto_address=crypto_address)

    async def get_deposit_address(self, currency):
        # First, find the account ID for the given currency
        accounts = await self.async_wrap(super().get_accounts)
        account_id = next((acc['id'] for acc in accounts if acc['currency'] == currency), None)

        if account_id is None:
            raise Exception(f"Account not found for currency: {currency}")

        # Now, fetch the deposit information for this account
        deposit_info = await self.async_wrap(super().get_deposit_address, account_id)
        return deposit_info


class CoinbaseExchange(ExchangeAbstractClass):
    def __init__(self, api_auth_obj: APIAuthClass):
        super().__init__(ExchangeNames.Binance, api_auth_obj)
        if self.api_auth_obj.is_testnet:
            sandbox_url = "https://api-public.sandbox.pro.coinbase.com"
            self.client = CoinbaseBaseSyncClient(key=self.api_auth_obj.api_key,
                                                 b64secret=self.api_auth_obj.secret_key,
                                                 passphrase=self.api_auth_obj.pass_phrase,
                                                 api_url=sandbox_url)

            self.async_client = CoinbaseAsyncClient(key=self.api_auth_obj.api_key,
                                                    b64secret=self.api_auth_obj.secret_key,
                                                    passphrase=self.api_auth_obj.pass_phrase,
                                                    api_url=sandbox_url)

        else:
            self.client = CoinbaseBaseSyncClient(key=self.api_auth_obj.api_key,
                                                 b64secret=self.api_auth_obj.secret_key,
                                                 passphrase=self.api_auth_obj.pass_phrase)

            self.async_client = CoinbaseAsyncClient(key=self.api_auth_obj.api_key,
                                                    b64secret=self.api_auth_obj.secret_key,
                                                    passphrase=self.api_auth_obj.pass_phrase)



