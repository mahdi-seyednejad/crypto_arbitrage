import pytest
from unittest.mock import Mock
import pandas as pd

from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.symbol_evaluator import SymbolEvaluatorArbitrage


@pytest.fixture
def setup_data():
    # Mock DataFrame
    data = {'symbol': ['BTCUSD', 'ETHUSD'], 'other_col': [1, 2]}
    df_in = pd.DataFrame(data)

    # Mock Exchange and its methods
    exchange = Mock()
    exchange.name = 'MockExchange'
    exchange.order_book_fetcher = Mock(return_value=pd.DataFrame({'price': [10, 11], 'volume': [5, 3]}))

    # Mock other functions
    calculate_bid_ask_spread = Mock(return_value=1)
    calculate_liquidity = Mock(return_value=100)
    calculate_max_sell_quantity = Mock(return_value=8)
    calculate_max_buy_quantity = Mock(return_value=7)
    calculate_market_impact = Mock(return_value=0.5)

    return df_in, exchange

def test_extract_symbol_metrics(setup_data):
    df_in, exchange = setup_data
    instance = SymbolEvaluatorArbitrage()  # Replace with the actual class name

    # Assuming index and row to test are from the first row of df_in
    index, row = 0, df_in.iloc[0]

    # Call the function
    df_out, order_book_df_dict = instance.extract_symbol_metrics(
        df_in, index, row, exchange, {}
    )

    # Assertions to check if the function behaves as expected
    assert df_out is not None
    assert isinstance(df_out, pd.DataFrame)
    assert f'MockExchange_{instance.bid_ask_spread_col}' in df_out.columns
    assert f'MockExchange_{instance.liquidity_col}' in df_out.columns
    assert f'MockExchange_{instance.max_sell_qty_col}' in df_out.columns
    assert f'MockExchange_{instance.max_buy_qty_col}' in df_out.columns
    assert f'MockExchange_{instance.market_impact_max_sell_col}' in df_out.columns
    assert 'MockExchange_BTCUSD' in order_book_df_dict
