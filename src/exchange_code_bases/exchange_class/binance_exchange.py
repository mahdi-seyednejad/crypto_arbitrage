import asyncio

import pandas as pd

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_symbol_utils import get_base_currency_binance
from src.exchange_code_bases.binance_enhanced.binance_client_utils.get_latest_prices import binance_ticker_to_df
from src.exchange_code_bases.exchange_class.base_exchange_class import ExchangeAbstractClass
from src.exchange_code_bases.abstract_classes.crypto_clients import CryptoClient
from src.exchange_code_bases.binance_enhanced.binance_clients.binance_async_client import BinanceAsyncClient
from src.exchange_code_bases.binance_enhanced.binance_clients.binance_sync_client import BinanceSyncClient


class BinanceExchange(ExchangeAbstractClass):
    def __init__(self, api_auth_obj: APIAuthClass):
        super().__init__(ExchangeNames.Binance, api_auth_obj)
        self.sync_client = BinanceSyncClient(api_auth_obj=self.api_auth_obj)
        self.async_client = None
        self.async_obj = None
        self.vol_col = "binance_volume_col"
        self.budget = None
        self.price_col = 'binance_price'
        self.transaction_fee_rate = 0.001
        self.quote_volume_col = "binance_quoteVolume_24h"

    async def create_async_client(self):
        self.async_obj = BinanceAsyncClient(api_auth_obj=self.api_auth_obj)
        self.async_client = await self.async_obj.create_client()
        return self.async_client

    async def get_async_client(self):
        if self.async_client is None:
            self.async_client = await self.create_async_client()
        return self.async_client

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

    def get_order_output_quantity(self, order, current_price):
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

    def get_current_price(self, symbol):
        return self.sync_client.client.get_symbol_ticker(symbol=symbol)

    async def wait_til_receive_Async(self,
                                     symbol,
                                     expected_amount,
                                     check_interval,
                                     timeout,
                                     amount_loss,
                                     second_chance,
                                     debug
                                     ):
        base_symbol = get_base_currency_binance(symbol)
        for i in range(2):
            result = await self.async_obj \
                .wait_for_deposit_confirmation_binance(symbol=base_symbol,
                                                       expected_amount=expected_amount,
                                                       check_interval=check_interval,
                                                       timeout=timeout,
                                                       amount_loss=amount_loss,
                                                       debug=debug)
            if result:
                return result
            else:
                if second_chance:
                    if debug:
                        print(f"Second chance for {symbol} on Binance")
                        print("Waiting ....")
                    await asyncio.sleep(timeout / 2)
                else:
                    break
        return False

    def get_available_amount_sync(self, currency):
        return self.sync_client.fetch_budget(currency)

    async def get_available_amount_async(self, currency):
        return await self.async_obj.sync_client.fetch_budget(currency)

    def get_latest_prices_sync(self, sample_size=None):
        tickers = self.sync_client.client.get_ticker()
        return binance_ticker_to_df(tickers=tickers,
                                    name=self.name.value,
                                    output_price_col=self.price_col)

    async def get_latest_prices_async(self, sample_size=None):
        if not self.async_client:
            self.async_client = await self.create_async_client()
        tickers = await self.async_client.get_ticker()
        return binance_ticker_to_df(tickers=tickers,
                                    name=self.name.value,
                                    output_price_col=self.price_col)

    def filter_diff_df(self, diff_df):
        df = diff_df.copy()
        df = df[df[self.price_col] != 0]
        df = df[df[self.quote_volume_col].astype(float) > 0]
        return df
