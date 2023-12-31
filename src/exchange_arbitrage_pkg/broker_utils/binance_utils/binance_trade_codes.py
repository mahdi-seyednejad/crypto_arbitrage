from binance.client import Client
import traceback

from binance.enums import ORDER_TYPE_MARKET

from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_symbol_utils import get_base_currency_binance

from src.exchange_code_bases.binance_enhanced.binance_tools.trade_amount_adjust_Async import BinanceAmountAdjusterAsync


async def check_balance_binance(client, symbol):
    try:
        balance = await client.get_asset_balance(asset=symbol)
        if balance is None:
            print(f"Balance for {symbol} on Binance is None")
            return 0
        else:
            return float(balance['free'])
    except Exception as e:
        print(f"Error checking balance for {symbol}: {e}")
        traceback.print_exc()  # This prints the full traceback
        return None


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


async def withdraw_binance(client, symbol, quantity, address, network, debug=False):
    # Note: Ensure the withdrawal address is whitelisted in your Binance account
    base_currency = get_base_currency_binance(symbol)

    try:
        withdrawal = await client.withdraw(
            coin=base_currency,
            amount=quantity,
            address=address,
            network=network  # Add the network parameter

        )
        if debug:
            print(f"Binance - Withdrawal of {base_currency}: {withdrawal}")
        return withdrawal
    except Exception as e:
        print(f"Error withdrawing {base_currency} from Binance: {e}")
        return None


async def buy_binance(client, symbol, quantity, price=None, debug=False, buy_min_notional=True):
    bi_amount_adjuster = BinanceAmountAdjusterAsync(client)  # Move it to the exchange code

    adjusted_quantity = await bi_amount_adjuster.adjust_buy_amount(symbol=symbol,
                                                                   quantity=quantity)
    if adjusted_quantity < 0:
        if buy_min_notional:
            print(f"Adjusted quantity is negative for {symbol} on Binance. "
                  f"Setting it to 0. Will try to buy anyway.")
            adjusted_quantity = abs(adjusted_quantity)
        else:
            adjusted_quantity = 0
    elif adjusted_quantity == 0:
        print(f"Adjusted quantity is 0 for {symbol} on Binance. Will not try to buy.")
        return None

    formatted_amount = "{:.8f}".format(adjusted_quantity)
    try:
        if price is None:
            # Market order
            # order = await client.order_market_buy(symbol=symbol, quantity=adjusted_quantity)
            order = await client.create_order(symbol=symbol,
                                              side="BUY",
                                              type=ORDER_TYPE_MARKET,
                                              quantity=formatted_amount)
        else:
            # Limit order
            order = await client.order_limit_buy(symbol=symbol, quantity=formatted_amount, price=str(price))
        if debug:
            print(f"On Binance: Buy order status for {symbol}: {order}")
        return order
    except Exception as e:
        print(f"Error buying {symbol} on Binance: {e}")


async def sell_binance(client, symbol, quantity, price=None, debug=False):
    bi_amount_adjuster = BinanceAmountAdjusterAsync(client)  # Move it to the exchange code
    adjusted_quantity = await bi_amount_adjuster.adjust_sell_amount(symbol, quantity)
    formatted_amount = "{:.8f}".format(adjusted_quantity)
    try:
        if price is None:
            # Market order
            order = await client.order_market_sell(symbol=symbol, quantity=formatted_amount)
        else:
            # Limit order
            order = await client.order_limit_sell(symbol=symbol, quantity=formatted_amount, price=str(price))
        if debug:
            print(f"Sell order status for {symbol}: {order}")
        return order
    except Exception as e:
        print(f"Error selling {symbol} on Binance: {e}")


async def get_deposit_address_binance(client, symbol, debug=False):
    base_currency = get_base_currency_binance(symbol)
    try:
        deposit_address = await client.get_deposit_address(coin=base_currency)
        # address = client.fetch_deposit_address(asset=base_currency)
        if debug:
            print(f"Binance - Deposit address for {base_currency}: {'deposit_address'}")

        return deposit_address['address']
    except Exception as e:
        print(f"Error getting deposit address for {base_currency} on Binance: {e}")
