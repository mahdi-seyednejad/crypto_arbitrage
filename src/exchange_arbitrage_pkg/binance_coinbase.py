import asyncio
import time
from datetime import datetime
from typing import List

import cbpro
import pandas as pd
from binance import AsyncClient

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeys, CoinbaseAPIKeys
from src.exchange_arbitrage_pkg.broker_utils.binance_data_fetcher import filter_invalid_symbols, update_data_df, \
    get_last_24_hour_price
from src.exchange_arbitrage_pkg.broker_utils.coinbase_utils.coinbase_get_prices import get_latest_prices_coinbase_pro
from src.exchange_arbitrage_pkg.utils.information_extractor import info_extractor_by_df, calculate_diff_and_sort


class CryptoExchangeArbitrage:
    def __init__(self,
                 binance_api_key_input,
                 binance_api_secret_input,
                 coinbase_pro_api_key_input,
                 coinbase_pro_api_secret_input,
                 sample_size=None,
                 debug=True):
        self.binance_api_key = binance_api_key_input
        self.binance_api_secret = binance_api_secret_input
        self.coinbase_pro_api_key = coinbase_pro_api_key_input
        self.coinbase_pro_api_secret = coinbase_pro_api_secret_input
        self.binance_client = None  # Will be initialized in an async context
        self.coinbase_pro_base_url = "https://api.pro.coinbase.com"
        self.data_collection: List[pd.DataFrame()] = []
        self.data: pd.DataFrame() = None
        self.accumulated_data: pd.DataFrame() = None # Todo: Concatenate new dataframes

        self.sample_size = sample_size
        self.debug = debug

    async def get_latest_prices_binance(self):
        # Initialize the client if it hasn't been already
        if not self.binance_client:
            self.binance_client = await AsyncClient.create(self.binance_api_key,
                                                           self.binance_api_secret,
                                                           tld='us',
                                                           testnet=False)

        # Fetch the ticker prices
        tickers = await self.binance_client.get_ticker()
        filtered_tickers = filter_invalid_symbols(tickers)

        tickers_series = pd.Series(filtered_tickers)
        binance_df = tickers_series.reset_index()
        binance_df.columns = ['symbol', 'binance_price']

        return binance_df

    def _get_latest_prices_coinbase_pro(self):
        cb_price_df = get_latest_prices_coinbase_pro(cbpro.PublicClient(), self.sample_size)
        cb_price_df_not_nan = cb_price_df.dropna(subset=['price']).copy()
        cb_price_df_not_nan.rename(columns={'id': 'symbol', 'price': 'coinbase_price'}, inplace=True)
        return cb_price_df_not_nan


    async def get_24h_price_change_binance(self, symbol):
        # Fetch 24-hour price change for a symbol from Binance
        change = await self.binance_client.get_ticker(symbol=symbol)
        return change['priceChangePercent']

    # def rank_opportunities(self, df):
    #     # Rank based on recency, value difference percentage, and 24-hour price change percentage
    #     df.sort_values(by=['last_occurrence', 'value_difference_percentage', '24h_price_change'],
    #                    ascending=[True, False, False], inplace=True)

    # def detect_arbitrage_opportunities(self, top_n=10):
    #     # Return the top N opportunities
    #     return self.data.head(top_n)
    #
    # def arbitrage_opportunity_detector(self, top_n=10):
    #     # This function can call `detect_arbitrage_opportunities` method to get the top N opportunities
    #     # and then execute trades based on those opportunities.
    #     opportunities = self.detect_arbitrage_opportunities(top_n)
    #     for index, opportunity in opportunities.iterrows():
    #         asyncio.run(self.execute_trade(
    #             symbol=opportunity['symbol'],
    #             buy_exchange=opportunity['lower_exchange'],
    #             sell_exchange=opportunity['higher_exchange'],
    #             amount=self.calculate_amount_to_trade(opportunity)
    #         ))

    def get_24h_price_change_coinbase_pro(self, symbol):
        # Fetch 24-hour price change for a symbol from Coinbase Pro
        # The Coinbase Pro API does not directly provide 24-hour change percentage,
        # so you would need to calculate this by fetching the 24-hour stats and comparing prices.
        public_client = cbpro.PublicClient()
        stats = public_client.get_product_24hr_stats(symbol)
        if stats and 'open' in stats and 'last' in stats:
            price_change = (float(stats['last']) - float(stats['open'])) / float(stats['open']) * 100
            return price_change
        else:
            return None

    def get_24h_price_change(self, symbols):
        # This function needs to be asynchronous to call the async Binance function
        # and synchronous Coinbase Pro function for each symbol.
        # For simplification, we'll assume the symbols list is already in the correct format for each exchange.
        loop = asyncio.get_event_loop()
        changes = {}
        for symbol in symbols:
            if 'USD' in symbol:
                changes[symbol] = self.get_24h_price_change_coinbase_pro(symbol)
            else:
                changes[symbol] = loop.run_until_complete(self.get_24h_price_change_binance(symbol))
        return changes

    # async def execute_trade(self, symbol, buy_exchange, sell_exchange, amount):
    #     # Execute trades on the respective exchanges.
    #     # This is a complex function as it requires placing orders and may involve transferring funds.
    #     # This is a placeholder for the real implementation which must handle authentication, order types, error checking etc.
    #     pass

    # def calculate_amount_to_trade(self, opportunity):
    #     # Calculate the amount to trade based on the opportunity details, your balance, and your risk management strategy.
    #     # Placeholder for the actual implementation
    #     pass

    def print_and_collect_df(self, df):
        # Print the DataFrame and save it to the collection
        print(df)
        self.data_collection.append(df)

    async def get_data_from_exchanges(self):
        binance_prices = await self.get_latest_prices_binance()
        coinbase_prices = self._get_latest_prices_coinbase_pro()
        combined_df = info_extractor_by_df(binance_prices, coinbase_prices)
        combined_df['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return combined_df

    async def add_last_24_h_price_change_info(self, combined_df):
        last_24_h_price_df = await get_last_24_hour_price(self.binance_client)
        return pd.merge(combined_df, last_24_h_price_df, on="symbol", how="inner")

    def update_and_sort_data(self, new_df):
        new_data_df = update_data_df(original_df_in=self.data, new_df=new_df)
        new_data_df.sort_values(by=['current_price_diff_percentage', 'recency', 'price_diff_bi_cb'],
                                ascending=[False, False, False], inplace=True)
        return new_data_df

    async def create_differential_df(self):
        # Step 1- Get the data from both exchanges
        extracted_info = await self.get_data_from_exchanges()

        # Step 2- Calculate the difference, diff percentage, and sort the data
        combined_df = calculate_diff_and_sort(extracted_info)

        # step 3- Add the recncy column
        combined_df['recency'] = 0

        # Step 4- Add the last 24 hours price change info
        combined_df_w_24_h_info = await self.add_last_24_h_price_change_info(combined_df)

        # Step 5- Update the data
        self.data = self.update_and_sort_data(new_df=combined_df_w_24_h_info)

        # ToDo: The update function must be checked. Why the data reduced? Why the new values are note updated? Do we drop data?
        if self.debug:
            print("\n")
            num_row_to_show = 10
            selected_cols = ['current_time', 'symbol', 'binance_price', 'coinbase_price', 'price_diff_bi_cb',
                             'current_price_diff_percentage', 'price_change_24h', 'recency']
            print("The extracted info is: ")
            print(combined_df_w_24_h_info[selected_cols].head(num_row_to_show).to_string())
            print("The updated data is: ")
            print(self.data[selected_cols].head(num_row_to_show).to_string())
            print("*" * 60)
        return self.data

    async def run(self, run_number=10, apply_function=None, storage_dir=None):
        sleep_time = 2
        counter = 0
        # Run the arbitrage detection for a specified number of times
        if run_number is None:
            while True:
                result_df = await self.create_differential_df()
                if apply_function is not None:
                    apply_function(result_df)
                if storage_dir is not None:
                    result_df.to_csv(f"{storage_dir}/data_{counter}.csv")
                    # result_df.to_csv(f"results/data_{counter}.csv")
                self.print_and_collect_df(self.data)
                time.sleep(sleep_time)
        else:
            for i in range(run_number):
                result_df = await self.create_differential_df()
                if apply_function is not None:
                    apply_function(result_df)
                if storage_dir is not None:
                    result_df.to_csv(f"{storage_dir}/data_{counter}.csv")
                    # result_df.to_csv(f"results/data_{counter}.csv")
                time.sleep(sleep_time)
            counter += 1


if __name__ == '__main__':
    # Run the bot
    # arb_bot.run()
    # To use the class and run the trading bot
    # ToDO: Just look into N symbol ols on top of the list
    DEBUG = True
    sample_size = None # Just for testing
    binance_api = BinanceAPIKeys()
    coinbase_api = CoinbaseAPIKeys()
    binance_api_key = binance_api.api_key_binance_read_only
    binance_api_secret = binance_api.secret_key_binance_read_only
    coinbase_pro_api_key = coinbase_api.api_key_coinbase
    coinbase_pro_api_secret = coinbase_api.secret_key_coinbase
    arb_bot = CryptoExchangeArbitrage(binance_api_key, binance_api_secret,
                                      coinbase_pro_api_key, coinbase_pro_api_secret,
                                      sample_size=sample_size,
                                      debug=DEBUG)
    asyncio.run(arb_bot.run(run_number=10))
