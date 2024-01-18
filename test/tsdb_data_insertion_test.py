import pandas as pd

from src.data_pkg.ts_db.time_scale_db_operations import TimeScaleClass

db_obj = TimeScaleClass()
sample_data = [
    {'timestamp': '2023-12-31T03:38:52.642319126Z', 'sequence_num': 0, 'product_id': 'ETH-USDT', 'side': 'bid',
     'price_level': '2280.72', 'new_quantity': '0.1593'},
    {'timestamp': '2023-12-31T03:38:52.642319126Z', 'sequence_num': 0, 'product_id': 'ETH-USDT', 'side': 'bid',
     'price_level': '2280.53', 'new_quantity': '0.41'},
    {'timestamp': '2023-12-31T03:38:52.642319126Z', 'sequence_num': 0, 'product_id': 'ETH-USDT', 'side': 'bid',
     'price_level': '2280.52', 'new_quantity': '0.32890086'},
    {'timestamp': '2023-12-31T03:38:52.642319126Z', 'sequence_num': 0, 'product_id': 'ETH-USDT', 'side': 'bid',
     'price_level': '2280.5', 'new_quantity': '0.3588781'},
    {'timestamp': '2023-12-31T03:38:52.642319126Z', 'sequence_num': 0, 'product_id': 'ETH-USDT', 'side': 'bid',
     'price_level': '2280.48', 'new_quantity': '0.19843'}]


def smoke_test_dict_to_db():
    df = pd.DataFrame(sample_data)

    # Convert data types as necessary
    df['price_level'] = df['price_level'].astype(float)
    df['new_quantity'] = df['new_quantity'].astype(float)
    db_obj.insert_df_to_tsdb(df_in=df,
                             table_name='test_orbk_stream_to_db',
                             time_column='timestamp',
                             date_as_index=False,
                             primary_keys=['product_id'],
                             debug=True)

    # for entry in sample_data:
    #     db_obj.insert_orbk_dict_to_tsdb(
    #         data_dict=entry,
    #         table_name='test_dict_to_db',
    #         time_key='timestamp',
    #         out_time_column='timestamp',
    #         symbol_col='product_id',
    #         side_col='side',
    #         debug=True
    #     )


if __name__ == '__main__':
    smoke_test_dict_to_db()
