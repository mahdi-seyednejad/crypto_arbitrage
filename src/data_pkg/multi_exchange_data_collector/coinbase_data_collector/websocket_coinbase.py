import asyncio
import hashlib
import hmac
import json
import time
import pandas as pd
import websockets
import backoff


from src.data_pkg.multi_exchange_data_collector.coinbase_data_collector.timestamp_adjustement import TimeAdjuster
from src.data_pkg.multi_exchange_data_collector.coinbase_data_collector.ws_cb_config import Important_Symbol_Pairs
from src.data_pkg.ts_db.time_scale_db_operations import TimeScaleClass
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, CoinbaseAPIKeys02

Threshold_Days = 200 # To define id the timestamp is too old
Table_Name = 'order_book_cbat_ws'
debug = True


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

def truncate_timestamp(timestamp):
    """ Truncate the fractional seconds in the timestamp to six decimal places. """
    if '.' in timestamp:
        main_part, fractional_part = timestamp.split('.')
        fractional_part = fractional_part[:6]  # Keep only six decimal places
        return f'{main_part}.{fractional_part}'
    return timestamp


tsdb_obj = TimeScaleClass()

def convert_to_df(event, seq_num, time_adjuster, time_column):
    df = pd.DataFrame(event.get('updates', []))
    df[time_column] = df.apply(lambda row: time_adjuster.check_and_adjust_timestamp(row['event_time']), axis=1)
    # df[time_column] = pd.to_datetime(df[time_column])
    df[time_column] = pd.to_datetime(df[time_column], format='%Y-%m-%dT%H:%M:%S.%f%z')

    df['sequence_num'] = seq_num
    df['product_id'] = event['product_id']
    if debug:
        print("df.tail():\n", df.tail().to_string())
    return df


def to_db(data, time_column='event_time'):
    time_adjuster = TimeAdjuster(current_time=data['timestamp'])
    # Process and insert each event into the database
    for event in data.get('events', []):
        # print("event.keys(): \n", event.keys())
        event_type = event.get('type')
        if not event_type:
            break

        if (event_type == 'snapshot') or ("update" in event_type):
            df = convert_to_df(event, data['sequence_num'], time_adjuster, time_column)

            tsdb_obj.insert_df_to_tsdb(df_in=df,
                                       table_name=Table_Name,
                                       time_column=time_column,
                                       date_as_index=False,
                                       primary_keys=['product_id', 'price_level', 'side'],
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
    api_auth_obj = CoinbaseAPIKeys02()
    product_ids = Important_Symbol_Pairs
    db_obj = TimeScaleClass()
    asyncio.run(stream_from_cbat_to_db(product_ids=product_ids,
                                       api_auth_obj=api_auth_obj,
                                       func=print,
                                       db_obj=None))


