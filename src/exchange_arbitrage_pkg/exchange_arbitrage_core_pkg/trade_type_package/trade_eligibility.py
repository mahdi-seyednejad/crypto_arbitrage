
def check_symbols_for_trade(df_in, goodness_col_output, price_diff_bi_cb, **kwargs):
    def apply_is_good_to_trade_basic(row):
        return True if row[price_diff_bi_cb] > 0 else False

    df = df_in.copy()
    df[goodness_col_output] = df.apply(apply_is_good_to_trade_basic, axis=1)

    return df


def evaluate_symbols_for_trade(df_in, order_book_fetcher, symbol_col, acceptable_slippage):
    '''
    We want to calculate max sell quantity,
    and other things to make decision either to trade a crypto or not.
    :param df_in:
    :type df_in:
    :param order_book_fetcher:
    :type order_book_fetcher:
    :param symbol_col:
    :type symbol_col:
    :return:
    :rtype:
    '''
    df = df_in.copy()
    df['order_book'] = df.apply(lambda row: order_book_fetcher(row[symbol_col]), axis=1)
    df['order_book_depth'] = df.apply(lambda row: len(row['order_book']), axis=1)
    return df


# Todo: Calculate the max quantity that can be sold on Binance without exceeding the acceptable slippage





