import cbpro
# async def check_balance_coinbase(client, symbol):
#     try:
#         def get_accounts():
#             return client.get_accounts()
#
#         accounts = await async_wrap(get_accounts)
#         for acc in accounts:
#             if acc.get('currency') == symbol:
#                 return acc
#     except Exception as e:
#         print(f"Error checking balance for {symbol} on Coinbase Pro: {e}")


async def check_balance_coinbase(client, symbol):
    try:
        accounts = client.get_accounts()
        for acc in accounts:
            if acc.get('currency') == symbol:
                return acc
    except Exception as e:
        print(f"Error checking balance for {symbol} on Coinbase Pro: {e}")


async def buy_sell_coinbase(client, symbol, side, quantity, price=None):
    try:
        order = client.place_order(
            product_id=symbol,
            side=side,
            type='limit' if price else 'market',
            price=price,
            size=quantity
        )
        return order
    except Exception as e:
        print(f"Error {side}ing {symbol} on Coinbase Pro: {e}")


async def withdraw_coinbase(client, currency, amount, crypto_address):
    try:
        withdrawal = await client.crypto_withdraw(
            amount=amount,
            currency=currency,
            crypto_address=crypto_address
        )
        return withdrawal
    except Exception as e:
        print(f"Error withdrawing {currency} from Coinbase Pro: {e}")


async def get_deposit_address_coinbase(client, currency):
    try:
        # Retrieve the deposit address for the specified currency
        crypto_account = next(acc for acc in client.get_accounts() if acc['currency'] == currency)
        deposit_info = client.fetch_deposit_address(crypto_account['id'])
        return deposit_info
    except Exception as e:
        print(f"Error getting deposit address for {currency} on Coinbase Pro: {e}")
