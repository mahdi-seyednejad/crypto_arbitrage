import requests
import pandas as pd
import json
from requests.auth import AuthBase
import http.client

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.utils.data_utils.coinbace_fetch_df import fetch_account_info_to_dataframe
from src.exchange_arbitrage_pkg.utils.order_uuid import generate_unique_order_id
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
        response_df = fetch_account_info_to_dataframe(url=url, auth=self.auth)
        return response_df

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

    def check_balance_coinbase(self, symbol):
        df = self.fetch_account_info()
        try:
            # Assuming 'currency.code' is the column name for currency codes after normalization
            matching_account = df[df['currency.code'] == symbol]
            if not matching_account.empty:
                # Assuming 'balance.amount' is the column name for balance amounts
                return matching_account['balance.amount'].iloc[0]
            else:
                return 'Currency not found'
        except Exception as e:
            print(f"Error checking balance for {symbol} on Coinbase Pro: {e}")
            return None

    def fetch_deposit_address(self, currency):
        # This endpoint and method might vary based on Coinbase's API documentation
        url = f'{self.base_url}/v2/accounts/{currency}/addresses'
        response = requests.post(url, auth=self.auth)
        if response.status_code in [200, 201]:
            return response.json()['data']['deposit_uri']
        else:
            # Handle error
            return response.json()['data']['deposit_uri']

    def fetch_budget(self, currency='USD'):
        url = f'{self.base_url}/v2/accounts'
        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            accounts = response.json().get('data', [])
            df = pd.DataFrame(accounts)

            # Extract currency code from the dictionaries in the 'currency' column
            df['currency_code'] = df['currency'].apply(lambda x: x.get('code'))

            if currency in df['currency_code'].values:
                account = df[df['currency_code'] == currency].iloc[0]
                return {
                    'balance': account['balance']['amount'],
                    'currency': account['currency']['code']
                }
            else:
                return {'message': 'Currency not found'}
        else:
            # Handle error
            return response.json()

    # def create_order(self, currency, amount, side=None, order_type='market'):
    #     formatted_amount = "{:.8f}".format(amount)
    #     if 'USD' in currency:
    #         product_id = currency
    #     else:
    #         product_id = f'{currency}-USD'
    #     # product_details = getProduct(product_id) --> product_id
    #     order_configuration = {'base_size': str(formatted_amount)}
    #     order_type = 'market_market_ioc'
    #
    #     payload = {
    #         "client_order_id": generate_unique_order_id(currency),
    #         "product_id": product_id,
    #         "side": side,
    #         "order_configuration": {
    #             order_type: order_configuration
    #         }
    #     }
    #     headers = {
    #         'Content-Type': 'application/json'
    #     }
    #
    #     # url = f'{self.base_url}/orders'
    #     url = "https://api.coinbase.com/api/v3/brokerage/orders"
    #
    #     response = requests.post(url,
    #                              json=payload,
    #                              auth=self.auth,
    #                              headers=headers)
    #
    #     if response.status_code in [200, 201]:
    #         try:
    #             return response.json()
    #         except Exception as e:
    #             print(f"Error checking balance for {currency}: {e}")
    #         except requests.exceptions.JSONDecodeError:
    #             # Handle the case where JSON decoding fails
    #             print(f"Failed to decode JSON. Status Code: {response.status_code}, Response: {response.text}")
    #             return None
    #     else:
    #         # Handle error
    #         return None

    # def create_order(self, order_type, amount, currency, price=None):
    #     client_order_id = generate_unique_order_id(currency)
    #     formatted_amount = "{:.8f}".format(amount)
    #     if 'USD' in currency:
    #         product_id = currency
    #     else:
    #         product_id = f'{currency}-USD'
    #
    #     # Prepare the payload
    #     payload = {
    #                   "order_configuration": {
    #                       "limit_limit_gtd": {
    #                           "base_size": formatted_amount
    #                       }
    #                   },
    #                   "side": order_type.upper() ,  # 'buy' or 'sell'
    #                   "product_id": product_id,
    #                   "client_order_id": client_order_id # Generate or define the client_order_id
    #     }
    #     if price:
    #         payload['price'] = price
    #         payload['type'] = 'limit'
    #     else:
    #         payload['type'] = 'market'
    #
    #     # Making the request
    #     response = requests.post(f"{self.base_url}/api/v3/brokerage/orders", json=payload, auth=self.auth)
    #
    #     if response.status_code in [200, 201]:
    #         try:
    #             return response.json()
    #         except json.JSONDecodeError:
    #             print(f"Failed to decode JSON. Status Code: {response.status_code}, Response: {response.text}")
    #             return None
    #     else:
    #         print(f"Error: {response.status_code}, {response.text}")
    #         return None

    # Example usage
    # client = CoinbaseTradingClient("<API_KEY>", "<API_SECRET>", "<PASSPHRASE>")
    # order_response = client.create

    def create_order(self, order_type, amount, currency, price=None):
        if 'USD' in currency:
            product_id = currency
        else:
            product_id = f'{currency}-USD'
        formatted_amount = "{:.8f}".format(amount)

        payload = {
            "client_order_id": "1212",
            "product_id": product_id,
            "side": order_type.upper(),
            "order_configuration": {
                "market_market_ioc": {
                    "base_size": str(formatted_amount)
                }
            }
        }

        url = "https://api.coinbase.com/api/v3/brokerage/orders"

        response = requests.post(url, json=payload, auth=self.auth)
        if response.status_code in [200, 201]:
            try:
                return response.json(),
            except Exception as e:
                print(f"Error checking balance for {currency}: {e}")
                return response.json(), -1
            except requests.exceptions.JSONDecodeError:
                # Handle the case where JSON decoding fails
                print(f"Failed to decode JSON. Status Code: {response.status_code}, Response: {response.text}")
                return response.json(), -1
        else:
            # Handle error
            return response.json(), -1

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
