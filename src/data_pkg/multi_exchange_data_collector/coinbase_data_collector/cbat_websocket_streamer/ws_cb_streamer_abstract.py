from abc import ABC, abstractmethod
import asyncio
import hashlib
import hmac
import json
import time
import pandas as pd
import websockets
import backoff

from src.data_pkg.multi_exchange_data_collector.coinbase_data_collector.cb_db_utils import random_backoff_generator
from src.data_pkg.ts_db.time_scale_db_operations import TimeScaleClass


class CbWebSocketStreamer(ABC):
    def __init(self,
               channel_name,
               api_auth_obj,
               threshold_days,
               table_name,
               timr_key, #
               time_column, # The name of the output column
               debug):
        self.channel_name = channel_name
        self.api_auth_obj = api_auth_obj
        self.threshold_days = threshold_days
        self.table_name = table_name
        self.time_key = timr_key
        self.time_column = time_column
        self.debug = debug
        self.tsdb_obj = TimeScaleClass()

    def _create_auth_message(self, product_ids):
        api_key = self.api_auth_obj.api_key
        api_secret = self.api_auth_obj.secret_key
        now = str(int(time.time()))  # Using an integer timestamp
        str_to_sign_websocket = now + self.channel_name + ','.join(product_ids)
        signature_websocket = hmac.new(api_secret.encode('utf-8'),
                                       str_to_sign_websocket.encode('utf-8'),
                                       hashlib.sha256).hexdigest()

        message = {
            "type": "subscribe",
            "channel": self.channel_name,
            "api_key": api_key,
            "product_ids": product_ids,
            "signature": signature_websocket,
            "timestamp": now
        }
        return message

    @abstractmethod
    def _convert_to_df(self, event, **kwargs):
        pass

    @abstractmethod
    def _to_db(self, data):
        pass

    @backoff.on_exception(random_backoff_generator(2, 5), Exception, max_tries=8)
    async def stream_from_cbat_to_db(self, product_ids, **kwargs):
        url_websocket = 'wss://advanced-trade-ws.coinbase.com'
        message = self._create_auth_message(product_ids)
        async with websockets.connect(url_websocket, max_size=1_000_000_000) as ws:
            await ws.send(json.dumps(message))
            while True:
                response = await ws.recv()
                data = json.loads(response)
                self._to_db(data)














