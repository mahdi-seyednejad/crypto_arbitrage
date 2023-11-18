from abc import ABC, abstractmethod

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames


class ExchangeAbstractClass(ABC):
    def __init__(self,
                 name: ExchangeNames,
                 api_auth_obj: APIAuthClass):
        self.name = name
        self.api_auth_obj = api_auth_obj




