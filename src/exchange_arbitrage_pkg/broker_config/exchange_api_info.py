import os
from abc import ABC
from decouple import config


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


class CoinbaseAPIKeys02(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = config("cb_hft_key_02")
        self.secret_key = config("cb_hft_secret_02")
        self.is_testnet = False


class CoinbaseAPIKeys03(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = config("cb_hft_key_03")
        self.secret_key = config("cb_hft_secret_03")
        self.is_testnet = False


class CoinbaseAPIKeysSandBox(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = str(os.environ.get("coinbase_api"))
        self.secret_key = str(os.environ.get("coinbase_secret"))
        self.is_testnet = True


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


# class CoinbaseProAPIKeys(APIAuthClass):
#     def __init__(self):
#         super().__init__()
#         self.api_key = str(os.environ.get("Coinbase_pro_api_key"))
#         self.secret_key = str(os.environ.get("Coinbase_pro_decret_key"))
#         self.pass_phrase = str(os.environ.get("Cpinbase_pro_pass_phrase"))
#         self.is_testnet = False


class BinanceAPIKeys(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = str(os.environ.get("binance_api"))
        self.secret_key = str(os.environ.get("binance_secret"))
        self.is_testnet = False


class BinanceAPIKeysHFT01(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = str(os.environ.get("binance_hft_api_key"))
        self.secret_key = str(os.environ.get("binance_hft_secret"))
        self.is_testnet = False


class BinanceAPIKeysHFT02(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = config("bi_my_hft_key_02")
        self.secret_key = config("bi_my_hft_secret_02")
        self.is_testnet = False


class BinanceAPIKeysHFT03(APIAuthClass):
    def __init__(self):
        super().__init__()
        self.api_key = config("bi_my_hft_key_03")
        self.secret_key = config("bi_my_hft_secret_03")
        self.is_testnet = False

