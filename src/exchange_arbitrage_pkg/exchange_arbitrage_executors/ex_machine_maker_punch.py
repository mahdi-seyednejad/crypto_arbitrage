from src.exchange_arbitrage_pkg.exchange_arbitrage_core_pkg.exchange_machine_pkg.exchange_machine_double import \
    ArbitrageMachinePunches
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.ex_machine_maker import ArbitrageMachineMaker
from src.exchange_arbitrage_pkg.trade_runner_package.trade_runner_base import TradeRunner


class ArbitrageMachineMakerPunch(ArbitrageMachineMaker):

    def get_arbit_machine_seller_FIRST(self, row):
        # The seller (the first exchange) will be the destination exchange
        src_exchange = self.exchange_pair.get_second_exchange()
        (secondary_symbol, sec_symbol_price) = self.best_sell_symbols_ex_2[-1] # Who is the higher price/gain symbol on the second exchange?
        return ArbitrageMachinePunches(name=self.exchange_pair.name_first_seller,
                                       src_exchange_platform=src_exchange,
                                       dst_exchange_platform=self.exchange_pair.get_first_exchange(),
                                       row=row,
                                       col_info_obj=self.col_info_obj,
                                       ex_price_cols=self.exchange_pair.get_all_price_cols(),
                                       budget=self.get_assigned_allowed_budget(src_exchange, row),
                                       min_acceptable_budget=self.trade_hy_params_obj.min_acceptable_budget,
                                       secondary_symbol=secondary_symbol,
                                       secondary_symbol_price=sec_symbol_price,
                                       debug=self.debug)

    def get_arbit_machine_seller_SECOND(self, row):
        # The seller (the second exchange) will be the destination exchange
        src_exchange = self.exchange_pair.get_first_exchange()
        (secondary_symbol, sec_symbol_price) = self.best_sell_symbols_ex_1[-1] # Who is the higher price/gain symbol on the first exchange?
        return ArbitrageMachinePunches(name=self.exchange_pair.name_second_seller,
                                       src_exchange_platform=self.exchange_pair.get_first_exchange(),
                                       dst_exchange_platform=self.exchange_pair.get_second_exchange(),
                                       row=row,
                                       col_info_obj=self.col_info_obj,
                                       budget=self.get_assigned_allowed_budget(src_exchange, row),
                                       min_acceptable_budget=self.trade_hy_params_obj.min_acceptable_budget,
                                       ex_price_cols=self.exchange_pair.get_all_price_cols(),
                                       secondary_symbol=secondary_symbol,
                                       secondary_symbol_price=sec_symbol_price,
                                       debug=self.debug)
