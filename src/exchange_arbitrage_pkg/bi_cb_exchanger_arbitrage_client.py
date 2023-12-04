import asyncio
import time
from datetime import datetime
from typing import List

import pandas as pd

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeys, CoinbaseProAPIKeys
from src.exchange_arbitrage_pkg.broker_utils.binance_data_fetcher import update_data_df
from src.exchange_arbitrage_pkg.broker_utils.coinbase_utils.coinbase_get_prices import get_latest_prices_coinbase_pro
from src.exchange_arbitrage_pkg.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_arbitrage_pkg.exchange_class.binance_exchange import BinanceExchange
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.information_extractor import calculate_diff_and_sort, info_extractor_by_df


class PriceDiffExtractor:
    def __init__(self,
                 binance_exchange_obj,
                 coinbase_exchange_obj,  # It can be either sync client, or a public one
                 column_obj,
                 experiment_sample_size=None,
                 debug=True):
        self.binance_exchange = binance_exchange_obj
        self.coinbase_exchange = coinbase_exchange_obj
        self.binance_client_async = None
        self.coinbase_client_sync = coinbase_exchange_obj.public_client
        self.data = None
        self.debug = debug
        self.sample_size = experiment_sample_size
        self.column_obj = column_obj
        self.data_collection: List[pd.DataFrame()] = []
        self.data: pd.DataFrame() = None
        self.accumulated_data: pd.DataFrame() = None  # Todo: Concatenate new dataframes

    async def get_latest_prices_binance(self):
        if not self.binance_client_async:
            self.binance_client_async = await self.binance_exchange.create_async_client()

        # Fetch the ticker prices
        tickers = await self.binance_client_async.get_ticker()

        # Convert the tickers to a Pandas DataFrame
        tickers_df = pd.DataFrame(tickers)

        # Filter symbols based on the specified criteria
        filtered_df = tickers_df[tickers_df['symbol'].str.contains("US") & ~tickers_df['symbol'].str.contains(r'\d')]

        # Rename the columns with the specified naming convention
        rename_dict = {col: (f'binance_{col}_24h' if col not in ['symbol', 'lastPrice'] else (
            'binance_price' if col == 'lastPrice' else col)) for col in filtered_df.columns}
        binance_df = filtered_df.rename(columns=rename_dict)

        return binance_df

    def _get_latest_prices_coinbase_pro(self):
        cb_price_df = get_latest_prices_coinbase_pro(self.coinbase_client_sync, self.sample_size)
        cb_price_df_not_nan = cb_price_df.dropna(subset=['price']).copy()
        cb_price_df_not_nan.rename(columns={'id': 'symbol', 'price': 'coinbase_price'}, inplace=True)
        return cb_price_df_not_nan

    async def get_data_from_exchanges(self):
        binance_prices = await self.get_latest_prices_binance()
        coinbase_prices = self._get_latest_prices_coinbase_pro()
        combined_df = info_extractor_by_df(binance_prices, coinbase_prices)
        combined_df['current_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Convert 'binance_price' and 'coinbase_price' to numeric values
        combined_df[self.binance_exchange.price_col] = pd.to_numeric(combined_df[self.binance_exchange.price_col], errors='coerce')
        combined_df[self.coinbase_exchange.price_col] = pd.to_numeric(combined_df[self.coinbase_exchange.price_col], errors='coerce')
        return combined_df

    def update_and_sort_data(self, new_df):
        new_data_df = update_data_df(original_df_in=self.data, new_df=new_df)
        new_data_df.sort_values(by=[self.column_obj.current_price_diff_percentage_col,
                                    'recency', self.column_obj.price_diff_col],
                                ascending=[False, False, False], inplace=True)
        return new_data_df

    async def create_differential_df(self):
        # Step 1- Get the data from both exchanges
        extracted_info = await self.get_data_from_exchanges()

        # Step 2- Calculate the difference, diff percentage, and sort the data
        combined_df = calculate_diff_and_sort(extracted_info_in=extracted_info,
                                              first_ex_price_col=self.binance_exchange.price_col,
                                              second_ex_price_col=self.coinbase_exchange.price_col,
                                              col_info_obj=self.column_obj)

        # step 3- Add the recency column
        combined_df['recency'] = 0

        # Step 4- Add the last 24 hours price change info
        # combined_df_w_24_h_info = await self.add_last_24_h_price_change_info(combined_df)
        combined_df_w_24_h_info = combined_df
        # ToDo: Exclude the ones with price = 0
        #ToDo: The volum is missing!

        # Step 5- Update the data
        self.data = self.update_and_sort_data(new_df=combined_df_w_24_h_info)

        if self.debug:
            print("\n")
            num_row_to_show = 10
            selected_cols = ['current_time', 'symbol', 'binance_price', 'coinbase_price', 'price_diff_bi_cb',
                             'current_price_diff_percentage', self.column_obj.bi_price_change_24h, 'recency']
            print("The extracted info is: ")
            print(combined_df_w_24_h_info[selected_cols].head(num_row_to_show).to_string())
            print("The updated data is: ")
            print(self.data[selected_cols].head(num_row_to_show).to_string())
            print("*" * 60)
        return self.data

    async def run(self, run_number=10, apply_function=None, storage_dir=None):
        #ToDo: Looping back starts in here.
        sleep_time = 2
        counter = 0
        # Run the arbitrage detection for a specified number of times
        if run_number is None:
            while True:
                result_df = await self.create_differential_df()
                if apply_function is not None:
                    await apply_function(result_df)
                if storage_dir is not None:
                    result_df.to_csv(f"{storage_dir}/data_{counter}.csv")
                    result_df.to_csv(f"results/data_{counter}.csv")
                time.sleep(sleep_time)
        else:
            for i in range(run_number):
                result_df = await self.create_differential_df()
                if apply_function is not None:
                    await apply_function(result_df)
                if storage_dir is not None:
                    result_df.to_csv(f"{storage_dir}/data_{counter}.csv")
                    # result_df.to_csv(f"results/data_{counter}.csv")
                time.sleep(sleep_time)
            counter += 1


def print_for_testing(df):
    print("\n")
    print("Apply function (Print for testing)... ")
    print(df.head(10).to_string())


if __name__ == '__main__':
    DEBUG = True
    sample_size = None # Just for testing
    run_number = 20

    col_obj = ColumnInfoClass()
    binance_exchange = BinanceExchange(BinanceAPIKeys())
    coinbase_exchange = AdvanceTradeExchange(CoinbaseProAPIKeys())

    arb_bot = PriceDiffExtractor(binance_exchange_obj=binance_exchange,
                                 coinbase_exchange_obj=coinbase_exchange,
                                 experiment_sample_size=sample_size,
                                 column_obj=col_obj,
                                 debug=DEBUG)
    asyncio.run(arb_bot.run(run_number=run_number,
                            apply_function=None, #print_for_testing
                            storage_dir=None))

