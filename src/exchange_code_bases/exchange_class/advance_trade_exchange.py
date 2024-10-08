import asyncio

import pandas as pd

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_symbol_utils import get_base_currency_bi_cb
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
        self.sync_client = CbAdvanceTradeClient(api_auth_obj)
        self.async_client = None
        self.async_obj = None
        self.price_col = 'adv_trade_price'
        self.vol_col = "adv_trade_volume_col"
        self.transaction_fee_rate = 0.001
        self.trading_disabled_col = 'trading_disabled'
        self.is_limit_only_col = 'limit_only'

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
        return float(self.sync_client.get_product_ticker(symbol)['price'])

    async def wait_til_receive_Async(self,
                                     symbol,
                                     expected_amount,
                                     check_interval,
                                     timeout_in,
                                     amount_loss,
                                     second_chance, #ToDo: Remove this.
                                     num_of_wait_tries,
                                     debug):
        base_symbol = get_base_currency_bi_cb(symbol)
        timeout = timeout_in
        for i in range(num_of_wait_tries):
            result = await self.async_client \
                .wait_for_deposit_confirmation(symbol=base_symbol,
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
                        print(f"Second chance for {symbol} on Coinbase advance trade")
                        print("Waiting ....")
                    if i % 2 == 0:
                        timeout /= 2
                    else:
                        timeout *= 2
                    await asyncio.sleep(timeout)
                else:
                    break
        return False
        #ToDO: use the transaction list to track the withdraw https://docs.cloud.coinbase.com/sign-in-with-coinbase/docs/api-transactions#list-transactions


    def get_latest_prices_sync(self, sample_size=None):
        return self.sync_client.get_prices_as_df(price_col=self.price_col,
                                                 limit=sample_size)

    async def get_latest_prices_async(self, sample_size=None):
        return await self.async_client.get_prices_as_df(price_col=self.price_col,
                                                        limit=sample_size)

    def filter_diff_df(self, diff_df):
        df = diff_df.copy()
        df = df[df[self.price_col] != 0]
        df = df[~df[self.trading_disabled_col].astype(bool)]
        return df
