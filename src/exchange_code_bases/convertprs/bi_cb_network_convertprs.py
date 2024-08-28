import pandas as pd

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys, BinanceAPIKeysHFT01
from src.exchange_arbitrage_pkg.broker_config.preferred_networks import General_Preferred_Networks
from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_symbol_utils import get_base_currency_bi_cb
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange
from src.exchange_code_bases.advance_trade.crypto_network_cb.cb_network_extraction import \
    process_response_with_dataframe
from src.exchange_code_bases.binance_enhanced.crypto_network_binance.binance_network_extractor import \
    extract_networks_binance
from src.exchange_code_bases.exchange_class.binance_exchange import BinanceExchange


def create_network_mapper(df_binance, df_coinbase, general_preferred_networks,
                          bi_network_col='network_coin', cb_network_col='crypto'):
    # Convert General_Preferred_Networks to DataFrame
    preferred_df = pd.DataFrame(general_preferred_networks)

    # Step 1: Merge DataFrames based on network names
    mg_df = pd.merge(df_coinbase, df_binance, left_on=cb_network_col, right_on=bi_network_col, how='inner')

    def network_mapper(crypto, network_name):
        if "USD" in crypto.upper():
            crypto = get_base_currency_bi_cb(crypto)
        # Check in General_Preferred_Networks first
        preferred_network = preferred_df.loc[preferred_df['id'].str.upper() == crypto.upper(), 'network_id']
        if not preferred_network.empty:
            return preferred_network.iloc[0]

        # If not found, check in merged DataFrame
        filtered = mg_df[(mg_df[cb_network_col].str.upper() == crypto.upper()) &
                     (mg_df['network_id'].str.lower() == network_name.lower())]
        if filtered.empty:
            return 'Network not found'
        elif len(filtered) > 1:
            seek = filtered[filtered['network_isDefault']]['network_network'].values
            return seek[0] if seek.size > 0 else 'Network not found'
        else:
            return filtered['network_network'].values[0]

    return network_mapper, mg_df


# def create_network_mapper_function(binance_client, coinbase_client):
#     df_binance, unique_networks_bi, coin_network_mapping_bi = extract_networks_binance(binance_client)
#     res = coinbase_client.fetch_supported_networks()
#     df_coinbase, unique_networks_cb, crypto_network_mapping_cb = process_response_with_dataframe(res)
#     mapper = create_network_mapper(df_binance, df_coinbase, General_Preferred_Networks)
#     return mapper


class BiCbNetworkConvertor:
    def __init__(self, binance_exchange, coinbase_exchange, paired_cols=None):
        self.binance_client = binance_exchange.sync_client.client
        self.coinbase_client = coinbase_exchange.sync_client
        self.df_binance, self.unique_networks_bi, self.coin_network_mapping_bi = extract_networks_binance(
            self.binance_client)
        res = self.coinbase_client.fetch_supported_networks()
        self.df_coinbase, self.unique_networks_cb, self.crypto_network_mapping_cb = process_response_with_dataframe(res)
        self.mapper, self.pair_df = create_network_mapper(self.df_binance, self.df_coinbase, General_Preferred_Networks)
        # ToDo: Ceck the newtro_is_default column. See if a default is the one acceptable on coinbase
        self.paired_cols = {'coin_id_col': 'coin_coin',
                            'network_name_col': 'network_network',
                            'net_multiple_int_col': 'network_withdrawIntegerMultiple',
                            'net_withdraw_max_col': 'network_withdrawMax',
                            'net_withdraw_min_col': 'network_withdrawMin',
                            'net_withdraw_fee_col': 'network_withdrawFee',
                            'net_is_default_col': 'network_isDefault'}

    def convert(self, crypto, network_name):
        return self.mapper(crypto, network_name)


if __name__ == '__main__':
    binance_exchange = BinanceExchange(BinanceAPIKeysHFT01())
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
    bi_cb_convertor = BiCbNetworkConvertor(binance_exchange, coinbase_exchange)
    # res = bi_cb_convertor.convert(crypto='BTC', network_name='bitcoin')
    # print(res)

    crypto = 'OGN'
    network_name = 'ethereum'
    res = bi_cb_convertor.convert(crypto=crypto,
                                  network_name=network_name)
    print(res)
