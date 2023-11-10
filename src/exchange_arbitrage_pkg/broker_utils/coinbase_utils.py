import logging
import cbpro


# def get_latest_prices_coinbase_pro():
#     public_client = cbpro.PublicClient()
#     products = public_client.get_products()
#     prices = {}
#
#     for product in products:
#         try:
#             ticker = public_client.get_product_ticker(product_id=product['id'])
#             prices[product['id']] = float(ticker['price'])
#         except Exception as e:
#             # Check for specific error message
#             if str(e) == "{'message': 'Not allowed for delisted products'}":
#                 # Optionally, log that the product is delisted
#                 logging.info(f"Product {product['id']} is delisted.")
#                 continue
#             else:
#                 # Log unexpected errors
#                 logging.error(f"Error fetching data for {product['id']}: {e}")
#         # Optionally, you can add more code here to handle other scenarios
#
#     return prices
import pandas as pd
import cbpro


def get_latest_price(product_id, public_client):
    try:
        ticker = public_client.get_product_ticker(product_id=product_id)
        return float(ticker['price'])
    except Exception as e:
        return None
        # if "delisted products" in str(e):
        #     return None  # or np.nan
        # else:
        #     raise


def get_latest_prices_coinbase_pro(sample_size=None):
    public_client = cbpro.PublicClient()
    products = public_client.get_products()

    # Convert to DataFrame
    df_products = pd.DataFrame(products)

    if sample_size:
        df_products = df_products.sample(sample_size)

    # Fetch and add prices
    df_products['price'] = df_products['id'].apply(lambda x: get_latest_price(x, public_client))

    return df_products

#
# def get_latest_prices_coinbase_pro():
#     public_client = cbpro.PublicClient()
#     products = public_client.get_products()
#
#     # Using list comprehension to gather data
#     data = []
#     for product in products:
#         try:
#             ticker = public_client.get_product_ticker(product_id=product['id'])
#             data.append({'id': product['id'], 'price': float(ticker['price'])})
#         except Exception as e:
#             # Handle specific error or general errors
#             if str(e) == "{'message': 'Not allowed for delisted products'}":
#                 continue
#             else:
#                 print(f"Error fetching data for {product['id']}: {e}")
#
#     # Creating DataFrame
#     df = pd.DataFrame(data)
#
#     return df
