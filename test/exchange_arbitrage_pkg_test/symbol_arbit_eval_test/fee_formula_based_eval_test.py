import pytest
import pandas as pd

from src.exchange_arbitrage_pkg.symbol_arbitrage_eval_pkg.fee_formula_based_inclusion import calculate_symbol_profit_old
from src.exchange_arbitrage_pkg.utils.python_utils.data_structures import Stack
from test.exchange_arbitrage_pkg_test.symbol_arbit_eval_test.volume_computer import process_sell_side_order_book, \
    process_buy_side_order_book, compute_trade_volume_and_money, calculate_symbol_profit, calculate_profit

src_exchange_name = 'Exchange1'
dst_exchange_name = 'Exchange2'
price_col = 'price'
volume_col = 'volume'
side_col = 'side'
exchange_name_col = 'exchange_name'
symbol = 'BTC'
order_book_rows = [
    # src exchange:
    (86, 5, symbol, 'buy', src_exchange_name),
    (97, 1, symbol, 'buy', src_exchange_name),
    (100, 2, symbol, 'sell', src_exchange_name),
    (102, 5, symbol, 'sell', src_exchange_name),
    (110, 6, symbol, 'sell', src_exchange_name),
    # dst exchange:
    (101, 5, symbol, 'buy', dst_exchange_name),
    (104, 2.5, symbol, 'buy', dst_exchange_name),
    (106, 1, symbol, 'buy', dst_exchange_name),
    (111, 0.5, symbol, 'sell', dst_exchange_name),
    (125, 2, symbol, 'sell', dst_exchange_name)
]

order_book_df = pd.DataFrame(order_book_rows,
                             columns=[price_col, volume_col, 'symbol',
                                      side_col, exchange_name_col])

withdrawal_fee = 0.1  # Sample withdrawal fee

src_order_book_df = order_book_df[order_book_df[exchange_name_col] == src_exchange_name]
src_sell_order_book_df = src_order_book_df[src_order_book_df[side_col] == 'sell']

dst_order_book_df = order_book_df[order_book_df[exchange_name_col] == dst_exchange_name]
dst_buy_order_book_df = dst_order_book_df[dst_order_book_df[side_col] == 'buy']


def test_evaluate_arbitrage_opportunity():
    result = calculate_symbol_profit_old(order_book_df=order_book_df,
                                         withdrawal_fee=withdrawal_fee,
                                         src_exchange_name=src_exchange_name,
                                         dst_exchange_name=dst_exchange_name,
                                         transaction_fee_rate=0.001,
                                         price_col=price_col,
                                         volume_col=volume_col,
                                         side_col=side_col,
                                         exchange_name_col=exchange_name_col)
    print(result)


def test_process_sell_side_order_book():
    sell_stack = process_sell_side_order_book(src_sell_order_book_df, price_col, volume_col)
    assert isinstance(sell_stack, Stack)
    assert sell_stack.size() == len(src_sell_order_book_df)
    assert sell_stack.pop()['price'] == src_sell_order_book_df[price_col].min()  # Smallest price pops first


def test_process_dst_buy_side_order_book():
    buy_stack = process_buy_side_order_book(dst_buy_order_book_df, price_col, volume_col)
    assert isinstance(buy_stack, Stack)
    assert buy_stack.size() == len(dst_buy_order_book_df)
    assert buy_stack.pop()['price'] == dst_buy_order_book_df[price_col].max()  # Smallest price pops first


def test_compute_trade_volume_and_money():
    result = compute_trade_volume_and_money(src_sell_order_book_df,
                                            dst_buy_order_book_df,
                                            price_col=price_col,
                                            volume_col=volume_col,
                                            withdrawal_fee_amount=10)
    print(result)
    assert (3.5, 353.0, 366.0) == result[:3]


def test_calculate_profit():
    profit_col = 'profit',
    spent_money_col = 'spent_money',
    sold_money_col = 'sold_money',
    trading_volume_col = 'trading_volume'
    transaction_fee_rate = 0.001
    result = calculate_symbol_profit(order_book_df,
                                     withdrawal_fee,
                                     src_exchange_name,
                                     dst_exchange_name,
                                     src_transaction_fee_rate=transaction_fee_rate,
                                     dst_transaction_fee_rate=transaction_fee_rate,
                                     price_col=price_col,
                                     volume_col=volume_col,
                                     side_col=side_col,
                                     exchange_name_col=exchange_name_col,
                                     profit_col=profit_col,
                                     spent_money_col=spent_money_col,
                                     sold_money_col=sold_money_col,
                                     trading_volume_col=trading_volume_col)
    cum_traded_volume, spent_money, sold_money = (
        3.5, 353.0, 366.0)  # Actual values coming from compute_trade_volume_and_money
    direct_results = calculate_profit(spent_money,
                                      sold_money,
                                      cum_traded_volume,
                                      withdrawal_fee,
                                      transaction_fee_rate)
    assert result[profit_col] == direct_results[0]
    assert result[spent_money_col] == direct_results[1]
    assert result[sold_money_col] == direct_results[2]
