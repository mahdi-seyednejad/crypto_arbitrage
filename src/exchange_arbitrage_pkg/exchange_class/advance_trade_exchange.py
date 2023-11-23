import cbpro
import pandas as pd

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass
from src.exchange_arbitrage_pkg.utils.binance_coinbase_convertor import convert__symbol_bi_to_cb
from src.exchange_code_bases.abstract_classes.crypto_clients import CryptoClient
from src.exchange_code_bases.advance_trade.cb_advance_trade_client.cbat_async import AsyncAdvanceTradeClient
from src.exchange_code_bases.advance_trade.cb_advance_trade_client.cbat_client import CbAdvanceTradeClient


class AdvanceTradeExchange(ExchangeAbstractClass):
    def __init__(self, api_auth_obj: APIAuthClass):
        super().__init__(ExchangeNames.Coinbase, api_auth_obj)
        self.vol_col_key = "coinbase_volume_col"
        self.budget = None
        self.public_client = cbpro.PublicClient()
        self.sync_client = CbAdvanceTradeClient(api_auth_obj)
        self.async_client = None

    def create_async_client(self):
        self.async_client = AsyncAdvanceTradeClient(api_auth_obj=self.api_auth_obj)
        return self.async_client

    def get_budget_sync(self, currency: str = 'USD'):
        return self.get_budget(self.sync_client, currency)

    def get_budget(self, client: CryptoClient, currency):
        return super().get_budget(self.sync_client, currency)

    def set_budget(self, client: CryptoClient, defined_budget=None, currency='USD'):
        super().set_budget(self.sync_client, defined_budget, currency)

    def get_order_book_sync(self, client, symbol, level=2):
        symbol = convert__symbol_bi_to_cb(symbol)
        order_book = client.fetch_order_book(product_id=symbol, level=level)

        # Adding 'side' column and combining bids and asks
        bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'volume', 'num_orders'])
        bids_df['side'] = 'buy'
        asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'volume', 'num_orders'])
        asks_df['side'] = 'sell'

        # Combine and convert types
        combined_df = pd.concat([bids_df, asks_df])
        combined_df[['price', 'volume']] = combined_df[['price', 'volume']].apply(pd.to_numeric)

        return combined_df

