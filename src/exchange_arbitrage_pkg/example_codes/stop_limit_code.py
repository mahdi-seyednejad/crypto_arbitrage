from binance.client import Client

# Initialize your Binance Client
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

def place_stop_limit_buy_order(symbol, quantity, stop_price, limit_price):
    """
    Place a stop-limit buy order.
    """
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
        timeInForce=Client.TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=str(limit_price),
        stopPrice=str(stop_price)
    )
    return order


def place_stop_limit_sell_order(symbol, quantity, stop_price, limit_price):
    """
    Place a stop-limit sell order.
    """
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
        timeInForce=Client.TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=str(limit_price),
        stopPrice=str(stop_price)
    )
    return order


# Usage Example:
if __name__ == "__main__":
    symbol = 'BTCUSDT'  # Replace with your desired symbol
    quantity = 0.001  # Replace with your desired quantity

    # For a stop-limit buy order
    stop_price_buy = 9500  # Trigger price for the stop-limit buy order
    limit_price_buy = 9600  # Limit price for the buy order
    buy_order = place_stop_limit_buy_order(symbol, quantity, stop_price_buy, limit_price_buy)
    print("Stop-Limit Buy Order:", buy_order)

    # For a stop-limit sell order
    stop_price_sell = 10500  # Trigger price for the stop-limit sell order
    limit_price_sell = 10400  # Limit price for the sell order
    sell_order = place_stop_limit_sell_order(symbol, quantity, stop_price_sell, limit_price_sell)
    print("Stop-Limit Sell Order:", sell_order)
