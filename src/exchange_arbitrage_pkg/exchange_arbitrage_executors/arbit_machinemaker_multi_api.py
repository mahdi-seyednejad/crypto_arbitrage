from src.data_pkg.ts_db.ts_db_handler import DbHandler
from src.exchange_arbitrage_pkg.exchange_arbitrage_executors.arbit_machine_maker_punch import ArbitrageMachineMakerPunch
from src.exchange_arbitrage_pkg.utils.column_type_class import ColumnInfoClass
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter
from src.exchange_code_bases.exchange_class.exchange_pair_class import ExchangePair
from src.exchange_code_bases.exchange_class.exchange_pair_multi_api import CollectableExPair


class ArbitMachineMakerMultiApi(ArbitrageMachineMakerPunch):
    #ToDo: make this one and use the exchange pair
    def __init__(self,
                 exchange_pair_collection: CollectableExPair,
                 col_info_obj: ColumnInfoClass,
                 trade_hy_params_obj: TradeHyperParameter,
                 db_handler: DbHandler,
                 debug: bool):
        super().__init__(exchange_pair=exchange_pair_collection.get_next_exchange_pair(),
                         col_info_obj=col_info_obj,
                         trade_hy_params_obj=trade_hy_params_obj,
                         db_handler=db_handler,
                         debug=debug)
        exchange_pair_collection.set_all_budgets(self.trade_hy_params_obj.initial_budget)
        self.exchange_pair_collection = exchange_pair_collection

    def _get_ex_pair(self):
        return self.exchange_pair_collection.get_next_exchange_pair()




