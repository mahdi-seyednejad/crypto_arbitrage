import pandas as pd

from src.exchange_arbitrage_pkg.broker_utils.binance_data_fetcher import calculate_percentage_diff_bi_cb


def info_extractor_by_df(binance_df_in, coinbase_df_in):
    coinbase_df = coinbase_df_in.copy()
    coinbase_df['symbol'] = coinbase_df['symbol'].str.replace('-', '')
    coinbase_df['symbol'] = coinbase_df['symbol'].str.replace('USD', 'USDT') # Use "exchange.main_quote" instead
    combined_df = pd.merge(binance_df_in, coinbase_df, on='symbol', how='inner')
    return combined_df


def calculate_diff_and_sort(extracted_info_in,
                            first_ex_price_col,
                            second_ex_price_col,
                            col_info_obj):
    extracted_info = extracted_info_in.copy()
    extracted_info[col_info_obj.price_diff_col] = extracted_info[first_ex_price_col] - extracted_info[second_ex_price_col]
    extracted_info[col_info_obj.current_price_diff_percentage_col] = extracted_info\
        .apply(lambda row: calculate_percentage_diff_bi_cb(row,
                                                           first_ex_price_col,
                                                           second_ex_price_col), axis=1)
    result_df = extracted_info[extracted_info[col_info_obj.current_price_diff_percentage_col] != 0].copy()
    result_df.sort_values(by=[col_info_obj.current_price_diff_percentage_col], ascending=[False], inplace=True)
    return result_df
