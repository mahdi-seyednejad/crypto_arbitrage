from binance.client import Client
import pandas as pd

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_code_bases.abstract_classes.crypto_clients import CryptoClient
from src.exchange_code_bases.binance_enhanced.crypto_network_binance.binance_network_extractor import \
    process_coins_info_binance_df


class BinanceSyncClient(CryptoClient):
    def __init__(self, api_auth_obj: APIAuthClass):
        self.api_key = api_auth_obj.api_key
        self.api_secret = api_auth_obj.secret_key
        self.testnet = api_auth_obj.is_testnet
        self.client = Client(api_auth_obj.api_key,
                             api_auth_obj.secret_key,
                             testnet=self.testnet,
                             tld="us",
                             requests_params={'timeout': 20})

    def fetch_account_info(self):
        # Implement the method using Binance API
        return self.client.get_account()

    def withdraw_to_address(self, address, amount, currency):
        # Implement the method using Binance API
        return self.client.withdraw(coin=currency, amount=amount, address=address)

    def fetch_deposit_address(self, currency):
        try:
            response = self.client.get_deposit_address(coin=currency)
            if response and 'address' in response:
                return response
            else:
                return {'message': 'Failed to retrieve deposit address'}
        except Exception as e:
            return {'message': str(e)}

    def fetch_budget(self, currency='USDT'):  # Default to 'USDT' for Binance
        account_info = self.client.get_account()
        balances = account_info['balances']
        df = pd.DataFrame(balances)

        if currency in df['asset'].values:
            account = df[df['asset'] == currency].iloc[0]
            return {
                'balance': account['free'],  # 'free' indicates available balance
                'currency': account['asset']
            }
        else:
            return {
                'balance': 0,
                'currency': currency
            }

    def fetch_available_cryptos(self):
        account_info = self.fetch_account_info()
        return {balance['asset']: balance['free'] for balance in account_info['balances'] if float(balance['free']) > 0}

    def fetch_available_budget(self, base_symbol, quota_symbol="USDT", quota=1):
        available_cryptos = self.fetch_available_cryptos()

        # Check if both the base and quota assets are in the available cryptos
        if base_symbol in available_cryptos and quota_symbol in available_cryptos:
            base_asset_amount = float(available_cryptos[base_symbol])
            quota_asset_amount = float(available_cryptos[quota_symbol])

            # Calculate the budget based on the quota
            return min(base_asset_amount, quota_asset_amount * quota)
        else:
            # Handle the case where one or both assets are not in the available cryptos
            return 0

    def fetch_all_available_base_assets(self):
        available_cryptos = self.fetch_available_cryptos()
        return list(available_cryptos.keys())

    def create_order(self, order_type, amount, currency, price=None):
        symbol = f'{currency}USDT'  # Example: 'BTCUSDT', assuming USDT pair
        side = 'BUY' if order_type.lower() == 'buy' else 'SELL'

        try:
            if price:
                # Create a limit order
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type='LIMIT',
                    timeInForce='GTC',  # Good Till Canceled
                    quantity=amount,
                    price=str(price)
                )
            else:
                # Create a market order
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=amount
                )
            return order
        except Exception as e:
            # Handle any exceptions (like insufficient funds, etc.)
            return {'message': str(e)}

    def fetch_order_book(self, symbol, limit=100):
        # Implement the method using Binance API
        return self.client.get_order_book(symbol=symbol, limit=limit)

    def get_all_symbol_info(self):
        all_coins_info = self.client.get_all_coins_info()
        df, unique_networks, coin_network_mapping = process_coins_info_binance_df(all_coins_info)
        return df
