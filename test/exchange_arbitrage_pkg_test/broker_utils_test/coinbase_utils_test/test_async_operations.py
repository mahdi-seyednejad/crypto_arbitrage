# import pytest
# import asyncio
#
# from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys
# from src.exchange_arbitrage_pkg.broker_utils.coinbase_utils.coinbase_trade_code import check_balance_coinbase, \
#     buy_sell_coinbase, get_deposit_address_coinbase
# from src.exchange_code_bases.advance_trade.cb_advance_trade_client.cbat_async import AsyncAdvanceTradeClient
#
#
# Api_Auth_Obj = CoinbaseAPIKeys()
#
# @pytest.mark.asyncio
# async def test_check_balance_coinbase():
#     client = AsyncAdvanceTradeClient(Api_Auth_Obj)  # Initialize with valid credentials
#     symbol = "BTC-USD"
#     balance = await check_balance_coinbase(client, symbol)
#     print("\nExtracted balance on advance trade for BTC:", balance)
#     assert isinstance(balance, float)  # Replace with appropriate assertion
#
# @pytest.mark.asyncio
# async def test_buy_sell_coinbase():
#     client = AsyncAdvanceTradeClient(Api_Auth_Obj)  # Initialize with valid credentials
#     symbol = "BTC"
#     side = "buy"
#     quantity = 0.001  # Small amount for test
#     price = None  # Market order
#     order_result = await buy_sell_coinbase(client, symbol, side, quantity, price)
#     assert order_result  # Replace with appropriate assertion
#
# @pytest.mark.asyncio
# async def test_withdraw_coinbase():
#     # Mock or use sandbox environment for this test
#     pass
#
# @pytest.mark.asyncio
# async def test_get_deposit_address_coinbase():
#     client = AsyncAdvanceTradeClient(Api_Auth_Obj)  # Initialize with valid credentials
#     currency = "BTC"
#     address = await get_deposit_address_coinbase(client, currency)
#     assert address  # Replace with appropriate assertion
