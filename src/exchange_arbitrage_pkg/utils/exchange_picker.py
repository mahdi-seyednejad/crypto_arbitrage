from typing import List, Optional

from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass


def pick_exchange(exchange_name: str,
                  exchange_list: List[ExchangeAbstractClass]) \
        -> Optional[ExchangeAbstractClass]:
    for exchange in exchange_list:
        if exchange.name == exchange_name:
            return exchange
    return None  # Return None if no match is found
