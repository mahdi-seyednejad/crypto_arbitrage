import pandas as pd

def create_asset_dataframe(data):
    asset_data = []
    for asset in data:
        try:
            asset_info = {
                'Asset ID': asset.get('id', None),
                'Name': asset.get('name', None),
                'Type': asset.get('currency', {}).get('type', None),
                'Amount': float(asset['balance'].get('amount', 0))
            }
            asset_data.append(asset_info)
        except (KeyError, TypeError):
            pass  # Skip this asset if the structure is not as expected

    return pd.DataFrame(asset_data)


def get_available_amount(data, asset_name):
    for asset in data:
        if asset['name'] == asset_name:
            return float(asset['balance']['amount'])
    return None  # If the asset name is not found


def calculate_available_budget(data):
    total_budget = sum(float(asset['balance']['amount']) for asset in data)
    return total_budget

