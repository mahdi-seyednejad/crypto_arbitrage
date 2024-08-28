# import requests
#
#
# def fetch_withdrawal_fees(self):
#     url = f'{self.base_url}/[withdrawal_fees_endpoint]'  # Replace with the actual endpoint
#     try:
#         response = requests.get(url, auth=self.auth)
#         if response.status_code == 200:
#             fees_data = response.json()
#             # Process the fees_data as required
#             return fees_data
#         else:
#             # Handle error response
#             print(f"Error fetching withdrawal fees: {response.json()}")
#             return None
#     except Exception as e:
#         print(f"Error fetching withdrawal fees from Coinbase: {e}")
#         return None
#
