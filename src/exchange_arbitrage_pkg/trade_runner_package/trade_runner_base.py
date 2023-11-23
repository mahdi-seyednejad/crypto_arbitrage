import asyncio
from typing import List

from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_class_pkg.exchange_class import ExchangeMachine


class TradeRunner:
    def __init__(self,
                 exchange_machines: List[ExchangeMachine],
                 debug: bool):
        self.exchange_machines = exchange_machines
        self.debug = debug

    async def run_all_trades(self):
        tasks = []
        for ex_machine in self.exchange_machines:
            arbitrage_trade = ex_machine.create_arbitrage_function()
            # Example usage, you would replace 'symbol' and 'quantity' with actual values
            tasks.append(asyncio.create_task(arbitrage_trade(self.debug)))
        # Run tasks concurrently
        await asyncio.gather(*tasks)

    async def execute(self):
        await self.run_all_trades()
