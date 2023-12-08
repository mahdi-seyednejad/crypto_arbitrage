
import pandas as pd
import cbpro


def get_latest_price(product_id, public_client):
    try:
        ticker = public_client.get_product_ticker(product_id=product_id)
        return float(ticker['price'])
    except Exception as e:
        return None


def get_latest_prices_coinbase_at(coinbase_client, sample_size):
    # public_client = cbpro.PublicClient()
    products = coinbase_client.get_products()

    # Convert to DataFrame
    df_products = pd.DataFrame(products)

    if sample_size:
        df_products = df_products.sample(sample_size)

    # Fetch and add prices
    df_products['price'] = df_products['id'].apply(lambda x: get_latest_price(x, coinbase_client))

    return df_products


def get_order_book_coinbase(coinbase_client, product_id, depth):
    """
    Fetches the order book for a given product from Coinbase Pro.

    :param coinbase_client: The Coinbase Pro client instance.
    :param product_id: The ID of the product (e.g., 'BTC-USD') to fetch the order book for.
    :param depth: The level of detail for the order book (1, 2, or 3).
    :return: A DataFrame containing the order book.
    """
    # Fetch the order book
    order_book = coinbase_client.fetch_order_book(product_id, level=depth)

    # Convert the order book to DataFrame
    if depth in [1, 2]:
        # For level 1 and 2, the order book contains bids and asks
        df_bids = pd.DataFrame(order_book['bids'], columns=['price', 'size', 'num_orders'])
        df_bids['side'] = 'bid'
        df_asks = pd.DataFrame(order_book['asks'], columns=['price', 'size', 'num_orders'])
        df_asks['side'] = 'ask'

        df_order_book = pd.concat([df_bids, df_asks])
    else:
        # Level 3 contains more detailed information
        df_order_book = pd.DataFrame(order_book)

    # Convert price and size to numeric
    df_order_book['price'] = pd.to_numeric(df_order_book['price'])
    df_order_book['size'] = pd.to_numeric(df_order_book['size'])

    return df_order_book

