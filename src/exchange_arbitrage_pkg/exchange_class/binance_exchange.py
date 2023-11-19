from binance import AsyncClient
from binance.client import Client
import pandas as pd

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass


class BinanceExchange(ExchangeAbstractClass):
    def __init__(self, api_auth_obj: APIAuthClass):
        super().__init__(ExchangeNames.Binance, api_auth_obj)
        self.client = Client(api_key=self.api_auth_obj.api_key,
                             api_secret=self.api_auth_obj.secret_key,
                             tld="us",
                             testnet=self.api_auth_obj.is_testnet,
                             requests_params={'timeout': 20})
        self.vol_col_key = "binance_volume_col"

    def create_async_client(self):
        return AsyncClient.create(api_key=self.api_auth_obj.api_key,
                                  api_secret=self.api_auth_obj.secret_key,
                                  testnet=self.api_auth_obj.is_testnet,
                                  tld="us",
                                  requests_params={'timeout': 20})

    def get_order_book(self, symbol, limit=100):
        order_book = self.client.get_order_book(symbol=symbol, limit=limit)

        # Adding 'side' column and combining bids and asks
        bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'volume'])
        bids_df['side'] = 'buy'
        asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'volume'])
        asks_df['side'] = 'sell'

        # Combine and convert types
        combined_df = pd.concat([bids_df, asks_df])
        combined_df[['price', 'volume']] = combined_df[['price', 'volume']].apply(pd.to_numeric)

        return combined_df

    def get_order_book_bids_and_ask_df(self, symbol, limit=100):
        # Fetch order book from Binance
        order_book = self.client.get_order_book(symbol=symbol, limit=limit)

        # Create DataFrames for bids and asks
        bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'quantity'])
        asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'quantity'])

        # Convert price and quantity to numeric types
        bids_df[['price', 'quantity']] = bids_df[['price', 'quantity']].apply(pd.to_numeric)
        asks_df[['price', 'quantity']] = asks_df[['price', 'quantity']].apply(pd.to_numeric)

        return bids_df, asks_df

    def get_order_book_and_volume_sync(self, symbol, depth=100):
        """
        Fetches the order book and trading volume for a given symbol.

        :param symbol: The trading symbol (e.g., 'BTCUSDT').
        :param depth: Depth of the order book to fetch.
        :return: A dictionary with order book and volume data.
        """
        # Fetch order book
        order_book = self.client.get_order_book(symbol=symbol, limit=depth)

        # Fetch ticker for volume information
        ticker = self.client.get_ticker(symbol=symbol)

        return {
            'order_book': order_book,
            '24h_volume': ticker['volume']
        }

