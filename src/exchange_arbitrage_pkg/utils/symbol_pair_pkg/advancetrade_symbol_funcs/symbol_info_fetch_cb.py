import requests
import decimal


def fetch_latest_price(symbol):
    """
    Fetches the latest price for a given symbol from Coinbase.
    """
    url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to get latest price for {symbol}")

    latest_price = float(response.json()['price'])
    return latest_price


def fetch_trade_parameters(symbol):
    """
    Fetches trading parameters like base_increment and min_market_funds for a given symbol.
    """
    url = f"https://api.exchange.coinbase.com/products/{symbol}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to get trade parameters for {symbol}")

    data = response.json()
    buy_precision = float(data['base_increment'])
    min_notional = float(data['min_market_funds'])
    return buy_precision, min_notional


def adjust_trade_amount_coinbase(symbol, suggested_amount, price=None):
    """
    Adjusts the trade amount based on the trade parameters and the type of order (limit or market).
    """
    buy_precision, min_notional = fetch_trade_parameters(symbol)
    precision_decimal = decimal.Decimal(str(buy_precision))

    if price is None:
        # Market order
        price = fetch_latest_price(symbol)
        # Calculate minimum amount that can be bought
        min_amount = min_notional / price
        max_amount = max(suggested_amount, min_amount)
        adjusted = decimal.Decimal(str(max_amount)) \
                          .quantize(precision_decimal,
                                    rounding=decimal.ROUND_DOWN)
        return adjusted

    else:
        # Limit order
        # Adjust amount based on buy precision
        adjusted_amount = round(suggested_amount / buy_precision) * buy_precision
        # Ensure the total value meets the minimum notional value
        if adjusted_amount * price < min_notional:
            adjusted_amount = min_notional / price
        return decimal.Decimal(str(adjusted_amount)) \
                      .quantize(precision_decimal,
                                rounding=decimal.ROUND_DOWN)

# import requests
#
#
# def get_coinbase_trade_details(symbol):
#     url = f"https://api.exchange.coinbase.com/products/{symbol}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         buy_precision = data['base_increment']
#         min_notional = data['min_market_funds']
#         return buy_precision, min_notional
#     return None, None, None
#
#
# def adjust_coinbase_buy_amount(amount, symbol, price, buy_precision, min_buy_amount, min_notional):
#     adjusted_amount = round(amount / float(buy_precision)) * float(buy_precision)
#     if adjusted_amount < float(min_buy_amount):
#         raise ValueError("Amount is below the minimum buy amount")
#     if adjusted_amount * price < float(min_notional):
#         raise ValueError("Trade value is below the minimum notional value")
#     return adjusted_amount
#
#
# def get_adjusted_coinbase_trade_amount(symbol, amount):
#     buy_precision, min_buy_amount, min_notional = get_coinbase_trade_details(symbol)
#     if buy_precision is None:
#         raise ValueError(f"Could not fetch trade details for {symbol}")
#
#     # Fetch the latest price
#     url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
#     response = requests.get(url)
#     if response.status_code != 200:
#         raise ValueError(f"Failed to get latest price for {symbol}")
#
#     latest_price = float(response.json()['price'])
#     adjusted_amount = adjust_coinbase_buy_amount(amount, symbol, latest_price, buy_precision, min_buy_amount,
#                                                  min_notional)
#     return adjusted_amount
#
