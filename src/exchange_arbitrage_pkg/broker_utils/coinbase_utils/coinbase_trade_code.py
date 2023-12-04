from decimal import Decimal


# Function to check balance for a given currency
from src.exchange_arbitrage_pkg.broker_utils.coinbase_utils.coinbase_symbol_utils import get_base_from_pair_coinbase
from src.exchange_arbitrage_pkg.utils.symbol_pair_pkg.advancetrade_symbol_funcs.symbol_info_fetch_cb import \
    adjust_trade_amount_coinbase


async def check_balance_coinbase(client, symbol, debug=False):
    available_balance, has_bought_before = await client.check_balance_coinbase(symbol)
    return available_balance


# Function to place a buy or sell order
async def buy_sell_coinbase(client, symbol, side, quantity, price=None, debug=False):
    adjusted_quantity = adjust_trade_amount_coinbase(symbol=symbol,
                                                     suggested_amount=quantity,
                                                     side=side,
                                                     price=price)
    # Assumes create_order method takes 'buy' or 'sell' as order_type, and price can be None for market order
    return await client.create_order(order_type=side,
                                     amount=adjusted_quantity,
                                     currency=symbol,
                                     price=price)


# Function to withdraw currency to a specified address
async def withdraw_coinbase(client, symbol, amount, crypto_address, debug=False):
    currency = get_base_from_pair_coinbase(symbol)
    return await client.withdraw_to_address(address=crypto_address, amount=amount, currency=currency)


# Function to get deposit address for a given currency
async def get_deposit_address_coinbase(client, symbol, debug=False):
    currency = get_base_from_pair_coinbase(symbol)
    return await client.fetch_deposit_address(currency)

# async def check_balance_coinbase(client, symbol):
#     try:
#         accounts = client.get_accounts()
#         for acc in accounts:
#             if acc.get('currency') == symbol:
#                 return acc
#     except Exception as e:
#         print(f"Error checking balance for {symbol} on Coinbase Pro: {e}")
#
#
# async def buy_sell_coinbase(client, symbol, side, quantity, price=None):
#     try:
#         order = client.place_order(
#             product_id=symbol,
#             side=side,
#             type='limit' if price else 'market',
#             price=price,
#             size=quantity
#         )
#         return order
#     except Exception as e:
#         print(f"Error {side}ing {symbol} on Coinbase Pro: {e}")
#
#
# async def withdraw_coinbase(client, currency, amount, crypto_address):
#     try:
#         withdrawal = await client.crypto_withdraw(
#             amount=amount,
#             currency=currency,
#             crypto_address=crypto_address
#         )
#         return withdrawal
#     except Exception as e:
#         print(f"Error withdrawing {currency} from Coinbase Pro: {e}")
#
#
# async def get_deposit_address_coinbase(client, currency):
#     try:
#         # Retrieve the deposit address for the specified currency
#         crypto_account = next(acc for acc in client.get_accounts() if acc['currency'] == currency)
#         deposit_info = client.fetch_deposit_address(crypto_account['id'])
#         return deposit_info
#     except Exception as e:
#         print(f"Error getting deposit address for {currency} on Coinbase Pro: {e}")
