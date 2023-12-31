import requests
import pandas as pd
import http.client
import json
from requests.auth import AuthBase
import http.client
from decimal import Decimal
from coinbase.wallet.client import Client


from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.utils.data_utils.coinbace_fetch_df import fetch_account_info_to_dataframe
from src.exchange_arbitrage_pkg.utils.order_uuid import generate_unique_order_id
from src.exchange_code_bases.abstract_classes.crypto_clients import CryptoClient
from src.exchange_code_bases.advance_trade.client_authentication.coinbase_auth import CoinbaseAuth
from src.exchange_code_bases.advance_trade.error_handling.handle_withdraw_response import check_insufficient_funds_error


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

    def check_balance_coinbase(self, symbol):
        df = self.fetch_account_info()
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

    def fetch_supported_networks(self):
        # Using the Exchange/Pro API endpoint for currencies
        url = f'https://api.exchange.coinbase.com/currencies'
        try:
            response = requests.get(url, auth=self.auth)
            if response.status_code == 200:
                return response.json()
            else:
                # Handle error response
                return response.json()
        except Exception as e:
            print(f"Error fetching supported networks from Coinbase: {e}")
            return {}

    def withdraw_to_address(self, address, amount, currency):
        url = f'{self.base_url}/v2/accounts/{currency}/transactions'
        data = {
            'type': 'send',
            'to': address,
            'amount': str(amount),
            'currency': currency
        }
        try:
            response = requests.post(url, json=data, auth=self.auth)
            if response.status_code in [200, 201]:
                return response.json()
            else:
                # Handle error
                return response.json()
        except Exception as e:
            print(f"Withdrawing selling {currency} on Binance: {e}")

    def withdraw_to_address_persistent(self, address, amount, currency, amount_adjuster, max_attempts):
        attempt = 0
        last_response = None  # Initialize last_response
        trading_amount = amount
        api_version = '2023-08-18'  # Replace with the actual version date you want to use

        headers = {'CB-VERSION': api_version}

        while attempt < max_attempts:
            url = f'{self.base_url}/v2/accounts/{currency}/transactions'
            data = {
                'type': 'send',
                'to': address,
                'amount': str(trading_amount),
                'currency': currency
            }
            try: # Just added headers=headers,
                response = requests.post(url, json=data, headers=headers,  auth=self.auth)
                last_response = response  # Update last_response each time

                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    if check_insufficient_funds_error(response.json()):
                        attempt += 1
                        new_amount = Decimal('0.95') * trading_amount
                        trading_amount = amount_adjuster(new_amount)
                    else:
                        # Other errors: return the response
                        return response.json()
            except Exception as e:
                print(f"Error withdrawing {currency}: {e}")
                last_response = None  # Update last_response in case of an exception

        # If the loop exits without a successful withdrawal, return the last error
        return last_response.json() if last_response else None

    def fetch_deposit_address(self, currency):
        # This endpoint and method might vary based on Coinbase's API documentation
        url = f'{self.base_url}/v2/accounts/{currency}/addresses'
        response = requests.post(url, auth=self.auth)
        if response.status_code in [200, 201]:
            response_data = response.json()['data']
            return {'address': response_data['address'],
                    'network': response_data['network']}
        else:
            # Handle error
            return response.json()['data']['address']

    def fetch_all_deposit_addresses(self, currencies):
        all_addresses = {}
        for currency in currencies:
            address_info = self.fetch_deposit_address(currency)
            if address_info:
                all_addresses[currency] = address_info
        return all_addresses

    def fetch_budget(self, currency='USD'):
        url = f'{self.base_url}/api/v3/brokerage/accounts'
        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            accounts = response.json().get('accounts', [])
            df = pd.DataFrame(accounts)
            # Extract currency code from the dictionaries in the 'currency' column
            res = df.loc[df['currency'] == currency]
            if not res.empty:
                # return res.iloc[0]['available_balance']['value']
                return {
                    'balance': res.iloc[0]['available_balance']['value'],
                    'currency': res.iloc[0]['available_balance']['currency']
                }
            else:
                return {'message': 'Currency not found'}
        else:
            # Handle error
            return {'error': response.json(), 'status_code': response.status_code}

    def create_order(self, order_type, amount, currency, price=None):
        if 'USD' in currency:
            product_id = currency
        else:
            product_id = f'{currency}-USD'
        formatted_amount = "{:.8f}".format(amount)

        # Determine the key for the amount based on the order type
        amount_key = "quote_size" if order_type.upper() == "BUY" else "base_size"

        payload = {
            "client_order_id": generate_unique_order_id(currency),
            "product_id": product_id,
            "side": order_type.upper(),
            "order_configuration": {
                "market_market_ioc": {
                    amount_key: str(formatted_amount)
                }
            }
        }

        url = "https://api.coinbase.com/api/v3/brokerage/orders"

        response = requests.post(url, json=payload, auth=self.auth)

        output = {}, -1
        if response.status_code in [200, 201]:
            try:
                return response.json(),
            except Exception as e:
                print(f"Error processing order for {currency}: {e}")
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

    # def get_latest_prices_coinbase_at(self, sample_size=None):
    #     url = "https://api.coinbase.com/api/v3/brokerage/products?limit=3&product_type=SPOT"
    #     headers = {
    #         'Content-Type': 'application/json'
    #     }
    #
    #     # Send the GET request
    #     response = requests.get(url, headers=headers, auth=self.auth)
    #     conn = http.client.HTTPSConnection("api.coinbase.com")
    #     conn.request("GET", url, '', headers)
    #     res = conn.getresponse()
    #     data = res.read()
    #     print(data.decode("utf-8"))
    #     # Check if the response is successful
    #     if response.status_code == 200:
    #         # Print the response data
    #         return(response.json())
    #     else:
    #         print(f"Failed to retrieve data. Status code: {response.status_code}")
    #         return None

        # conn = http.client.HTTPSConnection("api.coinbase.com")
        # payload = ''
        # headers = {
        #     'Content-Type': 'application/json'
        # }
        # conn.request("GET", "/api/v3/brokerage/products?limit=3&product_type=SPOT", payload, headers)
        # res = conn.getresponse()
        # data = res.read()
        # print(data.decode("utf-8"))
        # url = f"{self.base_url}/api/v3/brokerage/products?product_type=SPOT"
        # response = requests.get(url, headers=self.auth)
        # if response.status_code == 200:
        #     products_data = response.json()
        #     product_info = [(product['product_id'], product['price']) for product in products_data['products']]
        #
        #     # Convert to DataFrame
        #     df_products = pd.DataFrame(product_info, columns=['product_id', 'price'])
        #
        #     if sample_size:
        #         df_products = df_products.sample(sample_size)
        #
        #     return df_products
        # else:
        #     print("Failed to retrieve latest prices.")
        #     return None

    # def fetch_withdrawal_fee_estimate(self, currency, crypto_address, network):
    #     url = "https://api.exchange.coinbase.com/withdrawals/fee-estimate"
    #     params = {
    #         'currency': currency,
    #         'crypto_address': crypto_address,
    #         'network': network
    #     }
    #     headers = {
    #         'Content-Type': 'application/json'
    #     }
    #
    #     try:
    #         response = requests.get(url, headers=headers, params=params, auth=self.auth)
    #         if response.status_code == 200:
    #             return response.json()
    #         else:
    #             print(f"Error fetching withdrawal fee estimate: Status Code {response.status_code}, Response: {response.text}")
    #             return {'message': response.text}
    #     except Exception as e:
    #         print(f"Exception occurred: {e}")
    #         return {'message': str(e)}

    # def get_coinbase_symbol_details(client, symbol):
    #     df = client.fetch_account_info()
    #     if df is not None:
    #         buy_precision = df['base_increment']
    #         min_buy_amount = df['base_min_size']
    #         min_notional = df['min_market_funds']
    #         return buy_precision, min_buy_amount, min_notional
    #     return None, None, None
    #
