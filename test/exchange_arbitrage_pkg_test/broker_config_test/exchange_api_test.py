import json

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.advance_trade.cb_advance_trade_client.cbat_client import CbAdvanceTradeClient
from src.exchange_code_bases.advance_trade.client_authentication.coinbase_auth import CoinbaseAuth
from src.exchange_code_bases.advance_trade.client_authentication.utility_funcs import create_asset_dataframe, \
    get_available_amount, calculate_available_budget


def test_advanced_trade():
    # Replace with your actual Coinbase Pro API key, secret, and passphrase
    api_obj = CoinbaseAPIKeys()
    api_key = api_obj.api_key
    secret_key = api_obj.secret_key
    # Replace with your API key and secret key
    # Create CoinbaseAuth object
    auth = CoinbaseAuth(api_key, secret_key)
    # Get account information using the CoinbaseAuth object
    account_info = auth.get_account_info()
    print(json.dumps(account_info, indent=2))
    print("create_asset_dataframe: ", create_asset_dataframe(account_info['data']))
    print("get_available_amount: ", get_available_amount(account_info['data'], "BTC"))
    print("calculate_available_budget: ", calculate_available_budget(account_info['data']))


def test_advanced_trade_git_package():
    # Replace with your actual Coinbase Pro API key, secret, and passphrase
    api_obj = CoinbaseAPIKeys()
    api_key = api_obj.api_key
    secret_key = api_obj.secret_key
    # Replace with your API key and secret key
    # Create CoinbaseAuth object
    client = CbAdvanceTradeClient(api_key=api_key, api_secret=secret_key)
    account_info = client.fetch_account_info()
    print(json.dumps(account_info, indent=2))
    order_book = client.fetch_order_book(product_id="BTC-USD")
    # print(json.dumps(order_book, indent=2))

    at_ex = AdvanceTradeExchange(api_auth_obj=api_obj)
    order_book = at_ex.get_order_book_sync(symbol="BTC-USD")
    print(order_book.head().to_string())
