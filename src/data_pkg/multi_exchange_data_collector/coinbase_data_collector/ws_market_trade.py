import asyncio
import hashlib
import hmac
import json
import time
import pandas as pd
import websockets
import backoff

from src.data_pkg.multi_exchange_data_collector.coinbase_data_collector.ws_cb_config import Important_Symbol_Pairs
from src.data_pkg.ts_db.time_scale_db_operations import TimeScaleClass
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys


Table_Name = 'market_trades_cbat_ws'
debug = False


def create_auth_message(product_ids, api_auth_obj):
    api_key = api_auth_obj.api_key
    api_secret = api_auth_obj.secret_key
    now = str(int(time.time()))  # Using an integer timestamp
    channel_name = "market_trades"
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


def convert_trades_to_df(event, time_key, time_column):
    df = pd.DataFrame(event.get('trades', []))
    df[time_column] = pd.to_datetime(df[time_key], format='%Y-%m-%dT%H:%M:%S.%f%z')
    if debug:
        print("df.tail():\n", df.tail().to_string())
    return df


def to_db(data, time_column='trade_time'):
    # Process and insert each event into the database
    tsdb_obj = TimeScaleClass()

    for event in data.get('events', []):
        event_type = event.get('type')
        if not event_type:
            break
        if (event_type == 'snapshot') or ("update" in event_type):
            if len(event['trades'])> 0:
                df = convert_trades_to_df(event, 'time', time_column)
                tsdb_obj.insert_df_to_tsdb(df_in=df,
                                           table_name=Table_Name,
                                           time_column=time_column,
                                           date_as_index=False,
                                           primary_keys=['trade_id', 'product_id', 'side'],
                                           debug=debug)
                if debug:
                    print("df.tail():\n", df.tail().to_string())
    if debug:
        print("Done with current snapshot!")

@backoff.on_exception(backoff.expo, websockets.WebSocketException, max_tries=8)
async def stream_from_cbat_to_db(product_ids, api_auth_obj, func, db_obj):
    url_websocket = 'wss://advanced-trade-ws.coinbase.com'
    message = create_auth_message(product_ids, api_auth_obj)
    async with websockets.connect(url_websocket, max_size=1_000_000_000) as ws:
        await ws.send(json.dumps(message))
        while True:
            response = await ws.recv()
            data = json.loads(response)
            to_db(data)


if __name__ == '__main__':
    api_auth_obj = CoinbaseAPIKeys()
    product_ids = Important_Symbol_Pairs
    db_obj = TimeScaleClass()
    asyncio.run(stream_from_cbat_to_db(product_ids=product_ids,
                                       api_auth_obj=api_auth_obj,
                                       func=print,
                                       db_obj=None))
