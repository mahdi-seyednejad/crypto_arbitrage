import requests
import hmac
import hashlib
import time
import pandas as pd
from requests.auth import AuthBase


class CoinbaseAuth(AuthBase):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = timestamp + request.method + request.path_url
        if request.body:
            message += request.body.decode('utf-8')  # Decode the body to string

        # message = timestamp + request.method + request.path_url + (request.body or '')
        signature = hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

        request.headers.update({
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
        })
        return request

    def get_account_info(self):
        url = 'https://api.coinbase.com/v2/accounts'
        response = requests.get(url, auth=self)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def create_asset_dataframe(self, data):
        asset_data = []
        for asset in data:
            asset_info = {
                'Asset ID': asset['id'],
                'Name': asset['name'],
                'Type': asset['currency']['type'],
                'Amount': float(asset['balance']['amount'])
            }
            asset_data.append(asset_info)

        return pd.DataFrame(asset_data)


def get_available_amount(data, asset_name):
    for asset in data:
        if asset['name'] == asset_name:
            return float(asset['balance']['amount'])
    return None  # If the asset name is not found
