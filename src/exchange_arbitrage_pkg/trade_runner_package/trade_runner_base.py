import asyncio
from typing import List

from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_machine_pkg.arbitrage_machine_double import \
    ArbitrageMachinePunches


class TradeRunner:
    def __init__(self,
                 exchange_machines: List[ArbitrageMachinePunches],
                 debug: bool):
        self.exchange_machines = exchange_machines
        self.debug = debug

    async def run_all_trades(self):
        tasks = []
        for ex_machine in self.exchange_machines:
            try:
                arbitrage_trade = ex_machine.create_arbitrage_function()
                # Example usage, you would replace 'symbol' and 'quantity' with actual values
                task = asyncio.create_task(arbitrage_trade())
                tasks.append(task)
            except Exception as e:
                print(f"Error setting up trade for {ex_machine.name}: {e}")

        # Run tasks concurrently and handle exceptions
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f"An error occurred during trading: {result}")

    async def execute(self):
        try:
            await self.run_all_trades()
        except Exception as e:
            print(f"An error occurred in execute: {e}")

    # async def run_all_trades(self):
    #     tasks = []
    #     for ex_machine in self.exchange_machines:
    #         arbitrage_trade = ex_machine.create_arbitrage_function()
    #         # Example usage, you would replace 'symbol' and 'quantity' with actual values
    #         tasks.append(asyncio.create_task(arbitrage_trade()))
    #     # Run tasks concurrently
    #     await asyncio.gather(*tasks)
    #
    # async def execute(self):
    #     await self.run_all_trades()
