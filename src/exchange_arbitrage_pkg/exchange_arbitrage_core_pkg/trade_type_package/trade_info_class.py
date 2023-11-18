class TradeInformation:
    def __init__(self, trade_type, symbol, side, quantity, price=None, stop_price=None):
        self.trade_type = trade_type
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price

