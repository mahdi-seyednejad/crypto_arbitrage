from binance.client import Client

# Replace 'your_api_key' and 'your_api_secret' with your Binance API key and secret
api_key = 'your_api_key'
api_secret = 'your_api_secret'

# Initialize the client
client = Client(api_key, api_secret)

# Define order parameters
symbol = 'BTCUSDT'  # Replace with the symbol you want to trade
quantity = 0.001  # Replace with the amount of the cryptocurrency you want to buy/sell
price = 10000  # Replace with your desired price

# Place a limit buy order
order = client.create_order(
    symbol=symbol,
    side=Client.SIDE_BUY,
    type=Client.ORDER_TYPE_LIMIT,
    timeInForce=Client.TIME_IN_FORCE_GTC,  # Good till cancelled
    quantity=quantity,
    price=str(price)
)

print(order)
