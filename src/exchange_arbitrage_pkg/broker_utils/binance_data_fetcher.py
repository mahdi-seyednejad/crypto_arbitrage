import pandas as pd

from src.exchange_arbitrage_pkg.utils.calculation_utils import calculate_percentage_difference_2_values


def get_usa_symbols(self):
    info = self.sync_client.get_exchange_info()
    pairs_data = info['symbols']
    full_data_dict = {s['symbol']: s for s in pairs_data if 'USDT' in s['symbol']}
    return full_data_dict


def filter_invalid_symbols(tickers):
    filtered_prices = {}
    for ticker in tickers:
        symbol = ticker['symbol']
        if "US" in symbol and not any(char.isdigit() for char in symbol):
            filtered_prices[symbol] = float(ticker['lastPrice'])

    return filtered_prices


def add_exchange_info(df_in, client):
    exchange_info = client.get_exchange_info()
    exchange_df = pd.DataFrame(exchange_info['symbols'])  # Adjust according to the structure of exchange_info
    combined_df = pd.merge(df_in, exchange_df, on="symbol", how="inner")
    return combined_df


def calculate_percentage_diff_bi_cb(row):
    return calculate_percentage_difference_2_values(row['binance_price'], row['coinbase_price'])


def update_data_df(original_df_in, new_df):
    if original_df_in is None or new_df is None:
        return new_df
    if len(original_df_in) == 0:
        return new_df

    # Keep only rows in original_df where the symbol is in new_df
    original_df = original_df_in[original_df_in['symbol'].isin(new_df['symbol'])].copy()

    # Decrease recency by one, ensuring it does not go below zero
    # original_df['recency'] = original_df['recency'].apply(lambda x: x - 1)
    original_df.loc[:, 'recency'] = original_df['recency'].apply(lambda x: x - 1)

    # Find new symbols in new_df not in original_df
    new_symbols = new_df[~new_df['symbol'].isin(original_df['symbol'])]

    # Concatenate new symbols to original_df
    original_df = pd.concat([original_df, new_symbols], ignore_index=True)

    # Update values from new_df, except for 'recency'
    # Create a temporary DataFrame with columns excluding 'recency'
    temp_new_df = new_df.drop(columns='recency', errors='ignore')
    original_df.update(temp_new_df)

    return original_df


async def get_last_24_hour_price(client):
    # Use the get_ticker method to get 24-hour price change
    tickers = await client.get_ticker()

    # Convert the tickers to a Pandas DataFrame
    df = pd.DataFrame(tickers)

    # Filter down to only USDT pairs
    df = df[df['symbol'].str.endswith('USDT')]

    # The get_ticker method should already include a field for 24-hour price change percentage
    df['price_change_24h'] = df['priceChangePercent'].astype(float)

    return df



