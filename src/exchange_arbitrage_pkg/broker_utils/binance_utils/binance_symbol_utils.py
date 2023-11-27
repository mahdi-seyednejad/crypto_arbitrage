from src.exchange_arbitrage_pkg.broker_config.binance_constants import Binance_Quote_Currencies


def get_base_currency_binance(pair):
    for quote_currency in Binance_Quote_Currencies:
        if pair.endswith(quote_currency):
            return pair[:-len(quote_currency)]
    return None  # or raise an exception if the pair is not recognized
