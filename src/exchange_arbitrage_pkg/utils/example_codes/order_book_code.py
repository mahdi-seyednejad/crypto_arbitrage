from binance.client import Client

# Initialize your Binance Client
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

def get_order_book(symbol, limit=10):
    """
    Fetch the order book for a given symbol.
    """
    order_book = client.get_order_book(symbol=symbol, limit=limit)
    return order_book

def decide_buy_sell_prices(symbol):
    """
    Decide buy and sell prices based on the order book.
    """
    order_book = get_order_book(symbol)

    # Get the lowest ask and highest bid
    lowest_ask = float(order_book['asks'][0][0])
    highest_bid = float(order_book['bids'][0][0])

    # Set buy price slightly below the lowest ask, sell price slightly above the highest bid
    buy_price = lowest_ask * 0.99  # e.g., 1% below the lowest ask
    sell_price = highest_bid * 1.01  # e.g., 1% above the highest bid

    return buy_price, sell_price

def place_limit_buy_order(symbol, quantity, price):
    """
    Place a limit buy order.
    """
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_LIMIT,
        timeInForce=Client.TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=str(price)
    )
    return order

def place_limit_sell_order(symbol, quantity, price):
    """
    Place a limit sell order.
    """
    order = client.create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_LIMIT,
        timeInForce=Client.TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=str(price)
    )
    return order


if __name__ == "main":
    symbol = 'BTCUSDT'  # Replace with your desired symbol
    quantity_buy = 0.001  # Replace with your buy quantity
    quantity_sell = 0.001  # Replace with your sell quantity

    buy_price, sell_price = decide_buy_sell_prices(symbol)

    # Place limit buy order
    buy_order = place_limit_buy_order(symbol, quantity_buy, buy_price)
    print("Buy Order:", buy_order)

    # Place limit sell order
    sell_order = place_limit_sell_order(symbol, quantity_sell, sell_price)
    print("Sell Order:", sell_order)


