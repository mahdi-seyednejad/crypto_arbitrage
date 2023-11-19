import asyncio

from typing import List

from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_class_pkg.exchange_class import ExchangeMachine
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_helpers import execute_binance_trade, \
    execute_coinbase_trade

class TradeRunner:
    def __init__(self,
                 exchange_machines: List[ExchangeMachine],
                 debug: bool):
        self.exchange_machines = exchange_machines
        self.debug = debug

    async def run_all_trades(self):
        for machine in self.exchange_machines:
            arbitrage_trade = machine.create_arbitrage_function()
            # Example usage, you would replace 'symbol' and 'quantity' with actual values
            await arbitrage_trade(self.debug)

    def execute(self):
        asyncio.run(self.run_all_trades())

# class TradeRunner:
#     def __init__(self,
#                  exchange_machines: List[ExchangeMachine],
#                  debug: bool):
#         self.exchange_machines = exchange_machines
#         # self.client = client
#         self.debug = debug
#
#     async def execute_trade(self, trade):
#         print(f"Preparing to execute {trade.trade_type} trade for {trade.symbol} on {trade.exchange_platform}")
#
#         if trade.exchange_platform == ExchangeNames.Binance:
#             await execute_binance_trade(trade, self.debug)
#         elif trade.exchange_platform == ExchangeNames.Coinbase:
#             await execute_coinbase_trade(trade, self.debug)
#         else:
#             print(f"Unsupported exchange platform: {trade.exchange_platform}")
#
#
#     #ToDO: This is the part that we should control the flow of difefrent instruction for trades:
#     # 1. check balance
#     # 2. buy: Based on the quantity suggested, we should buy if we do not have it.
#     # 4. deposit: Get the deposite address
#     # 3. withdraw: withdraw to the deposite address
#     #
#     async def run_trades_for_machine(self, exchange_machine):
#         for trade in exchange_machine.trade_list:
#             await self.execute_trade(trade)
#
#     async def run_all_trades(self):
#         tasks = [self.run_trades_for_machine(machine) for machine in self.exchange_machines]
#         await asyncio.gather(*tasks)
#
#     def execute(self):
#         asyncio.run(self.run_all_trades())
