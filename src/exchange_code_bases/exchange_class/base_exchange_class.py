from abc import ABC, abstractmethod

import aiohttp

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import APIAuthClass
from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.budget_manager.budget_manager_class import BudgetManager
from src.exchange_code_bases.abstract_classes.crypto_clients import CryptoClient


class ExchangeAbstractClass(ABC):
    def __init__(self,
                 name: ExchangeNames,
                 api_auth_obj: APIAuthClass):
        self.name = name
        self.api_auth_obj = api_auth_obj
        self.sync_client = None
        self.async_obj = None
        self.async_client = None
        self.budget = None
        self.budget_manager = BudgetManager(self.budget)
        self.withdrawal_factor = 0.95  # The mount of money that will be withdrawn from the exchange after deducting the gas fee
        self.price_col = None  # ToDO: Move the price column name here
        self.transaction_fee_rate = None  # ToDO: Move the transaction fee here
        self.maker_fee_rate = None  # ToDO: Move the maker fee here
        self.taker_fee_rate = None  # ToDO: Move the taker fee here
        self.session = aiohttp.ClientSession()

    def get_transaction_fee_rate(self):
        return self.transaction_fee_rate

    def get_budget_sync(self, currency: str = 'USDT'):
        return self.get_budget(self.sync_client, currency)

    def get_budget(self, client: CryptoClient, currency):
        if self.budget is None:
            budget_result = client.fetch_budget(currency)
            self.budget = float(budget_result['balance'])
            return self.budget
        else:
            return self.budget

    def set_budget(self, client: CryptoClient, defined_budget=None, currency='USDT'):
        if defined_budget is not None:
            self.budget = defined_budget
        else:
            extracted_budget = client.fetch_budget(currency)
            self.budget = float(extracted_budget['balance'])

    # Becareful about the concurrency in the budget.

    @abstractmethod
    def create_async_client(self):
        pass

    @abstractmethod
    def get_order_book_sync(self, client, symbol, depth=100):
        pass

    @abstractmethod
    def get_order_output_quantity(self, order, current_price):
        pass

    @abstractmethod
    async def wait_til_receive_Async(self,
                                     symbol,
                                     expected_amount,
                                     check_interval,
                                     timeout,
                                     amount_loss,
                                     second_chance,
                                     num_of_wait_tries,
                                     debug):
        pass

    def get_available_amount_sync(self, currency):
        return self.sync_client.fetch_budget(currency)

    @abstractmethod
    def get_current_price(self, symbol):
        pass

    @abstractmethod
    def filter_diff_df(self, diff_df):
        pass

    async def get_available_amount_async(self, currency):
        return await self.async_obj.client.fetch_budget(currency)

    async def close(self):
        await self.session.close()

