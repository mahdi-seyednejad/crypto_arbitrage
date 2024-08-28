import pandas as pd
import pytest

from src.exchange_arbitrage_pkg.utils.information_extractor import info_extractor_by_df


# Fixture for Binance sample data
@pytest.fixture
def binance_sample_data():
    data = {'symbol': ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'STGUSDT'],
            'binance_price': [10000, 200, 0.25, 100]}
    return pd.DataFrame(data)

# Fixture for Coinbase sample data
@pytest.fixture
def coinbase_sample_data():
    data = {'symbol': ['BTC-USD', 'ETH-USD', 'JAM-USD', 'STG-USDT'],
            'coinbase_price': [10005, 205, 0.56, 100]}
    return pd.DataFrame(data)


# Test for info_extractor_by_df
def test_info_extractor_by_df(binance_sample_data, coinbase_sample_data):
    result_df = info_extractor_by_df(binance_sample_data, coinbase_sample_data)

    # Check if the function returns a DataFrame
    assert isinstance(result_df, pd.DataFrame), "Result should be a DataFrame"

    # Check if the symbols were correctly transformed and merged
    expected_data = {
        'symbol': ['BTCUSDT', 'ETHUSDT'],
        'binance_price': [10000, 200],
        'coinbase_price': [10005, 205]
    }
    expected_df = pd.DataFrame(expected_data)

    assert result_df.equals(expected_df), "Merged DataFrame is not as expected"

# Additional tests can be added for edge cases, such as when one DataFrame is empty, symbols do not match, etc.
