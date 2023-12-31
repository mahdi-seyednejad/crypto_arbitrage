import asyncio
import json

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, BinanceAPIKeysHFT01
from src.exchange_arbitrage_pkg.broker_utils.coinbase_utils.coinbase_trade_code import withdraw_coinbase
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.advance_trade.cb_advance_trade_client.cbat_client import CbAdvanceTradeClient
from src.exchange_code_bases.advance_trade.client_authentication.coinbase_auth import CoinbaseAuth
from src.exchange_code_bases.advance_trade.client_authentication.utility_funcs import create_asset_dataframe, \
    get_available_amount, calculate_available_budget
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange


#
# def test_advanced_trade():
#     # Replace with your actual Coinbase Pro API key, secret, and passphrase
#     api_obj = CoinbaseAPIKeys()
#     api_key = api_obj.api_key
#     secret_key = api_obj.secret_key
#     # Replace with your API key and secret key
#     # Create CoinbaseAuth object
#     auth = CoinbaseAuth(api_key, secret_key)
#     # Get account information using the CoinbaseAuth object
#     account_info = auth.get_account_info()
#     print(json.dumps(account_info, indent=2))
#     print("create_asset_dataframe: ", create_asset_dataframe(account_info['data']))
#     print("get_available_amount: ", get_available_amount(account_info['data'], "BTC"))
#     print("calculate_available_budget: ", calculate_available_budget(account_info['data']))
#
#
# def test_advanced_trade_git_package():
#     # Replace with your actual Coinbase Pro API key, secret, and passphrase
#     api_obj = CoinbaseAPIKeys()
#     api_key = api_obj.api_key
#     secret_key = api_obj.secret_key
#     # Replace with your API key and secret key
#     # Create CoinbaseAuth object
#     client = CbAdvanceTradeClient(api_obj)
#     account_info = client.fetch_account_info()
#     # print(account_info.to_json(orient='records', lines=True))
#     order_book = client.fetch_order_book(product_id="BTC-USD")
#     # print(json.dumps(order_book, indent=2))
#
#     at_ex = AdvanceTradeExchange(api_auth_obj=api_obj)
#     order_book = at_ex.get_order_book_sync(client, symbol="BTC-USD")
#     # print(order_book.head().to_string())
#

# def test_check_balance_cbat():
#     coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
#     result = coinbase_exchange.sync_client.check_balance_coinbase("BTC")
#     print(result)
#

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
    # result = coinbase_exchange.sync_client.withdraw_to_address_persistent(address=address,
    #                                                                       amount=0.0001,
    #                                                                       currency=currency)
    # print(result)
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


# def test_withdraw_fee():
#     currency = "ETH"
#     network = "ethereum"
#     address = "0x.............."
#     coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
#     result = coinbase_exchange.sync_client.fetch_withdrawal_fee_estimate(currency=currency,
#                                                                          network=network,
#                                                                          crypto_address=address)
#     print(result)


if __name__ == '__main__':
    # test_advanced_trade()
    # test_advanced_trade_git_package()
    # test_check_balance_cbat()
    asyncio.run(cbat_withdraw_test())
