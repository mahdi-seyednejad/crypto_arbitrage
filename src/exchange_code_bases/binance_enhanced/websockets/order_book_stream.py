import websocket
import json

def on_message(ws, message):
    print("Received Message:")
    print(json.loads(message))

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    # Subscribe to the BTCUSDT depth stream
    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": ["btcusdt@depth"],
        "id": 1
    }))

if __name__ == "__main__":
    socket = "wss://stream.binance.us:9443/ws/btcusdt@depth"
    #Depth Levels: You can specify the depth of the order book (e.g., btcusdt@depth5 for top 5 levels).
    ws = websocket.WebSocketApp(socket,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()
