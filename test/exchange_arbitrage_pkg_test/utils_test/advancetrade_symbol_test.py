from src.exchange_code_bases.advance_trade.advancetrade_symbol_funcs.symbol_info_fetch_cb import \
    adjust_trade_amount_coinbase
from src.exchange_code_bases.advance_trade.cb_advance_trade_client.cbat_client import fetch_trade_params_coinbase


def test_fetch_trade_params_coinbase():
    symbol: str = "BTC-USD"
    res = fetch_trade_params_coinbase(symbol=symbol)
    print(res)

def test_adjust_trade_amount_coinbase():
    res = adjust_trade_amount_coinbase(symbol="BTC-USD",
                                    suggested_amount=0.0123450006789001,
                                 side="buy",
                                    price=37860.0)

    print(res)

