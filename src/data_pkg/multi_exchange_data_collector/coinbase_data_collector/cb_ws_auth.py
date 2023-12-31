import requests
import base64
import hmac
import hashlib
import time
import json
import uuid
import decimal
import websockets
import asyncio

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys

api_auth_obj = CoinbaseAPIKeys()

api_key = api_auth_obj.api_key
api_secret = api_auth_obj.secret_key


now = int(time.time())

# Get account info
# url_accounts1 = 'https://coinbase.com/api/v3/brokerage/accounts'
# str_to_sign_accounts1 = str(now) + 'GET' + '/api/v3/brokerage/accounts' + ''
# signature_accounts1 = hmac.new(api_secret.encode('utf-8'),
#                                str_to_sign_accounts1.encode('utf-8'),
#                                hashlib.sha256).hexdigest()
#
# headers_accounts1 = {
#     "CB-ACCESS-SIGN": signature_accounts1,
#     "CB-ACCESS-TIMESTAMP": str(now),
#     "CB-ACCESS-KEY": api_key,
#
#
# }
# response_accounts1 = requests.request('get', url_accounts1, headers=headers_accounts1)
# print(response_accounts1.status_code)
# print(response_accounts1.json())


# Get account balance of BTC
# btc_balance1 = 0
# for account1 in response_accounts1.json()['accounts']:
#     if account1['currency'] == 'BTC':
#         btc_balance1 = account1['available_balance']['value']
# print(btc_balance1)


# Get account balance of ETH
# eth_balance1 = 0
# for account1 in response_accounts1.json()['accounts']:
#     if account1['currency'] == 'ETH':
#         eth_balance1 = account1['available_balance']['value']
# print(eth_balance1)


# Get account balance of USDT
# usdt_balance1 = 0
# for account1 in response_accounts1.json()['accounts']:
#     if account1['currency'] == 'USDT':
#         usdt_balance1 = account1['available_balance']['value']
# print(usdt_balance1)


# subscribe to and get websocket feed

url_websocket = 'wss://advanced-trade-ws.coinbase.com'
channel_name = 'level2'
product_ids = 'ETH-USDT', 'ETH-EUR'
str_to_sign_websocket = str(now) + channel_name + ','.join(product_ids)
print(str_to_sign_websocket)
signature_websocket = hmac.new(api_secret.encode('utf-8'), str_to_sign_websocket.encode('utf-8'),  hashlib.sha256).hexdigest()
print(signature_websocket)
message = {
  "type": "subscribe",
  "channel": channel_name,
  "api_key": api_key,
  "product_ids": product_ids,
  "signature": signature_websocket,
  "timestamp": str(now)
}

# async def main():
#     ws = await websockets.connect(url_websocket)
#     await ws.send(json.dumps(message))
#     print(json.dumps(message))
#     async def receive_data():
#         while True:
#             response = await ws.recv()
#             data = json.loads(response)
#             print(data)
#
#     while True:
#         await receive_data()

async def receive_data(ws):
    while True:
        response = await ws.recv()
        data = json.loads(response)
        print(data)
async def main():
    ws = await websockets.connect(url_websocket)
    await ws.send(json.dumps(message))
    print(json.dumps(message))

    while True:
        await receive_data(ws)

if __name__ == '__main__':
    asyncio.run(main())