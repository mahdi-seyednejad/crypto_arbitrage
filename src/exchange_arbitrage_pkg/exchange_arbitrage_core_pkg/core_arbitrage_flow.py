# def arbitrage_workflow(df_diff_info_in, binance_client, coinbase_client):
#     df = df_diff_info_in.copy()
#     opportunities = find_arbitrage_opportunities(df, 'symbol', 'binance_price', 'coinbase_price')
#
#     binance_exchange = Exchange('binance', binance_client)
#     coinbase_exchange = Exchange('coinbase', coinbase_client)
#
#     for symbol in opportunities:
#         # Define your logic here to decide on the trades
#         # Example:
#         # trade = Trade('market', symbol, 'buy', quantity)
#         # binance_exchange.add_trade(trade)
#         # ...
#
#     return binance_exchange, coinbase_exchange
