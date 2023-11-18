from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.arbitrage_plan_func import create_arbitrage_plan
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_base import TradeRunner


class ArbitrageExecutor:

    def create_exchange_machines(self, df_in):
        return create_arbitrage_plan(df_in)

    def execute_exchange_machines(self, exchange_machines):
        trade_runner = TradeRunner(exchange_machines)
        trade_runner.execute()

    def execute_from_df(self, df_in):
        exchange_machines = self.create_exchange_machines(df_in)
        self.execute_exchange_machines(exchange_machines)


