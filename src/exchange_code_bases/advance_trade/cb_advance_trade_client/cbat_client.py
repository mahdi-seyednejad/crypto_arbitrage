import requests
import pandas as pd
import json
from requests.auth import AuthBase
import http.client

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_code_bases.abstract_classes.crypto_clients import CryptoClient
from src.exchange_code_bases.advance_trade.client_authentication.coinbase_auth import CoinbaseAuth


class CbAdvanceTradeClient(CryptoClient):
    def __init__(self, api_auth_obj: APIAuthClass):
        self.api_key = api_auth_obj.api_key
        self.api_secret = api_auth_obj.secret_key
        self.auth = CoinbaseAuth(self.api_key, self.api_secret)
        if api_auth_obj.is_testnet:
            self.base_url = 'https://api-public.sandbox.pro.coinbase.com'
        else:
            self.base_url = 'https://api.coinbase.com'

    def fetch_account_info(self):
        url = f'{self.base_url}/v2/accounts'
        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            return response.json()
        else:
            # Handle error
            return response.json()

    def withdraw_to_address(self, address, amount, currency):
        url = f'{self.base_url}/v2/accounts/{currency}/transactions'
        data = {
            'type': 'send',
            'to': address,
            'amount': amount,
            'currency': currency
        }
        response = requests.post(url, json=data, auth=self.auth)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            # Handle error
            return response.json()

    def fetch_deposit_address(self, currency):
        # This endpoint and method might vary based on Coinbase's API documentation
        url = f'{self.base_url}/v2/accounts/{currency}/addresses'
        response = requests.post(url, auth=self.auth)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            # Handle error
            return response.json()

    def fetch_budget(self, currency='USD'):
        url = f'{self.base_url}/v2/accounts'
        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            accounts = response.json().get('data', [])
            df = pd.DataFrame(accounts)
            if currency in df['currency'].values:
                account = df[df['currency'] == currency].iloc[0]
                return {
                    'balance': account['balance']['amount'],
                    'currency': account['balance']['currency']
                }
            else:
                return {'message': 'Currency not found'}
        else:
            # Handle error
            return response.json()

    def create_order(self, order_type, amount, currency, price=None):
        url = f'{self.base_url}/orders'
        data = {
            'side': order_type,  # 'buy' or 'sell'
            'product_id': f'{currency}-USD',
            'size': amount
        }
        if price:
            data['price'] = price
            data['type'] = 'limit'
        else:
            data['type'] = 'market'

        response = requests.post(url, json=data, auth=self.auth)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            # Handle error
            return response.json()

    def fetch_available_cryptos(self):
        account_info = self.fetch_account_info()
        if 'data' in account_info:
            return {item['currency']: item['balance'] for item in account_info['data'] if
                    float(item['balance']) > 0}
        else:
            return {}

    def fetch_all_available_base_assets(self):
        available_cryptos = self.fetch_available_cryptos()
        return list(available_cryptos.keys())

    def fetch_order_book(self, product_id, level=2):
        url = f"https://api.exchange.coinbase.com/products/{product_id}/book?level={level}"
        response = requests.get(url)
        if response.status_code == 200:
            order_book = response.json()
            return order_book
        else:
            print("Failed to retrieve the order book for the given product ID: ", product_id)
            return None
