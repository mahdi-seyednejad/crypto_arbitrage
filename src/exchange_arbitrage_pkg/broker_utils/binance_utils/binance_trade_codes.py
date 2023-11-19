from binance.client import Client
import asyncio


async def check_balance(client, symbol):
    balance = None
    try:
        balance = client.get_asset_balance(asset=symbol)
        # return balance
    except Exception as e:
        print(f"Error checking balance for {symbol} on Binance: {e}")

    return balance


async def place_limit_order(client, symbol, side, quantity, price):
    order = client.create_order(
        symbol=symbol,
        side=side,
        type=Client.ORDER_TYPE_LIMIT,
        timeInForce=Client.TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=price
    )
    print(f"Limit Order {side} for {symbol}: {order}")
    return order


async def withdraw(client, asset, quantity, address, debug=False):
    # Note: Ensure the withdrawal address is whitelisted in your Binance account
    try:
        withdrawal = client.withdraw(
            asset=asset,
            amount=quantity,
            address=address
        )
        if debug:
            print(f"Withdrawal of {asset}: {withdrawal}")
        return withdrawal
    except Exception as e:
        print(f"Error withdrawing {asset} from Binance: {e}")


# async def execute_binance_trade(client, trade):
#     if trade.trade_type == 'check':
#         await check_balance(client, trade.symbol)
#     elif trade.trade_type == 'limit_order':
#         await place_limit_order(client, trade.symbol, trade.side, trade.quantity, trade.price)
#     elif trade.trade_type == 'withdraw':
#         # You need to provide the withdrawal address
#         await withdraw(client, trade.symbol, trade.quantity, 'your_withdrawal_address')
#     # ... add other trade types as needed
#     await asyncio.sleep(1)  # Simulate async operation

async def buy_binance(client, symbol, quantity, price=None, debug=False):
    try:
        if price is None:
            # Market order
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
        else:
            # Limit order
            order = client.order_limit_buy(symbol=symbol, quantity=quantity, price=str(price))
        if debug:
            print(f"Buy order status for {symbol}: {order}")
        return order
    except Exception as e:
        print(f"Error buying {symbol} on Binance: {e}")


async def sell_binance(client, symbol, quantity, price=None, debug=False):
    try:
        if price is None:
            # Market order
            order = client.order_market_sell(symbol=symbol, quantity=quantity)
        else:
            # Limit order
            order = client.order_limit_sell(symbol=symbol, quantity=quantity, price=str(price))
        if debug:
            print(f"Sell order status for {symbol}: {order}")
        return order
    except Exception as e:
        print(f"Error selling {symbol} on Binance: {e}")


async def get_deposit_address_binance(client, symbol, debug=False):
    try:
        address = client.get_deposit_address(asset=symbol)
        if debug:
            print(f"Deposit address for {symbol}: {address}")

        return address
    except Exception as e:
        print(f"Error getting deposit address for {symbol} on Binance: {e}")




