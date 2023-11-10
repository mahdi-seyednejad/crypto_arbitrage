import os

class CoinbaseAPIKeys:
    def __init__(self):
        self.api_key_coinbase = str(os.environ.get("coinbase_api"))
        self.secret_key_coinbase = str(os.environ.get("coinbase_secret"))
# api_key_coinbase = str(os.environ.get("coinbase_api"))
# secret_key_coinbase = str(os.environ.get("coinbase_secret"))


class BinanceAPIKeys:
    def __init__(self):
        self.api_key_binance_read_only = str(os.environ.get("b_api_read_only"))
        self.secret_key_binance_read_only = str(os.environ.get("b_secret_read_only"))

        self.api_key_binance = str(os.environ.get("binance_api"))
        self.secret_key_binance = str(os.environ.get("binance_secret"))

        self.api_key_binance_testnet = str(os.environ.get("binance_api_testnet"))
        self.secret_key_binance_testnet = str(os.environ.get("binance_secret_testnet"))
# api_key_binance_read_only = str(os.environ.get("b_api_read_only"))
# secret_key_binance_read_only = str(os.environ.get("b_secret_read_only"))
#
# api_key_binance = str(os.environ.get("binance_api"))
# secret_key_binance = str(os.environ.get("binance_secret"))
#
#
# api_key_binance_testnet = str(os.environ.get("binance_api_testnet"))
# secret_key_binance_testnet = str(os.environ.get("binance_secret_testnet"))

