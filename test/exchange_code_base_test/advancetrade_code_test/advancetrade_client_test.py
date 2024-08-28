from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
import pprint



if __name__ == '__main__':
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
    # budget = coinbase_exchange.get_budget_sync()
    # print(budget)
    # order_type = "buy"
    # amount = 0.00002
    # currency = "BTC"
    currency = "VOXEL"

    # order = coinbase_exchange.sync_client.create_order(order_type=order_type,
    #                                                    amount=amount,
    #                                                    currency=currency)
    #
    order = coinbase_exchange.sync_client\
                             .fetch_deposit_address(currency=currency)


    print("\norder output:")
    pprint.pprint(order)
