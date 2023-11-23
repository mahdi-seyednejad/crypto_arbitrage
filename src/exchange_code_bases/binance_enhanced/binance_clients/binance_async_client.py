import asyncio
from binance import AsyncClient

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_code_bases.abstract_classes.crypto_clients import CryptoClient


class BinanceAsyncClient(CryptoClient):
    def __init__(self, api_auth_obj: APIAuthClass):
        self.client = None
        self.api_key = api_auth_obj.api_key
        self.api_secret = api_auth_obj.secret_key
        self.testnet = api_auth_obj.is_testnet

    async def create_client(self):
        self.client = await AsyncClient.create(self.api_key,
                                               self.api_secret,
                                               testnet=self.testnet,
                                               tld="us",
                                               requests_params={'timeout': 20})
        return self.client

    async def fetch_account_info(self):
        # Ensure the client is created
        if not self.client:
            await self.create_client()
        return await self.client.get_account()

    async def fetch_deposit_address(self, currency):
        if not self.client:
            await self.create_client()
        return await self.client.get_deposit_address(coin=currency)

    async def withdraw_to_address(self, address, amount, currency):
        if not self.client:
            await self.create_client()
        return await self.client.withdraw(coin=currency, amount=amount, address=address)

    async def fetch_budget(self, currency='USDT'):
        account_info = await self.fetch_account_info()
        balances = account_info['balances']

        if currency in [balance['asset'] for balance in balances]:
            account = [balance for balance in balances if balance['asset'] == currency][0]
            return {
                'balance': account['free'],
                'currency': account['asset']
            }
        else:
            return {'message': 'Currency not found'}

    async def fetch_available_cryptos(self):
        account_info = await self.fetch_account_info()
        return {balance['asset']: balance['free'] for balance in account_info['balances'] if float(balance['free']) > 0}

    async def fetch_available_budget(self, base_symbol, quota_symbol="USDT", quota=1):
        available_cryptos = await self.fetch_available_cryptos()

        if base_symbol in available_cryptos and quota_symbol in available_cryptos:
            base_asset_amount = float(available_cryptos[base_symbol])
            quota_asset_amount = float(available_cryptos[quota_symbol])
            return min(base_asset_amount, quota_asset_amount * quota)
        else:
            return 0

    async def fetch_all_available_base_assets(self):
        available_cryptos = await self.fetch_available_cryptos()
        return list(available_cryptos.keys())

    async def create_order(self, order_type, amount, currency, price=None):
        symbol = f'{currency}USDT'  # Example: 'BTCUSDT', assuming USDT pair
        side = 'BUY' if order_type.lower() == 'buy' else 'SELL'

        try:
            if price:
                # Create an asynchronous limit order
                order = await self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type='LIMIT',
                    timeInForce='GTC',  # Good Till Canceled
                    quantity=amount,
                    price=str(price)
                )
            else:
                # Create an asynchronous market order
                order = await self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=amount
                )
            return order
        except Exception as e:
            # Handle any exceptions (like insufficient funds, etc.)
            return {'message': str(e)}

    async def fetch_order_book(self, symbol, limit=100):
        if not self.client:
            await self.create_client()
        return await self.client.get_order_book_sync(symbol=symbol, limit=limit)
