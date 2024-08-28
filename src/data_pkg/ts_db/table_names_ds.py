

class TableNames:
    def __init__(self,
                 stream_diff_table: str = "diff_data_stream",
                 agg_diff_table: str = "diff_data_agg",
                 evaluated_symbols_table: str = "evaluated_symbols",
                 order_book_table: str = "order_books"):
        self.stream_diff_table = stream_diff_table
        self.agg_diff_table = agg_diff_table
        self.evaluated_symbols_table = evaluated_symbols_table
        self.order_book_table = order_book_table

    def get_stream_table_name(self):
        return self.stream_diff_table

    def get_agg_table_name(self):
        return self.agg_diff_table

    def get_evaluated_symbols_table_name(self):
        return self.evaluated_symbols_table

    def get_order_book_table_name(self):
        return self.order_book_table


