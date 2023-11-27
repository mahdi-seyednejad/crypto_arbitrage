import requests
import pandas as pd


def fetch_account_info_to_dataframe(url, auth):
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        data = response.json().get('data', [])
        # Flatten the nested JSON structure
        df = pd.json_normalize(data)
        return df
    else:
        # Handle error or return an empty DataFrame
        print(f"Error fetching account info: {response.text}")
        return pd.DataFrame()
