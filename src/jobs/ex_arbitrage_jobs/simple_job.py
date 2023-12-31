##########   Force to use IPv4   #########
import socket

# Store the original getaddrinfo to restore later if needed
original_getaddrinfo = socket.getaddrinfo


def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


# Monkey patch the socket module
socket.getaddrinfo = getaddrinfo_ipv4_only
##########################################

import asyncio

from src.data_pkg.ts_db.table_names_ds import TableNames
from src.exchange_arbitrage_pkg.utils.hyper_parameters.trade_hyper_parameter_class import TradeHyperParameter, \
    WaitTimeDeposit
from src.pipelines.exchange_arbitrage_pipeline.simple_pipeline import SimplePipeline


def main_job():
    DEBUG = True
    Sample_Size = None  # Just for testing

    waite_time_obj = WaitTimeDeposit(check_interval=10,  # Get this to the punches
                                     timeout=800,
                                     amount_loss=0.05,
                                     second_chance=True)

    tr_hype_param = TradeHyperParameter(trade_bucket_size=20,
                                        order_book_fetch_level=100,
                                        acceptable_slippage=0.5,
                                        price_range_percent=0.5,
                                        initial_budget=None,
                                        outlier_threshold=2.1,
                                        fetch_period=30,
                                        run_number=10,
                                        num_of_top_symbols=2,
                                        budget_factor=0.7,
                                        acceptable_amount_diff_percent=0.5,
                                        min_acceptable_budget=10,
                                        secondary_symbol_rank=2,
                                        num_rank_hard_cut_off=3,
                                        wait_time_deposit=waite_time_obj)

    my_table_names = TableNames()

    pipeline = SimplePipeline(trade_hyper_parameters=tr_hype_param,
                              sample_size=Sample_Size,
                              storage_dir=None,
                              table_names=my_table_names,
                              debug=DEBUG)

    loop = asyncio.get_event_loop()
    loop.set_debug(DEBUG)
    asyncio.run(pipeline.run())


if __name__ == '__main__':
    main_job()

#ToDo: Check to see why it shows error about not having enough money.
#ToDo: If there is no secondary crypto to move from an exchange to another one,
# then find the crypto that we already have while it has the smallest withdraw fee.
# if we do not have something like that, then, buy and move something that minimizes the lost and withdraw fee.
# OR-> JUST MOVE WITH THETTER --> Kt has 8 dollars fee

