import pandas as pd
import numpy as np
import pytest

from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.information_extractor import calculate_diff_and_sort



# Fixture for test data
@pytest.fixture
def sample_data():
    data = {
        'binance_price': [100, 150, 200, 400],
        'coinbase_price': [95, 155, 195, 400]
    }
    return pd.DataFrame(data)

# Test for calculating differences and sorting

def test_calculate_diff_and_sort(sample_data):
    col_info = ColumnInfoClass()
    result_df = calculate_diff_and_sort(sample_data,
                                        'binance_price',
                                        'coinbase_price',
                                        col_info)

    # Check if the function returns a DataFrame
    assert isinstance(result_df, pd.DataFrame), "Result should be a DataFrame"


    expected_data = {
        'binance_price': [100, 150, 200],
        'coinbase_price': [95, 155, 195],
        'price_diff_bi_cb': [5, -5,  5],
        col_info.current_price_diff_percentage_col: [(5 / 95) * 100, (abs(-5) / 150) * 100, (5 / 195) * 100] # [5.263, 3.333, 2.564],
    }
    expected_df = pd.DataFrame(expected_data)

    # Check if the price difference is calculated correctly
    assert all(result_df['price_diff_bi_cb'] == expected_data['price_diff_bi_cb']), "Price difference calculation error"

    # Check if the DataFrame is sorted correctly
    assert result_df.iloc[0]['price_diff_bi_cb'] >= result_df.iloc[-1]['price_diff_bi_cb'], "DataFrame is not sorted correctly"

    # Check percentage difference calculation (assuming the implementation)
    assert np.allclose(result_df['current_price_diff_percentage'],
                       expected_df['current_price_diff_percentage'],
                       atol=1e-2), "Percentage difference column values differ"


# Additional tests can be added to cover edge cases, such as zero prices, etc.
