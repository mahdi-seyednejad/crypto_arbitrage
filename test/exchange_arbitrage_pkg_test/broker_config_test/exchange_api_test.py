import asyncio

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, BinanceAPIKeysHFT01
from src.exchange_code_bases.advance_trade.coinbase_utils.coinbase_trade_code import withdraw_coinbase
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange

async def cbat_withdraw_test():
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
    currency = "WAXL-USD"
    address = "0..........."
    quantity = 61.49
    cb_async_client = await coinbase_exchange.create_async_client()
    result = await withdraw_coinbase(client=cb_async_client,
                                     amount=quantity,
                                     symbol=currency,
                                     crypto_address=address,
                                     debug=True)
    print(result)

def test_cbat_fetch_budget_smoke_test():
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
    currency = "BTC"
    budget = coinbase_exchange.sync_client.fetch_budget(currency=currency)
    print(budget)
    print(coinbase_exchange.get_available_amount_sync(currency=currency))

def test_binance_fetch_budget_smoke_test():
    binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
    currency = "BTC"
    budget = binance_exchange.sync_client.fetch_budget(currency=currency)
    print(budget)
    print(binance_exchange.get_available_amount_sync(currency=currency))




if __name__ == '__main__':
    # test_advanced_trade()
    # test_advanced_trade_git_package()
    # test_check_balance_cbat()
    asyncio.run(cbat_withdraw_test())
