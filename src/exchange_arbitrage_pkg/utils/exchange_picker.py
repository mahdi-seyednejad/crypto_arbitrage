from typing import List, Optional

from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_class.base_exchange_class import ExchangeAbstractClass


def pick_exchange(exchange_name: ExchangeNames,
                  exchange_list: List[ExchangeAbstractClass]) \
        -> Optional[ExchangeAbstractClass]:
    for exchange in exchange_list:
        if exchange.name == exchange_name:
            return exchange
    return None  # Return None if no match is found

def get_all_price_cols(exchange_list: List[ExchangeAbstractClass]) -> List[str]:
    price_cols = []
    for exchange in exchange_list:
        price_cols.append(exchange.price_col)
    return price_cols



