from pandas import json_normalize


from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import CoinbaseAPIKeys
from src.exchange_code_bases.exchange_class.advance_trade_exchange import AdvanceTradeExchange


def process_coinbase_network(response):
    unique_networks = set()
    crypto_network_mapping = {}

    for currency in response:
        # Extracting the crypto name and its supported networks
        crypto_name = currency['id']
        networks = currency.get('supported_networks', [])

        # Initialize a set for each crypto
        crypto_networks = set()

        for network in networks:
            network_name = network['id']
            unique_networks.add(network_name)
            crypto_networks.add(network_name)

        # Assign the set of networks to the crypto in the dictionary
        crypto_network_mapping[crypto_name] = crypto_networks

    return unique_networks, crypto_network_mapping


def process_response_with_dataframe(response):
    # Normalize the JSON response to a flat table
    df = json_normalize(response, 'supported_networks', ['id'],
                        record_prefix='network_', meta_prefix='crypto_')

    # Renaming the columns for clarity
    df.rename(columns={'crypto_id': 'crypto'}, inplace=True)

    # Extracting unique networks and crypto-network mapping
    unique_networks = set(df['network_id'].unique())
    crypto_network_mapping = df.groupby('crypto')['network_id'].apply(set).to_dict()

    return df, unique_networks, crypto_network_mapping


if __name__ == '__main__':
    coinbase_exchange = AdvanceTradeExchange(CoinbaseAPIKeys())
    res = coinbase_exchange.sync_client.fetch_supported_networks()

    df, unique_networks, crypto_network_mapping = process_response_with_dataframe(res)
    # unique_networks, crypto_network_mapping = process_coinbase_network(res)
    print(crypto_network_mapping)

