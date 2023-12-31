from typing import Optional, List, Union

from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.trade_runner_package.operation_executor_class import OperationExecutor
from src.exchange_code_bases.exchange_class.base_exchange_class import ExchangeAbstractClass


class ExchangePair:
    def __init__(self, first_exchange: ExchangeAbstractClass, second_exchange: ExchangeAbstractClass, debug=False):
        self.first_exchange = first_exchange
        self.second_exchange = second_exchange
        self.name_first_seller = second_exchange.name.value + "_to_" + first_exchange.name.value
        self.name_second_seller = first_exchange.name.value + "_to_" + second_exchange.name.value
        self.operation_executor = OperationExecutor(first_exchange=first_exchange,
                                                    second_exchange=second_exchange,
                                                    debug=debug)
        self.budget = None

    def get_paired_fee_info_df(self):
        return self.operation_executor.network_convertor_obj.pair_df

    def __getitem__(self, index):
        if index == 0:
            return self.first_exchange
        elif index == 1:
            return self.second_exchange
        else:
            raise IndexError("Index out of range")

    def pick_exchange(self, exchange_name: Union[ExchangeNames, str]) -> Optional[ExchangeAbstractClass]:
        # Convert exchange_name to string if it is an enum member
        exchange_name_str = exchange_name.value if isinstance(exchange_name, ExchangeNames) else exchange_name

        if self.first_exchange.name.value == exchange_name_str:
            return self.first_exchange
        elif self.second_exchange.name.value == exchange_name_str:
            return self.second_exchange

        return None  # Return None if no match is found

    def get_all_exchanges(self) -> List[ExchangeAbstractClass]:
        return [self.first_exchange, self.second_exchange]

    def get_all_price_cols(self) -> List[str]:
        return [self.first_exchange.price_col, self.second_exchange.price_col]

    def set_all_budgets(self, budget):
        self.first_exchange.set_budget(self.first_exchange.sync_client, budget)
        self.second_exchange.set_budget(self.second_exchange.sync_client, budget)

    def get_ex_price_col(self, exchange_name: Union[ExchangeNames, str]) -> Optional[str]:
        # Convert exchange_name to string if it is an enum member
        exchange_name_str = exchange_name.value if isinstance(exchange_name, ExchangeNames) else exchange_name

        if self.first_exchange.name.value == exchange_name_str:
            return self.first_exchange.price_col
        elif self.second_exchange.name.value == exchange_name_str:
            return self.second_exchange.price_col

        return None

    def get_first_exchange(self):
        return self.first_exchange

    def get_second_exchange(self):
        return self.second_exchange

    def get_1st_ex_budget_sync(self):
        return self.first_exchange.get_budget_sync()

    def get_2nd_ex_budget_sync(self):
        return self.second_exchange.get_budget_sync()

    def get_list_of_exchanges(self):
        return [self.first_exchange, self.second_exchange]

    def get_exchange_names(self):
        return [self.first_exchange.name, self.second_exchange.name]

    def get_exchange_names_str_val(self):
        return [self.first_exchange.name.value, self.second_exchange.name.value]

    def get_operation_executor(self):
        return self.operation_executor

    def get_all_symbol_info_ex_pair(self):
        return self.first_exchange.sync_client.get_all_symbol_info()
