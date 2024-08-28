# Function to check balance for a given currency
from src.exchange_code_bases.advance_trade.advancetrade_symbol_funcs.symbol_info_fetch_cb import \
    adjust_trade_amount_coinbase, adjust_withdrawal_amount
from src.exchange_code_bases.advance_trade.coinbase_utils.coinbase_symbol_utils import get_base_from_pair_coinbase


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
    order =  await client.create_order(order_type=side,
                                     amount=adjusted_quantity,
                                     currency=symbol,
                                     price=price)
    if debug:
        print(f"On Coinbase: {side} order status for {symbol}: {order}")
    return order


# Function to withdraw currency to a specified address
async def withdraw_coinbase(client, symbol, amount, crypto_address, debug=False):
    base_currency = get_base_from_pair_coinbase(symbol)
    balance = await check_balance_coinbase(client, symbol, debug)
    def inner_amount_Adjuster(amount_in):
        return adjust_withdrawal_amount(symbol, amount_in, balance)

    amount_adjusted = inner_amount_Adjuster(amount)
    return await client.withdraw_to_address_persistent(crypto_address, amount_adjusted, base_currency,
                                                       inner_amount_Adjuster, 8)



# Function to get deposit address for a given currency
async def get_deposit_address_coinbase(client, symbol, debug=False):
    currency = get_base_from_pair_coinbase(symbol)
    if debug:
        print(f"Coinbase AT - Deposit address for {currency}: {'deposit_address'}")

    return await client.fetch_deposit_address(currency)
