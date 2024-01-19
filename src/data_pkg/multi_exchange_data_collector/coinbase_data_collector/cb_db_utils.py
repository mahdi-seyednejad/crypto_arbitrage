import http.client
import json
import random


def get_all_crypto_pairs():
    conn = http.client.HTTPSConnection("api.exchange.coinbase.com")
    payload = ''
    headers = {
        'Content-Type': 'application/json',
    'User-Agent': 'Python http.client'  # Add a User-Agent header

    }
    conn.request("GET", "/products", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data_decoded = data.decode("utf-8")
    print(data_decoded)
    # Convert the JSON string to a Python object (list of dicts)
    data_list = json.loads(data_decoded)

    # Write the data to a JSON file
    with open('coinbase_data.json', 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)


# Define a custom backoff generator
def random_backoff_generator(min_seconds, max_seconds):
    def f():
        while True:
            yield random.randint(min_seconds, max_seconds)
    return f


def truncate_timestamp(timestamp):
    """ Truncate the fractional seconds in the timestamp to six decimal places. """
    if '.' in timestamp:
        main_part, fractional_part = timestamp.split('.')
        fractional_part = fractional_part[:6]  # Keep only six decimal places
        return f'{main_part}.{fractional_part}'
    return timestamp
