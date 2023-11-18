import pandas as pd
import pytest

from src.exchange_arbitrage_pkg.broker_utils.binance_data_fetcher import update_data_df


# Fixture for initial data
@pytest.fixture
def initial_data():
    data = {
        'symbol': ['BTCUSDT', 'ETHUSDT', 'XRPUSDT'],
        'price': [10000, 200, 0.25],
        'price_change_percent': [3.1, 2.1, 1.1],
        'recency': [0, 0, 0]
    }
    return pd.DataFrame(data)


# Test with initial new_df
def test_initial_data_update(initial_data):
    new_data = {
        'symbol': ['BTCUSDT', 'ETHUSDT', 'XRPUSDT'],
        'price': [10100, 210, 0.27],
        'price_change_percent': [3.0, 2.0, 1.0],
        'recency': [0, 0, 0]
    }
    new_df = pd.DataFrame(new_data)
    updated_df = update_data_df(original_df_in=None, new_df=new_df)
    assert new_df.shape == updated_df.shape, "DataFrames shape differ"
    assert all(new_data['symbol'] == updated_df['symbol']), "Column values differ"
    pd.testing.assert_frame_equal(updated_df, new_df, atol=1e-5)

    # Assertions to check if updated_df is same as new_df


# Test updating with overlapping symbols
def test_updating_overlapping_symbols(initial_data):
    new_data = {
        'symbol': ['ETHUSDT', 'BTCUSDT', 'JAMUSDT'],
        'price': [220, 10118, 0.22],
        'price_change_percent': [2.0, 1.3, 0.9],
        'recency': [0, 0, 0]
    }
    new_df = pd.DataFrame(new_data)
    updated_df = update_data_df(original_df_in=initial_data, new_df=new_df)
    updated_df.sort_values(by=['price_change_percent', 'recency'], ascending=[False, False], inplace=True)
    expected_data = {
        'symbol': ['ETHUSDT', 'BTCUSDT', 'JAMUSDT'],
        'price': [220, 10118, 0.22],
        'price_change_percent': [2.0, 1.3, 0.9],
        'recency': [-1, -1, 0]
    }
    expected_df = pd.DataFrame(expected_data)

    assert expected_df.shape == updated_df.shape, "DataFrames shape differ"
    assert all(expected_data['symbol'] == updated_df['symbol']), "Column values differ"
    pd.testing.assert_frame_equal(expected_df, updated_df, atol=1e-5)



    # Assertions to check proper update and recency handling

# Test recency update
def test_recency_update(initial_data):
    # You might need to call update_data_df multiple times to simulate multiple updates
    # Assertions to check if recency is updated correctly
    pass


# Test removal of rows if symbol not in new_df
def test_removal_of_rows(initial_data):
    new_data = {
        'symbol': ['BTCUSDT'],
        'price': [10300],
        'price_change_percent': [1.3],
        'recency': [0]
    }
    new_df = pd.DataFrame(new_data)
    updated_df = update_data_df(original_df_in=initial_data, new_df=new_df)
    # Assertions to check if non-present symbols are removed
    expected_data = {
        'symbol': ['BTCUSDT'],
        'price': [10300.0],
        'price_change_percent': [1.3],
        'recency': [-1]
    }
    expected_df = pd.DataFrame(expected_data)

    assert expected_df.shape == updated_df.shape, "DataFrames shape differ"
    assert all(expected_data['symbol'] == updated_df['symbol']), "Column values differ"
    pd.testing.assert_frame_equal(expected_df, updated_df, atol=1e-5)
