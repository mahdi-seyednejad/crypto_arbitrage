from src.exchange_arbitrage_pkg.broker_config.binance_constants import Binance_Quote_Currencies
from src.exchange_code_bases.advance_trade.coinbase_utils.coinbase_symbol_utils import get_base_from_pair_coinbase


def get_base_currency_binance(pair):
    for quote_currency in Binance_Quote_Currencies:
        if pair.endswith(quote_currency):
            return pair[:-len(quote_currency)]
    return None  # or raise an exception if the pair is not recognized


def get_base_currency_bi_cb(pair):
    if "-" in pair:
        return get_base_from_pair_coinbase(pair)
    else:
        return get_base_currency_binance(pair)