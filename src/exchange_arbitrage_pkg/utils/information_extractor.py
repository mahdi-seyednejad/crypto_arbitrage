import pandas as pd


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
    #Todo: Remove the dash from the symbol
    coinbase_df['symbol'] = coinbase_df['symbol'].str.replace('-', '')
    coinbase_df['symbol'] = coinbase_df['symbol'].str.replace('USD', 'USDT')
    combined_df = pd.merge(binance_df_in, coinbase_df, on='symbol', how='inner')
    return combined_df


