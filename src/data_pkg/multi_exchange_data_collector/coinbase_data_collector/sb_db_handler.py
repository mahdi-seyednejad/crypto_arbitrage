from src.data_pkg.ts_db.time_scale_db_operations import TimeScaleClass


class DbHandler:
    def __init__(self,
                 time_column: str):
        self.ts_obj: TimeScaleClass = TimeScaleClass()
        self.time_column = time_column

    def insert_stream_order_book_dict(self, data_dict):
        self.ts_obj.insert_orbk_dict_to_tsdb(data_dict=data_dict,
                                             table_name='stream_order_book',
                                             time_key='timestamp',
                                             out_time_column='utc_time',
                                             symbol_col='product_id',
                                             side_col='side',
                                             debug=True)
