from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine_double import \
    ArbitrageMachinePunches
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.ex_machine_maker import ArbitrageMachineMaker


class ArbitrageMachineMakerPunch(ArbitrageMachineMaker):

    def get_best_positive_symbol(self, df_pos):
        # We need the best positive symbol from the first exchange.
        first_exchange_price_col = self.exchange_list[0].price_col  # ToDo FIx this.
        best = df_pos[df_pos[first_exchange_price_col] == df_pos[first_exchange_price_col].max()].iloc[0].values[0]
        return best -> Get the symbol and their price

    def get_best_negative_symbol(self, df_neg):
        second_exchange_price_col = self.exchange_list[1].price_col
        best = df_neg[df_neg[second_exchange_price_col] == df_neg[second_exchange_price_col].max()].iloc[0].values[0]
        return best




    def _create_arbitrage_machines_punch(self, df_pos, df_neg):
        arbitrage_machines = []
        arbitrage_machine = None
        best_positive_symbol = self.get_best_positive_symbol(df_pos)
        best_negative_symbol = self.get_best_negative_symbol(df_neg)

        exchange_machines = []
        for index, row in df.iterrows():
            if row[self.col_info_obj.price_diff_col] > 0:
                arbitrage_machine = ArbitrageMachinePunches(name="Coinbase_to_Binance",
                                                            src_exchange_platform=src_exchange,
                                                            dst_exchange_platform=self._get_exchange(
                                                                ExchangeNames.Binance),
                                                            row=row,
                                                            col_info_obj=self.col_info_obj,
                                                            budget=self.get_assigned_allowed_budget(available_budget,
                                                                                                    row),
                                                            secondary_symbol=self.secondary_symbol,
                                                            secondary_symbol_price=self.secondary_symbol_price,
                                                            debug=self.debug)
            elif row[self.col_info_obj.price_diff_col] < 0:



