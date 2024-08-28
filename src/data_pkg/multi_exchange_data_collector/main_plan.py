import time
from abc import ABC, abstractmethod


class ExchangeAgent(ABC):
    def __init__(self, exchange_name: str, api_key: str, secret_key: str):
        self.exchange_name = exchange_name
        self.api_key = api_key
        self.secret_key = secret_key
        self.symbol_list = None
        self.exchange_client = None
        self.exchange_symbol_capacity = None

    def accept_symbols(self, symbol_list: list):
        self.symbol_list = symbol_list

    def download_all_symbol_order_books(self):
        pass

    def insert_to_db(self):
        pass


class DataCollector(ABC):
    def __init__(self,
                 collecting_interval: int,
                 symbol_list: list,
                 exchange_agents):
        self.collecting_interval = collecting_interval
        self.symbol_list = symbol_list
        self.exchange_agents = exchange_agents

    @abstractmethod
    def distribute_symbols_to_exchange_agents(self):
        pass

    def collect_data(self):
        self.distribute_symbols_to_exchange_agents()
        while True:
            self.exchange_agents.download_all_symbol_order_books()
            self.exchange_agents.insert_to_db()
            time.sleep(self.collecting_interval)



