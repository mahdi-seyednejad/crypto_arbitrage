import pandas as pd

from src.exchange_arbitrage_pkg.broker_utils.binance_data_fetcher import calculate_percentage_diff_bi_cb


def binance_coinbase_info_extractor(binance_data, coinbase_data):
    # Ensure coinbase_data is a DataFrame
    if not isinstance(coinbase_data, pd.DataFrame):
        raise ValueError("coinbase_data should be a pandas DataFrame")

    # Extract and combine the price data from Binance and Coinbase
    combined_data = []
    for symbol, binance_price in binance_data.items():
        # Coinbase symbols are in the format BASE-QUOTE (e.g., BTC-USD)
        coinbase_symbol = symbol.replace('USDT', 'USD')

        # Query the DataFrame for the Coinbase price
        coinbase_price = coinbase_data.loc[coinbase_data['id'] == coinbase_symbol, 'price'].squeeze()
        coinbase_price = coinbase_price.iloc[0] if not coinbase_price.empty else None

        # Check if there is a valid coinbase price
        if pd.notna(coinbase_price):
            combined_data.append({
                'symbol': symbol,
                'binance_price': binance_price,
                'coinbase_price': coinbase_price
            })

    return combined_data


def info_extractor_by_dict(binance_data, coinbase_data):
    # Extract and combine the price data from Binance and Coinbase
    combined_data = []
    for symbol, binance_price in binance_data.items():
        # Coinbase symbols are in the format BASE-QUOTE (e.g., BTC-USD)
        coinbase_symbol = symbol.replace('USDT', 'USD')
        coinbase_price = coinbase_data.get(coinbase_symbol)
        if coinbase_price:
            combined_data.append({
                'symbol': symbol,
                'binance_price': binance_price,
                'coinbase_price': coinbase_price
            })
    return combined_data


def info_extractor_by_df(binance_df_in, coinbase_df_in):
    coinbase_df = coinbase_df_in.copy()
    coinbase_df['symbol'] = coinbase_df['symbol'].str.replace('-', '')
    coinbase_df['symbol'] = coinbase_df['symbol'].str.replace('USD', 'USDT')
    combined_df = pd.merge(binance_df_in, coinbase_df, on='symbol', how='inner')
    return combined_df


def calculate_diff_and_sort(extracted_info_in):
    extracted_info = extracted_info_in.copy()
    extracted_info["price_diff_bi_cb"] = extracted_info["binance_price"] - extracted_info["coinbase_price"]
    extracted_info['current_price_diff_percentage'] = extracted_info.apply(calculate_percentage_diff_bi_cb, axis=1)
    result_df = extracted_info[extracted_info['current_price_diff_percentage'] != 0].copy()
    result_df.sort_values(by=['current_price_diff_percentage'], ascending=[False], inplace=True)
    return result_df

