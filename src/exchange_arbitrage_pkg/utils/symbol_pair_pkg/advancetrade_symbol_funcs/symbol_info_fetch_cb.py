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


def adjust_quote_size_coinbase(quote_size, quote_increment):
    """
    Adjusts the quote size to match the required precision.
    """
    # Convert to Decimal for precision in calculations
    quote_size = decimal.Decimal(str(quote_size))
    quote_increment = decimal.Decimal(str(quote_increment))

    # Adjust the quote size
    adjusted_quote_size = (quote_size // quote_increment) * quote_increment

    return adjusted_quote_size


def fetch_trade_params_coinbase(symbol):
    """
    Fetches trading parameters like base_increment and min_market_funds for a given symbol.
    """
    url = f"https://api.exchange.coinbase.com/products/{symbol}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to get trade parameters for {symbol}")

    data = response.json()
    base_precision = float(data['base_increment'])
    min_notional = float(data['min_market_funds'])
    quote_precision = float(data['quote_increment'])
    return base_precision, min_notional, quote_precision


def adjust_buy_amount_coinbase(quote_precision, suggested_amount, current_price, min_notional):
    """
    Adjusts the buy amount based on the trade parameters and the type of order (limit or market).
    """
    # Convert
    quote_amount = suggested_amount * current_price
    precision_decimal = decimal.Decimal(str(quote_precision))
    adjusted_q_amount = round(quote_amount / quote_precision) * quote_precision
    if adjusted_q_amount < min_notional:
        result_q_amount = min_notional
    else:
        result_q_amount = decimal.Decimal(str(adjusted_q_amount)) \
            .quantize(precision_decimal,
                      rounding=decimal.ROUND_DOWN)

    return result_q_amount


def adjust_trade_amount_coinbase(symbol, suggested_amount, side, price=None):
    """
    Adjusts the trade amount based on the trade parameters and the type of order (limit or market).
    """
    base_precision, min_notional, quote_precision = fetch_trade_params_coinbase(symbol)
    precision_decimal = decimal.Decimal(str(base_precision))

    if side.lower() == 'buy':
        if price is None:
            # Market order
            price = fetch_latest_price(symbol)
        final_amount = adjust_buy_amount_coinbase(quote_precision=quote_precision,
                                                  suggested_amount=suggested_amount,
                                                  current_price=price,
                                                  min_notional=min_notional)
        # write the limit order later
    else:
        if price is None:
            # Market order
            # Calculate minimum amount that can be bought
            price = fetch_latest_price(symbol)
            min_amount = min_notional / price
            max_amount = max(suggested_amount, min_amount)
            adjusted = decimal.Decimal(str(max_amount)) \
                .quantize(precision_decimal,
                          rounding=decimal.ROUND_DOWN)
            final_amount = adjusted

        else:
            # Limit order
            # Adjust amount based on buy precision
            adjusted_amount = round(suggested_amount / base_precision) * base_precision
            # Ensure the total value meets the minimum notional value
            if adjusted_amount * price < min_notional:
                adjusted_amount = min_notional / price
            final_amount = decimal.Decimal(str(adjusted_amount)) \
                .quantize(precision_decimal,
                          rounding=decimal.ROUND_DOWN)

    return final_amount
