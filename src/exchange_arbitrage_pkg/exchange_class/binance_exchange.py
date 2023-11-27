from binance import AsyncClient
from binance.client import Client
import pandas as pd

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass
from src.exchange_code_bases.abstract_classes.crypto_clients import CryptoClient
from src.exchange_code_bases.binance_enhanced.binance_clients.binance_async_client import BinanceAsyncClient
from src.exchange_code_bases.binance_enhanced.binance_clients.binance_sync_client import BinanceSyncClient


class BinanceExchange(ExchangeAbstractClass):
    def __init__(self, api_auth_obj: APIAuthClass):
        super().__init__(ExchangeNames.Binance, api_auth_obj)
        self.sync_client = BinanceSyncClient(api_auth_obj=self.api_auth_obj)
        self.vol_col_key = "binance_volume_col"
        self.budget = None

    def create_async_client(self):
        self.async_obj = BinanceAsyncClient(api_auth_obj=self.api_auth_obj)
        return self.async_obj.create_client()

    def get_order_book_sync(self, client: CryptoClient, symbol, limit=100):
        order_book = client.fetch_order_book(symbol=symbol, limit=limit)

        # Adding 'side' column and combining bids and asks
        bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'volume'])
        bids_df['side'] = 'buy'
        asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'volume'])
        asks_df['side'] = 'sell'

        # Combine and convert types
        combined_df = pd.concat([bids_df, asks_df])
        combined_df[['price', 'volume']] = combined_df[['price', 'volume']].apply(pd.to_numeric)

        return combined_df

    def get_order_output_quantity(self, order):
        """
        Processes the Binance order response (either buy or sell) and returns the executed quantity.
        If the order was not successful or an error occurred, returns -1.
        """
        try:
            # Assuming 'order' is a dictionary containing the response from Binance
            if order and 'executedQty' in order:
                executed_quantity = float(order['executedQty'])
                return executed_quantity
            else:
                # Order response doesn't have the expected field
                return -1
        except Exception as e:
            print(f"Error processing order response: {e}")
            return -1


