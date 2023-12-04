import socket

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeysHFT01

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only



from binance.client import Client
from binance.exceptions import BinanceAPIException


def process_coins_info(coins_info):
    unique_networks = set()
    coin_network_mapping = {}

    for coin_info in coins_info:
        coin_name = coin_info['name']
        network_list = coin_info['networkList']

        # Prepare the dictionary of networks for the current coin
        networks_for_coin = {}

        for network_info in network_list:
            network = network_info['network']
            network_name = network_info.get('name', network)  # Use 'network' as the name if 'name' is not available

            # Add to the set of unique networks
            unique_networks.add(network)

            # Update the dictionary of networks for the current coin
            networks_for_coin[network] = network_name

        # Update the mapping dictionary
        coin_network_mapping[coin_name] = networks_for_coin

    return unique_networks, coin_network_mapping


def can_withdraw(api_key, api_secret, coin):
    client = Client(api_key, api_secret, tld='us', testnet=False)

    try:
        # Fetch account information
        account_info = client.get_account()

        all_coins_info = client.get_all_coins_info()

        # Example usage
        unique_networks, coin_network_mapping = process_coins_info(all_coins_info)

        print("Unique Networks:", unique_networks)
        print("Coin Network Mapping:", coin_network_mapping)

        # # The account information contains a list of all assets
        # for asset in account_info['balances']:
        #     if asset['asset'] == coin:
        #         # Check if withdrawals are enabled for this asset
        #         return asset['withdrawEnabled']

        # If the coin is not found in the account info
        return False

    except BinanceAPIException as e:
        # Handle potential exceptions
        print(f"Binance API Exception occurred: {e}")
        return False

if __name__ == '__main__':
    coin = 'BTC'  # Example coin symbol
    binance_api = BinanceAPIKeysHFT01()
    can_withdraw_status = can_withdraw(binance_api.api_key,
                                       binance_api.secret_key,
                                       coin)
    print(f"Can withdraw {coin}: {can_withdraw_status}")

