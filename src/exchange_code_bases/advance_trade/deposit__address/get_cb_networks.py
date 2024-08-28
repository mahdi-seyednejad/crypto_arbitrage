import coinbase
import binance

coinbase_client = coinbase.Client()
binance_client = binance.Client()

# Get Coinbase networks
coinbase_networks = coinbase_client.get_payment_methods()

# Get Binance networks
binance_networks = binance_client.get_deposit_addresses()

# Map Coinbase to Binance
network_map = {
    "Ethereum": "ERC20",
    "Bitcoin": "BTC",
    "Litecoin": "LTC",
}

# Find matching Coinbase address
for coinbase_network in coinbase_networks:
    if coinbase_network['network'] in network_map:
        binance_network = network_map[coinbase_network['network']]

        # Get Binance address for this network
        binance_addr = binance_networks[binance_network][0]['address']

        print(
            f"Deposit {coinbase_network['crypto']['name']} on Binance at address {binance_addr} using {binance_network} network")