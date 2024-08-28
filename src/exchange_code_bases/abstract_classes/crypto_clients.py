from abc import ABC, abstractmethod


class CryptoClient(ABC):

    @abstractmethod
    def fetch_account_info(self):
        pass

    @abstractmethod
    def withdraw_to_address(self, address, amount, currency):
        pass

    @abstractmethod
    def fetch_budget(self, currency):
        pass

    @abstractmethod
    def fetch_deposit_address(self, currency):
        pass

    @abstractmethod
    def fetch_available_cryptos(self):
        pass

    @abstractmethod
    def fetch_all_available_base_assets(self):
        pass

    @abstractmethod
    def create_order(self, order_type, amount, currency, price=None):
        pass

    @abstractmethod
    def fetch_order_book(self, symbol, limit=100):
        pass

