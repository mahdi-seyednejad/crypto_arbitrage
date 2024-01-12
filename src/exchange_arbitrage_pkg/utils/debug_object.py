class DebugClass:
    def __init__(self,
                 price_diff_debug,
                 arbitrage_machine_debug,
                 db_handler_debug):
        self.price_diff_debug = price_diff_debug
        self.arbitrage_machine_debug = arbitrage_machine_debug
        self.db_handler_debug = db_handler_debug

    def __repr__(self):
        return f"DebugClass(price_diff_debug={self.price_diff_debug}, arbitrage_machine_debug={self.arbitrage_machine_debug}, db_handler_debug={self.db_handler_debug})"

    def __str__(self):
        return f"DebugClass(price_diff_debug={self.price_diff_debug}, arbitrage_machine_debug={self.arbitrage_machine_debug}, db_handler_debug={self.db_handler_debug})"

    def get_total_debug(self):
        return self.price_diff_debug and self.arbitrage_machine_debug and self.db_handler_debug

    def least_true(self):
        return self.price_diff_debug or self.arbitrage_machine_debug or self.db_handler_debug