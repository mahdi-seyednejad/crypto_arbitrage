from typing import Optional, List

from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass


class ExchangePair:
    def __init__(self, first_exchange: ExchangeAbstractClass, second_exchange: ExchangeAbstractClass):
        self.first_exchange = first_exchange
        self.second_exchange = second_exchange
        self.name_first_seller = second_exchange.name.value + "_to_" + first_exchange.name.value
        self.name_second_seller = first_exchange.name.value + "_to_" + second_exchange.name.value
        self.budget = None

    def __getitem__(self, index):
        if index == 0:
            return self.first_exchange
        elif index == 1:
            return self.second_exchange
        else:
            raise IndexError("Index out of range")

    def pick_exchange(self, exchange_name: ExchangeNames) -> Optional[ExchangeAbstractClass]:
        if self.first_exchange.name == exchange_name:
            return self.first_exchange
        elif self.second_exchange.name == exchange_name:
            return self.second_exchange
        return None  # Return None if no match is found

    def get_all_price_cols(self) -> List[str]:
        return [self.first_exchange.price_col, self.second_exchange.price_col]

    def set_all_budgets(self, budget):
        self.first_exchange.set_budget(self.first_exchange.sync_client, budget)
        self.second_exchange.set_budget(self.second_exchange.sync_client, budget)

    def get_first_exchange(self):
        return self.first_exchange

    def get_second_exchange(self):
        return self.second_exchange

    def get_1st_ex_budget_sync(self):
        return self.first_exchange.get_budget_sync()

    def get_2nd_ex_budget_sync(self):
        return self.second_exchange.get_budget_sync()
