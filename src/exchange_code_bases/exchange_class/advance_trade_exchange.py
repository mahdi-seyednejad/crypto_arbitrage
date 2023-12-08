import cbpro
import pandas as pd

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.broker_utils.coinbase_utils.coinbase_symbol_utils import get_base_from_pair_coinbase
from src.exchange_code_bases.exchange_class.advance_trade_exchange_tools.order_parser import \
    get_order_output_quantity
from src.exchange_code_bases.exchange_class.base_exchange_class import ExchangeAbstractClass
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
        self.async_obj = None
        self.price_col = 'adv_trade_price'
        self.vol_col = "adv_trade_volume_col"

    async def create_async_client(self):
        self.async_obj = AsyncAdvanceTradeClient(api_auth_obj=self.api_auth_obj)
        self.async_client = await self.async_obj.create_async(self.api_auth_obj)
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

    def get_order_output_quantity(self, order, current_price):
        return get_order_output_quantity(order, current_price)

    def get_current_price(self, symbol):
        symbol = convert__symbol_bi_to_cb(symbol)
        return self.public_client.get_product_ticker(symbol)['price']

    async def get_coinbase_symbol_details(self, client, symbol):
        df = await client.fetch_account_info()
        if df is not None:
            buy_precision = df['base_increment']
            min_buy_amount = df['base_min_size']
            min_notional = df['min_market_funds']
            return buy_precision, min_buy_amount, min_notional
        return None, None, None

    async def wait_til_receive_Async(self,
                                     symbol,
                                     expected_amount,
                                     check_interval,
                                     timeout,
                                     amount_loss):
        if '-' in symbol:
            base_symbol = get_base_from_pair_coinbase(symbol)
        else:
            symbol_cb = convert__symbol_bi_to_cb(symbol)
            base_symbol = get_base_from_pair_coinbase(symbol_cb)
        return await self.async_client \
            .wait_for_deposit_confirmation(symbol=base_symbol,
                                           expected_amount=expected_amount,
                                           check_interval=check_interval,
                                           timeout=timeout,
                                           amount_loss=amount_loss)
