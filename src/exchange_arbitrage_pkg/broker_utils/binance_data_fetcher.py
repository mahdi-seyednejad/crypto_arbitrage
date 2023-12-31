import pandas as pd

from src.exchange_arbitrage_pkg.utils.calculation_utils import calc_absolute_percentage_diff_2_values


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


def calculate_percentage_diff_bi_cb(row, first_ex_price_col, second_ex_price_col):
    return calc_absolute_percentage_diff_2_values(row[first_ex_price_col],
                                                  row[second_ex_price_col])


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



