from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_class_pkg.exchange_class import ExchangeMachine

from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.trade_type_package.trade_eligibility import \
    check_symbols_for_trade, evaluate_symbols_for_trade
from src.exchange_arbitrage_pkg.utils.binance_coinbase_convertor import extract_symbol


def get_binance_to_coinbase_X(symbol):
    exchange_machine = ExchangeMachine(name="Binance_to_Coinbase",
                                       src_exchange_platform=ExchangeNames.Binance,
                                       dst_exchange_platform=ExchangeNames.Coinbase,
                                       client=None)
    exchange_machine.create_trades(symbol)

    return exchange_machine


def get_coinbase_to_binance_X(symbol):
    exchange_machine = ExchangeMachine(name="Binance_to_Coinbase",
                                       src_exchange_platform=ExchangeNames.Coinbase,
                                       dst_exchange_platform=ExchangeNames.Binance,
                                       client=None)
    exchange_machine.create_trades(symbol)

    return exchange_machine


def create_arbitrage_plan(df_in):
    df = df_in.copy()
    is_good_to_trade_col = 'is_good_to_trade_col'
    price_diff_bi_cb = 'price_diff_bi_cb'

    evaluate_symbols_for_trade

    df_trade_checked = check_symbols_for_trade(df_in=df,
                                               goodness_col_output=is_good_to_trade_col,
                                               price_diff_bi_cb=price_diff_bi_cb)

    exchange_machines = []
    exchange_machine = None
    for index, row in df_trade_checked.iterrows():
        symbol = extract_symbol(row)
        if row['price_diff_bi_cb'] > 0:
            # Opportunity: Buy on Coinbase, Sell on Binance
            exchange_machine = get_binance_to_coinbase_X(symbol)

        elif row['price_diff_bi_cb'] < 0:
            # Opportunity: Buy on Binance, Sell on Coinbase
            exchange_machine = get_coinbase_to_binance_X(symbol)

        if row['price_diff_bi_cb'] == 0 or exchange_machine is None:
            # No opportunity
            pass
        else:
            exchange_machines.append(exchange_machine)

    return exchange_machines


