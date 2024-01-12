import asyncio
import time
from datetime import datetime
from typing import List, Optional
import pandas as pd

from src.data_pkg.ts_db.table_names_ds import TableNames
from src.data_pkg.ts_db.ts_db_handler import DbHandler
from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, \
    BinanceAPIKeysHFT02
from src.exchange_arbitrage_pkg.diff_df_maker_pkg.diff_df_maker_utils import update_data_df
# from src.exchange_code_bases.advance_trade.coinbase_utils.coinbase_get_prices import get_latest_prices_coinbase_at
from src.exchange_arbitrage_pkg.utils.python_utils.df_utils import convert_column_types, convert_column_types_and_case
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.information_extractor import calculate_diff_and_sort, info_extractor_by_df
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_code_bases.exchange_class.exchange_pair_class import ExchangePair


class PriceDiffExtractor:
    def __init__(self,
                 exchange_pair: ExchangePair,
                 col_info: ColumnInfoClass,
                 diff_db_handler: DbHandler,
                 experiment_sample_size: Optional[int] = None,
                 debug=True):
        self.first_exchange = exchange_pair.get_first_exchange()
        self.second_exchange = exchange_pair.get_second_exchange()
        self.binance_client_async = None
        self.coinbase_client_sync = exchange_pair.get_second_client_for_diff_df()
        self.data = None
        self.debug = debug
        self.sample_size = experiment_sample_size
        self.col_info = col_info
        self.data_collection: List[pd.DataFrame()] = []
        self.data: pd.DataFrame() = None
        self.accumulated_data: pd.DataFrame() = None  # Todo: Concatenate new dataframes
        self.db_handler = diff_db_handler

    async def get_latest_prices_first_ex(self):  # ToDO: move this to Exchange object
        latest_price_df = await self.first_exchange.get_latest_prices_async(self.sample_size)
        return latest_price_df

    # async def get_latest_prices_first_ex(self):  # ToDO: move this to Exchange object
    #     if not self.binance_client_async:
    #         self.binance_client_async = await self.first_exchange.create_async_client()
    #
    #     # Fetch the ticker prices
    #     tickers = await self.binance_client_async.get_ticker()
    #
    #     # Convert the tickers to a Pandas DataFrame
    #     tickers_df = pd.DataFrame(tickers)
    #
    #     # Filter symbols based on the specified criteria
    #     filtered_df = tickers_df[tickers_df['symbol'].str.contains("US") & ~tickers_df['symbol'].str.contains(r'\d')]
    #
    #     # Rename the columns with the specified naming convention
    #     rename_dict = {
    #         col: (f'{self.first_exchange.name.value}_{col}_24h' if col not in ['symbol', 'lastPrice'] else (
    #             self.first_exchange.price_col if col == 'lastPrice' else col)) for col in filtered_df.columns}
    #     binance_df = filtered_df.rename(columns=rename_dict)
    #
    #     return binance_df

    def _get_latest_prices_second_ex(self):
        return self.second_exchange.get_latest_prices_sync(self.sample_size)

    # def _get_latest_prices_second_ex(self):  # ToDO: move this to Exchange object
    #     cb_price_df = get_latest_prices_coinbase_at(self.coinbase_client_sync, self.sample_size)
    #     cb_price_df_not_nan = cb_price_df.dropna(subset=['price']).copy()
    #     cb_price_df_not_nan.rename(columns={'id': 'symbol', 'price': self.second_exchange.price_col}, inplace=True)
    #     return cb_price_df_not_nan

    async def get_data_from_exchanges(self):
        binance_prices = await self.get_latest_prices_first_ex()
        coinbase_prices = self._get_latest_prices_second_ex()
        combined_df = info_extractor_by_df(binance_prices, coinbase_prices)
        combined_df[self.col_info.current_time_col] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        combined_df[self.first_exchange.price_col] = pd.to_numeric(combined_df[self.first_exchange.price_col],
                                                                   errors='coerce')
        combined_df[self.second_exchange.price_col] = pd.to_numeric(combined_df[self.second_exchange.price_col],
                                                                    errors='coerce')
        return combined_df

    def update_and_sort_data(self, new_df):
        new_data_df = update_data_df(original_df_in=self.data, new_df=new_df)
        new_data_df.sort_values(by=[self.col_info.current_price_diff_percentage_col,
                                    self.col_info.recency_col, self.col_info.price_diff_col],
                                ascending=[False, False, False], inplace=True)
        return new_data_df

    def print_debug(self, new_data_df):
        if self.debug:
            print("\n")
            num_row_to_show = 10
            selected_cols = [self.col_info.current_time_col, self.col_info.symbol_col,
                             self.first_exchange.price_col, self.second_exchange.price_col,
                             self.col_info.price_diff_col, self.col_info.current_price_diff_percentage_col,
                             self.col_info.bi_price_change_24h, self.col_info.recency_col]
            print("The extracted info is: ")
            print(new_data_df[selected_cols].head(num_row_to_show).to_string())
            print("The updated data is: ")
            print(self.data[selected_cols].head(num_row_to_show).to_string())
            print("*" * 60)

    def get_src_exchange_name(self, row):
        if row[self.col_info.price_diff_col] > 0:
            return self.second_exchange.name.value
        else:
            return self.first_exchange.name.value

    def get_dst_exchange_name(self, row):
        if row[self.col_info.price_diff_col] > 0:
            return self.first_exchange.name.value
        else:
            return self.second_exchange.name.value

    def _put_src_dst_exchange_names(self, df_in):
        df = df_in.copy()
        df[self.col_info.src_exchange_name_col] = df.apply(self.get_src_exchange_name, axis=1)
        df[self.col_info.dst_exchange_name_col] = df.apply(self.get_dst_exchange_name, axis=1)
        return df

    def _filter_unwanted_symbols(self, df_in):
        df = df_in.copy()
        df = df[df[self.col_info.price_diff_col] != 0]
        df = df[df[self.first_exchange.price_col] > 0]
        df = df[df[self.second_exchange.price_col] > 0]
        return df

    async def create_differential_df(self):
        # Step 1- Get the data from both exchanges
        extracted_info = await self.get_data_from_exchanges()

        # Step 2- Calculate the difference, diff percentage, and sort the data
        combined_df = calculate_diff_and_sort(extracted_info_in=extracted_info,
                                              first_ex_price_col=self.first_exchange.price_col,
                                              second_ex_price_col=self.second_exchange.price_col,
                                              col_info_obj=self.col_info)

        # step 3- Add the recency column
        combined_df[self.col_info.recency_col] = 0

        # Step 4- Add the last 24 hours price change info
        combined_df_w_24_h_info = combined_df
        filtered_df = self._filter_unwanted_symbols(combined_df_w_24_h_info)
        # new_data_df = convert_column_types(filtered_df)
        new_data_df = convert_column_types_and_case(filtered_df)
        new_data_w_src_dst = self._put_src_dst_exchange_names(new_data_df)

        if self.db_handler is not None:
            self.db_handler.insert_stream_diff_data_df(new_data_w_src_dst)

        # Step 5- Update the data
        self.data = self.update_and_sort_data(new_df=new_data_w_src_dst)
        self.print_debug(new_data_w_src_dst)
        return self.data

    async def obtain_and_process_diff_df(self, counter, sleep_time, storage_dir=None, apply_function=None):
        try:
            result_df = await self.create_differential_df()
            if apply_function is not None:
                await apply_function(result_df)
            if storage_dir is not None:
                result_df.to_csv(f"{storage_dir}/data_{counter}.csv")
            time.sleep(sleep_time)
            return result_df
        except Exception as e:
            print(e)
            time.sleep(sleep_time)

    async def run(self, run_number=10, apply_function=None, storage_dir=None):
        # ToDo: Looping back starts in here.
        sleep_time = 2
        counter = 0
        while True:
            result_df = await self.obtain_and_process_diff_df(counter=counter,
                                                              sleep_time=sleep_time,
                                                              storage_dir=storage_dir,
                                                              apply_function=apply_function)
            counter += 1
            if run_number is not None:
                if counter >= run_number:
                    break


def print_for_testing(df):
    print("\n")
    print("Apply function (Print for testing)... ")
    print(df.head(10).to_string())


if __name__ == '__main__':
    DEBUG = True
    sample_size = None  # Just for testing
    run_number = 4

    col_obj = ColumnInfoClass()
    binance_exchange = BinanceExchange(BinanceAPIKeysHFT02())
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())

    db_handler = DbHandler(
        time_column=col_obj.current_time_col,
        date_as_index=False,
        table_names=TableNames(),
        debug=True)

    example_exchange_pair = ExchangePair(first_exchange=binance_exchange,
                                         second_exchange=coinbase_exchange)

    arb_bot = PriceDiffExtractor(exchange_pair=example_exchange_pair,
                                 experiment_sample_size=sample_size,
                                 col_info=col_obj,
                                 diff_db_handler=db_handler,
                                 debug=DEBUG)

    asyncio.run(arb_bot.run(run_number=run_number,
                            apply_function=None,  # print_for_testing
                            storage_dir='sample_results'))
