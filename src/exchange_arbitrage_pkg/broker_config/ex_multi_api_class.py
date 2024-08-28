from typing import Optional, List, Union

# from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass, CoinbaseAPIKeys
import src.exchange_arbitrage_pkg.broker_config.exchange_api_info as api_info


class MultiApiAuthClass:
    def __init__(self, api_auth_obj_list: List[api_info.APIAuthClass]):
        self.ex_api_list = api_auth_obj_list

    def get_ex_api_list(self):
        return self.ex_api_list


CBAT_MULTI_API_OBJ = MultiApiAuthClass(api_auth_obj_list=[api_info.CoinbaseAPIKeys(),
                                                          api_info.CoinbaseAPIKeys02(),
                                                          api_info.CoinbaseAPIKeys03()])

BINANCE_MULTI_API_OBJ = MultiApiAuthClass(api_auth_obj_list=[api_info.BinanceAPIKeysHFT01(),
                                                             api_info.BinanceAPIKeysHFT02(),
                                                             api_info.BinanceAPIKeysHFT03()])
