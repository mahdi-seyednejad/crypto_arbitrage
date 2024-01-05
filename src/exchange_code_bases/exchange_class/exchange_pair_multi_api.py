from collections import deque
from typing import List, Optional

from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.exchange_class.base_exchange_class import ExchangeAbstractClass
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange
from src.exchange_code_bases.exchange_class.exchange_pair_class import ExchangePair
from collections import deque
from typing import List

class CollectableExPair:
    def __init__(self,
                 first_exchanges: List[ExchangeAbstractClass],
                 second_exchanges: List[ExchangeAbstractClass]):
        self.first_exchanges = deque(first_exchanges)
        self.second_exchanges = deque(second_exchanges)

    def get_next_exchange_pair(self) -> ExchangePair:
        # Retrieve the next instance from each queue
        first_exchange = self.first_exchanges[0]
        second_exchange = self.second_exchanges[0]

        # Rotate the queues to get the next instance for the next call
        self.first_exchanges.rotate(-1)
        self.second_exchanges.rotate(-1)

        # Return a new ExchangePair with the selected instances
        return ExchangePair(first_exchange, second_exchange)

    def get_len(self):
        return len(self.first_exchanges)

    def set_all_budgets(self, budget):
        for exchange in self.first_exchanges:
            exchange.set_budget(exchange.sync_client, budget)
        for exchange in self.second_exchanges:
            exchange.set_budget(exchange.sync_client, budget)

# class ExchangePairMultiApi(ExchangePair):
#     def __init__(self,
#                  first_exchange_list: List[ExchangeAbstractClass],
#                  second_exchange_list: List[ExchangeAbstractClass],
#                  debug=False):
#         super().__init__(first_exchange=first_exchange_list[0],
#                          second_exchange=second_exchange_list[0],
#                          debug=debug)
#         self.first_exchanges = deque(first_exchange_list)
#         self.second_exchanges = deque(second_exchange_list)
#
#     def get_next_exchange(self, exchanges: deque) -> ExchangeAbstractClass:
#         exchange = exchanges[0]
#         exchanges.rotate(-1)  # Move the first exchange to the end
#         return exchange
#
#     def get_first_exchange(self):
#         return self.get_next_exchange(self.first_exchanges)
#
#     def get_second_exchange(self):
#         return self.get_next_exchange(self.second_exchanges)
#







