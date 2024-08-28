import pandas as pd


def binance_ticker_to_df(tickers, name, output_price_col):
    # Convert the tickers to a Pandas DataFrame
    tickers_df = pd.DataFrame(tickers)

    # Filter symbols based on the specified criteria
    filtered_df = tickers_df[tickers_df['symbol'].str.contains("US") & ~tickers_df['symbol'].str.contains(r'\d')]

    # Rename the columns with the specified naming convention
    rename_dict = {
        col: (f'{name}_{col}_24h' if col not in ['symbol', 'lastPrice'] else (
            output_price_col if col == 'lastPrice' else col)) for col in filtered_df.columns}
    binance_df = filtered_df.rename(columns=rename_dict)
    return binance_df





