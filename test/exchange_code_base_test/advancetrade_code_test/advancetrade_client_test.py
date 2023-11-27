from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, CoinbaseAPIKeysSandBox
from src.exchange_arbitrage_pkg.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_arbitrage_pkg.utils.symbol_pair_pkg.advancetrade_symbol_funcs.symbol_info_fetch_cb import \
    adjust_trade_amount_coinbase
import pprint


def test_advancetrade_client():
    """Tests for advancetrade_client"""
    # coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
    # client = coinbase_exchange.sync_client
    # res = client.get_coinbase_symbol_details("BTC-USD")
    adjusted_qty_market = adjust_trade_amount_coinbase(symbol="BTC-USD",
                                                       suggested_amount=0.0123450006789001)
    print(adjusted_qty_market)

    adjusted_qty_limit = adjust_trade_amount_coinbase(symbol="BTC-USD",
                                                      suggested_amount=0.0123450006789001,
                                                      price=37860.0)
    print(adjusted_qty_limit)



if __name__ == '__main__':
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
    # budget = coinbase_exchange.get_budget_sync()
    # print(budget)
    order_type = "buy"
    amount = 0.00002
    currency = "BTC"
    order = coinbase_exchange.sync_client.create_order(order_type=order_type,
                                                       amount=amount,
                                                       currency=currency)

    print("\norder output:")
    pprint.pprint(order)
