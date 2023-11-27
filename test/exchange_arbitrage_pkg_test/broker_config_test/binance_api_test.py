from binance.client import AsyncClient, Client
import pytest_asyncio

from src.exchange_arbitrage_pkg.broker_config.exchange_api_info import BinanceAPIKeys

Binance_API_Obj = BinanceAPIKeys()


def test_api_key_sync():
    client = Client(Binance_API_Obj.api_key,
                    Binance_API_Obj.secret_key,
                    testnet=False,
                    tld="us", )
    # Example test: Fetching the server time
    server_time = client.get_server_time()
    print("Server time:", server_time)
    assert 'serverTime' in server_time

    # Close the client after testing
    client.close_connection()


async def test_api_key():
    client = await AsyncClient.create(Binance_API_Obj.api_key,
                                      Binance_API_Obj.secret_key,
                                      testnet=False,
                                      tld="us", )
    try:
        time = await client.get_server_time()
        print("API key is valid. Server time:", time)
    except Exception as e:
        print("Error with API key:", e)
    finally:
        await client.close()
