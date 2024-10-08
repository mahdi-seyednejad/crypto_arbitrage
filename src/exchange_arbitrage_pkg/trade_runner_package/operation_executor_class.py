from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_symbol_utils import get_base_currency_binance
from src.exchange_arbitrage_pkg.broker_utils.binance_utils.binance_trade_codes import buy_binance, sell_binance, \
    get_deposit_address_binance, check_balance_binance, withdraw_binance
from src.exchange_code_bases.advance_trade.coinbase_utils.coinbase_trade_code import check_balance_coinbase, \
    buy_sell_coinbase, withdraw_coinbase, get_deposit_address_coinbase
from src.exchange_arbitrage_pkg.utils.binance_coinbase_convertor import convert__symbol_bi_to_cb
from src.exchange_code_bases.convertprs.bi_cb_network_convertprs import BiCbNetworkConvertor


class OperationExecutor:
    def __init__(self, first_exchange, second_exchange, debug=False):
        self.debug = debug
        self.network_convertor_obj = BiCbNetworkConvertor(first_exchange, second_exchange)

    async def execute_trade(self, trade, debug):
        if debug:
            print("In the execute_trade function")
            print(f"-- Executing trade: {trade}")
        if trade.exchange_platform.name == ExchangeNames.Binance:
            binance_client = await trade.exchange_platform.create_async_client()
            result = await self.execute_binance_trade(binance_client, trade, debug)
        elif trade.exchange_platform.name == ExchangeNames.Coinbase:
            coinbase_client = await trade.exchange_platform.create_async_client()
            result = await self.execute_coinbase_trade(coinbase_client, trade, debug)
        else:
            print(f"Unsupported exchange platform: {trade.exchange_platform}")
            result = None

        return result

    async def execute_binance_trade(self, binance_async_client, trade, debug):
        # binance_async_client = await trade.exchange_platform.create_async_client()
        if trade.trade_type == 'check':
            result = await check_balance_binance(binance_async_client, get_base_currency_binance(trade.symbol))
        elif trade.trade_type == 'withdraw':
            converted_network = self.network_convertor_obj.convert(crypto=trade.symbol,
                                                                   network_name=trade.network)
            result = await withdraw_binance(binance_async_client, trade.symbol, trade.quantity, trade.address,
                                            converted_network,
                                            debug=debug)
        elif trade.trade_type == 'buy':
            result = await buy_binance(binance_async_client, trade.symbol, trade.quantity, trade.price, debug)
        elif trade.trade_type == 'sell':
            result = await sell_binance(binance_async_client, trade.symbol, trade.quantity, trade.price, debug)
        elif trade.trade_type == 'deposit':
            result = await get_deposit_address_binance(binance_async_client, trade.symbol, debug)
        else:
            print(f"Unsupported trade type: {trade.trade_type}")
            result = None
        return result

    async def execute_coinbase_trade(self, coinbase_async_client, trade, debug):
        # coinbase_async_client = await trade.exchange_platform.create_async_client()
        symbol = convert__symbol_bi_to_cb(trade.symbol)
        if trade.trade_type == 'check':
            result = await check_balance_coinbase(coinbase_async_client, symbol)
        elif trade.trade_type == 'withdraw':
            result = await withdraw_coinbase(coinbase_async_client, symbol, trade.quantity, trade.address)
        elif trade.trade_type in ['buy', 'sell']:
            result = await buy_sell_coinbase(client=coinbase_async_client,
                                             symbol=symbol,
                                             side=trade.side,
                                             quantity=trade.quantity,
                                             price=trade.price,
                                             debug=debug)
        elif trade.trade_type == 'deposit':
            result = await get_deposit_address_coinbase(coinbase_async_client, symbol)
        else:
            print(f"Unsupported trade type: {trade.trade_type}")
            result = None
        return result

# ToDO: #IDEA: We could consider each operation as an agent or object.
#  Then we could have a class for each operation type, and each class could have a function to execute the operation.
#  For example, we will have a "buy" object. It goes and buys. Based on the exchange,
#  it will have a function to buy on that exchange.
