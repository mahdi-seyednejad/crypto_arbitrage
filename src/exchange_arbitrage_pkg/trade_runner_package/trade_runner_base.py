import asyncio

from src.exchange_arbitrage_pkg.broker_config.exchange_names import ExchangeNames
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_helpers import execute_binance_trade, \
    execute_coinbase_trade


class TradeRunner:
    def __init__(self, exchange_machines, client, debug):
        self.exchange_machines = exchange_machines
        self.client = client
        self.debug = debug

    async def execute_trade(self, trade):
        print(f"Preparing to execute {trade.trade_type} trade for {trade.symbol} on {trade.exchange_platform}")

        if trade.exchange_platform == ExchangeNames.Binance:
            await execute_binance_trade(self.client, trade, self.debug)
        elif trade.exchange_platform == ExchangeNames.Coinbase:
            await execute_coinbase_trade(self.client, trade, self.debug)
        else:
            print(f"Unsupported exchange platform: {trade.exchange_platform}")

    async def run_trades_for_machine(self, exchange_machine):
        for trade in exchange_machine.trade_pairs:
            await self.execute_trade(trade)

    async def run_all_trades(self):
        tasks = [self.run_trades_for_machine(machine) for machine in self.exchange_machines]
        await asyncio.gather(*tasks)

    def execute(self):
        asyncio.run(self.run_all_trades())
