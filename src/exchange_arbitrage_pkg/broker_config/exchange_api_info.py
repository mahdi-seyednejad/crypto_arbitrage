import os
from abc import ABC


class APIAuthClass(ABC):
    def __init__(self):
        self.api_key = None
        self.secret_key = None
        self.pass_phrase = None
        self.is_testnet = None


class CoinbaseAPIKeys(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = str(os.environ.get("coinbase_api"))
        self.secret_key = str(os.environ.get("coinbase_secret"))
        self.is_testnet = False


class CoinbaseAPIKeysSandBox(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = str(os.environ.get("coinbase_api"))
        self.secret_key = str(os.environ.get("coinbase_secret"))
        self.is_testnet = True


class CoinbaseProAPIKeys(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = str(os.environ.get("Coinbase_pro_api_key"))
        self.secret_key = str(os.environ.get("Coinbase_pro_decret_key"))
        self.pass_phrase = str(os.environ.get("Cpinbase_pro_pass_phrase"))
        self.is_testnet = False


class BinanceAPIKeys(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = str(os.environ.get("binance_api"))
        self.secret_key = str(os.environ.get("binance_secret"))
        self.is_testnet = False


class BinanceAPIKeysReadOnly(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = str(os.environ.get("b_api_read_only"))
        self.secret_key = str(os.environ.get("b_secret_read_only"))
        self.is_testnet = False


class BinanceAPIKeysTestNet(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = str(os.environ.get("binance_api_testnet"))
        self.secret_key = str(os.environ.get("binance_secret_testnet"))
        self.is_testnet = True

#