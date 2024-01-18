import http.client
import json

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
