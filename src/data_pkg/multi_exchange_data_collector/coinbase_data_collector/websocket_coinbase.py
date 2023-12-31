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

from src.data_pkg.ts_db.time_scale_db_operations import TimeScaleClass
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys


# def create_auth_message(api_auth_obj):
#     # api_auth_obj = CoinbaseAPIKeys()
#     api_key = api_auth_obj.api_key
#     api_secret = api_auth_obj.secret_key
#     now = int(time.time())
#     channel_name = 'level2'
#     product_ids = 'ETH-USD', 'BTC-USD' #, 'NMR-USD', 'GALA-USD', 'XRP-USD', 'FET-USD', 'SHIB-USD', 'BCH-USD'
#     str_to_sign_websocket = str(now) + channel_name + ','.join(product_ids)
#     print(str_to_sign_websocket)
#     signature_websocket = hmac.new(api_secret.encode('utf-8'),
#                                    str_to_sign_websocket.encode('utf-8'),
#                                    hashlib.sha256).hexdigest()
#     print(signature_websocket)
#     message = {
#         "type": "subscribe",
#         "channel": channel_name,
#         "api_key": api_key,
#         "product_ids": product_ids,
#         "signature": signature_websocket,
#         "timestamp": str(now)
#     }
#     return message
#
#
# async def stream_from_cbat(api_auth_obj, func):
#     url_websocket = 'wss://advanced-trade-ws.coinbase.com'
#     message = create_auth_message(api_auth_obj)
#     ws = await websockets.connect(url_websocket)
#     await ws.send(json.dumps(message))
#     # print(json.dumps(message))
#     async def receive_data():
#         while True:
#             response = await ws.recv()
#             data = json.loads(response)
#             func(data)
#
#     while True:
#         await receive_data()
#         break


def create_auth_message(product_ids, api_auth_obj):
    api_key = api_auth_obj.api_key
    api_secret = api_auth_obj.secret_key
    now = str(int(time.time()))  # Using an integer timestamp
    channel_name = 'level2'
    str_to_sign_websocket = now + channel_name + ','.join(product_ids)
    signature_websocket = hmac.new(api_secret.encode('utf-8'),
                                   str_to_sign_websocket.encode('utf-8'),
                                   hashlib.sha256).hexdigest()

    message = {
        "type": "subscribe",
        "channel": channel_name,
        "api_key": api_key,
        "product_ids": product_ids,
        "signature": signature_websocket,
        "timestamp": now
    }
    return message


async def stream_from_cbat(product_ids, api_auth_obj, func):
    url_websocket = 'wss://advanced-trade-ws.coinbase.com'
    message = create_auth_message(product_ids, api_auth_obj)

    try:
        async with websockets.connect(url_websocket) as ws:
            print("WebSocket connection established.")
            await ws.send(json.dumps(message))
            print("Sent subscription message:", json.dumps(message))

            async for response in ws:
                data = json.loads(response)
                print("Received data:", data)
                func(data)
    except Exception as e:
        print("An error occurred:", e)

def to_db(data):
    # Process and insert each event into the database
    for event in data.get('events', []):
        if event.get('type') == 'snapshot':
            for update in event.get('updates', []):
                data_dict = {
                    'timestamp': data['timestamp'],
                    'sequence_num': data['sequence_num'],
                    'product_id': event['product_id'],
                    'side': update['side'],
                    'price_level': update['price_level'],
                    'new_quantity': update['new_quantity']
                }
                print(data_dict)
                # db_obj.insert_dict_to_tsdb(
                #     data_dict,
                #     table_name='order_book_cbat',
                #     time_key='timestamp',
                #     time_column='time_column_in_your_db',
                #     symbol=event['product_id'],
                #     interval='your_interval',
                #     debug=True
                # )


async def stream_from_cbat_to_db(product_ids, api_auth_obj, func, db_obj):
    url_websocket = 'wss://advanced-trade-ws.coinbase.com'
    message = create_auth_message(product_ids, api_auth_obj)
    async with websockets.connect(url_websocket) as ws:
        await ws.send(json.dumps(message))
        while True:
            response = await ws.recv()
            data = json.loads(response)
            # func(data)
            to_db(data)
            # # Process and insert each event into the database
            # for event in data.get('events', []):
            #     if event.get('type') == 'snapshot':
            #         for update in event.get('updates', []):
            #             data_dict = {
            #                 'timestamp': data['timestamp'],
            #                 'sequence_num': data['sequence_num'],
            #                 'product_id': event['product_id'],
            #                 'side': update['side'],
            #                 'price_level': update['price_level'],
            #                 'new_quantity': update['new_quantity']
            #             }
            #             print(data_dict)
            #             db_obj.insert_dict_to_tsdb(
            #                 data_dict,
            #                 table_name='order_book_cbat',
            #                 time_key='timestamp',
            #                 time_column='time_column_in_your_db',
            #                 symbol=event['product_id'],
            #                 interval='your_interval',
            #                 debug=True
            #             )

def get_all_crypto_pairs():
    import http.client
    import json
    conn = http.client.HTTPSConnection("api.exchange.coinbase.com")
    payload = ''
    headers = {
        'Content-Type': 'application/json',
    'User-Agent': 'Python http.client'  # Add a User-Agent header

    }
    conn.request("GET", "/products", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data_decoded = data.decode("utf-8")
    print(data_decoded)
    # Convert the JSON string to a Python object (list of dicts)
    data_list = json.loads(data_decoded)

    # Write the data to a JSON file
    with open('coinbase_data.json', 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # get_all_crypto_pairs()
    api_auth_obj = CoinbaseAPIKeys()
    product_ids = ['ETH-USDT']
    # asyncio.run(stream_from_cbat(product_ids=product_ids,
    #                              api_auth_obj=api_auth_obj,
    #                              func=print))
    db_obj = TimeScaleClass()
    asyncio.run(stream_from_cbat_to_db(product_ids=product_ids,
                                       api_auth_obj=api_auth_obj,
                                       func=print,
                                       db_obj=None))


