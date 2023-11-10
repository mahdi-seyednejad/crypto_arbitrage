import pandas as pd


def get_usa_symbols(self):
    info = self.client.get_exchange_info()
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


def calculate_percentage_difference(row):
    smaller_price = min(row['coinbase_price'], row['binance_price'])
    price_difference = abs(row['coinbase_price'] - row['binance_price'])
    if smaller_price != 0:
        return (price_difference / smaller_price) * 100
    else:
        return None  # or 0, depending on how you want to handle division by zero


def update_data_df(original_df_in, new_df):
    if original_df_in is None or new_df is None:
        return new_df
    if len(original_df_in) == 0 or len(new_df) == 0:
        return new_df

    original_df = original_df_in.copy()
    original_df = original_df[original_df['symbol'].isin(new_df['symbol'])]

    # Update 'recency' by decreasing its value by one, but not less than zero
    # Check if 'recency' column exists
    if 'recency' in original_df.columns:
        # Update 'recency' by decreasing its value by one
        original_df['recency'] = original_df['recency'].apply(lambda x: x-1)
    else:
        # Create 'recency' column and set it to zero
        original_df['recency'] = 0

    # Update A with new values from B
    original_df.update(new_df)
    return original_df


# async def get_last_24_hour_price(client):
#     # tickers = client.get_all_tickers()
#     tickers = await client.get_all_tickers()
#
#
#     # Convert the tickers to a Pandas DataFrame
#     df = pd.DataFrame(tickers)
#
#     # Filter down to only USDT pairs
#     df = df[df['symbol'].str.endswith('USDT')]
#
#     # Calculate the price change percentage
#     df['price_change_24h'] = df['priceChangePercent'].astype(float)
#
#     return df

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



