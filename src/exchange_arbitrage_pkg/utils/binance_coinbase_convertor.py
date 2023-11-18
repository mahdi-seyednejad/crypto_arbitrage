def binance_to_coinbase(binance_symbol):
    """
    Convert a Binance symbol pair to Coinbase format.
    Binance format example: 'BTCUSDT'
    Coinbase format example: 'BTC-USD'
    """
    # Coinbase uses '-' to separate the base and the quote, and 'USD' instead of 'USDT'
    return binance_symbol.replace('USDT', '-USD')


def coinbase_to_binance(coinbase_symbol):
    """
    Convert a Coinbase symbol pair to Binance format.
    Coinbase format example: 'BTC-USD'
    Binance format example: 'BTCUSDT'
    """
    # Binance uses 'USDT' to represent Tether pairs instead of 'USD' and no separator
    return coinbase_symbol.replace('-USD', 'USDT')


def extract_symbol(row):
    return row['symbol'].values[0]
