from src.exchange_arbitrage_pkg.utils.symbol_pair_pkg.advancetrade_symbol_funcs.symbol_info_fetch_cb import \
    fetch_trade_params_coinbase, adjust_trade_amount_coinbase


def test_fetch_trade_params_coinbase():
    symbol: str = "BTC-USD"
    res = fetch_trade_params_coinbase(symbol=symbol)

def test_adjust_trade_amount_coinbase():
    res = adjust_trade_amount_coinbase(symbol="BTC-USD",
                                    suggested_amount=0.0123450006789001,
                                 side="buy",
                                    price=37860.0)

    print(res)

