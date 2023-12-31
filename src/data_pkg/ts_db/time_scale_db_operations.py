'''
Postgres docker container:
CREATE TABLE IF NOT EXISTS
        top_gainer_table (
            time TIMESTAMP WITH TIME ZONE NOT NULL,
            symbol TEXT NOT NULL,
            price_change_percent NUMERIC,
            last_price NUMERIC,
            status TEXT);
How to run teh docker:
docker exec -it <dbname> psql -U <username>
in our case:
    docker exec -it timescaledb psql -U postgres
'''
import numpy as np
import psycopg2 as pg
from decouple import config
from psycopg2.extras import execute_batch
from psycopg2 import sql

from src.data_pkg.ts_db.ts_db_utils import get_col_types_sql, guess_type, prepare_dataframe, register_data_adapters, \
    convert_bool_columns, handle_null_values, serialize_complex_types, check_large_text_binary

# from crypto_trade.db_utils.time_scale_db import TimeScaleDB

db_pass = config("DB_PASS_LOCAL")
local_user = config("LOCAL_DB_USER")


class TimeScaleClass:
    def __init__(self):
        self.conn = pg.connect(host="localhost",
                               user=local_user,
                               password=db_pass,
                               dbname="postgres",
                               port=5432)
        self.cur = self.conn.cursor()

    # def _check_or_create_table(self, df, table_name, time_column, symbol_col, debug):
    #     col_types = get_col_types_sql(df)
    #     columns = ', '.join([f"{col.replace(' ', '_')} {col_types[col]}" for col in df.columns])
    #     create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns}, PRIMARY KEY ({time_column}, {symbol_col}))'
    #     if debug:
    #         print(create_table_query)
    #     self.cur.execute(create_table_query)
    #     self.conn.commit()

    def _check_or_create_table(self, df, table_name, time_column, primary_keys=None, debug=False):
        col_types = get_col_types_sql(df)
        columns = ', '.join([f"{col.replace(' ', '_')} {col_types[col]}" for col in df.columns])

        # Ensure time_column is part of primary keys
        if primary_keys is None:
            primary_keys = [time_column]
        elif time_column not in primary_keys:
            primary_keys.append(time_column)

        # Construct primary key clause
        primary_key_clause = ', PRIMARY KEY (' + ', '.join(primary_keys) + ')'

        create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns}{primary_key_clause})'
        if debug:
            print(create_table_query)
        self.cur.execute(create_table_query)
        self.conn.commit()

    # def _insert_data(self, df, table_name, time_column, symbol_col, debug):
    #     # Convert numpy.int32 columns to Python int
    #     for col in df.select_dtypes(include=['int32']).columns:
    #         df[col] = df[col].astype(int)
    #
    #     column_list = [col.replace(' ', '_') for col in df.columns]
    #     query = f"INSERT INTO {table_name} ({', '.join(column_list)}) VALUES ({'%s, ' * (len(column_list) - 1)}%s) ON " \
    #             f"CONFLICT ({time_column}, {symbol_col}) DO NOTHING"
    #     execute_batch(self.cur,
    #                   query,
    #                   [tuple(x) for x in df.to_records(index=False)],
    #                   page_size=1000)
    #     self.conn.commit()

    def _insert_data(self, df, table_name, time_column, primary_keys=None, debug=False):
        # Convert numpy.int32 columns to Python int
        for col in df.select_dtypes(include=['int32']).columns:
            df[col] = df[col].astype(int)

        column_list = [col.replace(' ', '_') for col in df.columns]

        # Ensure time_column is part of primary keys
        if primary_keys is None:
            primary_keys = [time_column]
        elif time_column not in primary_keys:
            primary_keys.append(time_column)

        query = f"INSERT INTO {table_name} ({', '.join(column_list)}) VALUES ({'%s, ' * (len(column_list) - 1)}%s) " \
                f"ON CONFLICT ({', '.join(primary_keys)}) DO NOTHING"

        execute_batch(self.cur,
                      query,
                      [tuple(x) for x in df.to_records(index=False)],
                      page_size=1000)
        self.conn.commit()

        if debug:
            print(query)

    def insert_df_to_tsdb(self, df_in, table_name, time_column, symbol_col, date_as_index, debug,
                          primary_keys=None, need_dt_conversion=True):
        # Pre-processing
        df = prepare_dataframe(df_in, time_column, date_as_index, need_dt_conversion)
        df = handle_null_values(df)
        df = serialize_complex_types(df)
        # df = convert_to_decimal(df, decimal_columns)  # Specify decimal columns if any
        register_data_adapters()

        # Other existing pre-processing
        df = convert_bool_columns(df)  # Assuming this is another function you have

        # Check data integrity, large text/binary, etc.
        # check_data_integrity(df, unique_columns)  # Specify unique columns if any
        check_large_text_binary(df)

        # Now proceed to table creation and data insertion
        self._check_or_create_table(df, table_name, time_column, primary_keys, debug)
        self._insert_data(df, table_name, time_column, primary_keys, debug)

    def insert_single_row_tsdb(self, series, table_name, time_column, symbol, date_as_index, interval, debug=True):
        from psycopg2 import sql

        # Create a DataFrame from the series
        df = series.to_frame().T

        # Add the index (assumed to be the date) as a column
        if date_as_index:
            df[time_column] = df.index.strftime('%Y-%m-%d %H:%M:%S')

        # Convert pandas datatypes to native Python datatypes
        for col, dtype in df.dtypes.items():
            if dtype == np.bool_:
                df[col] = df[col].astype(str)
            elif dtype == np.int64:
                df[col] = df[col].astype(int)
            elif dtype == np.float64:
                df[col] = df[col].astype(float)

        # Get the row from the DataFrame
        row = df.iloc[0].to_dict()

        # Construct the insert SQL query
        cols_list = ', '.join([str(key).replace(" ", "_") for key in row.keys()])
        query = sql.SQL(
            f"INSERT INTO {table_name} ({cols_list}, symbol, interval) VALUES ({', '.join(['%s'] * len(row))}, %s, %s) ON CONFLICT DO NOTHING")

        # Prepare the data to be inserted
        data_to_insert = list(row.values()) + [symbol, interval]

        # Create a cursor
        cur = self.conn.cursor()

        # Execute the insert SQL query
        cur.execute(query, data_to_insert)

        # Commit the transaction
        self.conn.commit()

        # Close the cursor
        cur.close()

    def _prepare_dict(self, data_dict, time_key, out_time_column):
        prep_dict = {}
        for col, value in data_dict.items():
            if isinstance(value, bool):
                prep_dict[col] = str(value)
            elif isinstance(value, np.int64):
                prep_dict[col] = int(value)
            elif isinstance(value, np.float64):
                prep_dict[col] = float(value)
            else:
                prep_dict[col] = str(value)
            # If date_as_index is True, convert date in the dict to the desired format
            if col == time_key:
                prep_dict[out_time_column] = value.strftime('%Y-%m-%d %H:%M:%S')
        return prep_dict

    def insert_orbk_dict_to_tsdb(self, data_dict, table_name, time_key, out_time_column,
                                 symbol_col, side_col, debug=True):
        prep_dict = self._prepare_dict(data_dict, time_key, out_time_column)

        columns = ', '.join([f"{col.replace(' ', '_')} {guess_type(value)}" for col, value in prep_dict.items()])
        # columns += f", {symbol_col} TEXT"

        create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns}, ' \
                             f'PRIMARY KEY ({out_time_column}, {symbol_col}, {side_col}))'
        if debug:
            print(prep_dict)
            print(create_table_query)
        self.cur.execute(create_table_query)

        self.conn.commit()

        # Construct the insert SQL query
        cols_list = ', '.join([str(key).replace(" ", "_") for key in prep_dict.keys()])
        query_str = f"INSERT INTO {table_name} ({cols_list}, {symbol_col}, {side_col}) " \
                    f"VALUES ({', '.join(['%s'] * len(prep_dict))}, %s, %s) ON CONFLICT DO NOTHING"
        query = sql.SQL(query_str)

        # Prepare the data to be inserted
        data_to_insert = list(prep_dict.values()) + [symbol_col]

        # Create a cursor
        cur = self.conn.cursor()

        # Execute the insert SQL query
        cur.execute(query, data_to_insert)

        # Commit the transaction
        self.conn.commit()

        # Close the cursor
        cur.close()

    # def insert_dict_to_tsdb(self, data_dict, table_name, time_key, time_column, symbol, interval, debug=True):
    #     prep_dict = {}
    #     # Convert data_dict datatypes to native Python datatypes
    #     for col, value in data_dict.items():
    #         if isinstance(value, bool):
    #             prep_dict[col] = str(value)
    #         elif isinstance(value, np.int64):
    #             prep_dict[col] = int(value)
    #         elif isinstance(value, np.float64):
    #             prep_dict[col] = float(value)
    #         else:
    #             prep_dict[col] = str(value)
    #         # If date_as_index is True, convert date in the dict to the desired format
    #         if col == time_key:
    #             prep_dict[time_column] = value.strftime('%Y-%m-%d %H:%M:%S')
    #
    #     columns = ', '.join([f"{col.replace(' ', '_')} {guess_type(value)}" for col, value in prep_dict.items()])
    #
    #     columns += ", symbol TEXT, interval TEXT"
    #     create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns}, PRIMARY KEY ({time_column}, symbol,interval))'
    #     if debug:
    #         print(prep_dict)
    #         print(create_table_query)
    #     self.cur.execute(create_table_query)
    #
    #     self.conn.commit()
    #
    #     # Construct the insert SQL query
    #     cols_list = ', '.join([str(key).replace(" ", "_") for key in prep_dict.keys()])
    #     query_str = f"INSERT INTO {table_name} ({cols_list}, symbol, interval) VALUES ({', '.join(['%s'] * len(prep_dict))}, %s, %s) ON CONFLICT DO NOTHING"
    #     query = sql.SQL(query_str)
    #
    #     # Prepare the data to be inserted
    #     data_to_insert = list(prep_dict.values()) + [symbol, interval]
    #
    #     # Create a cursor
    #     cur = self.conn.cursor()
    #
    #     # Execute the insert SQL query
    #     cur.execute(query, data_to_insert)
    #
    #     # Commit the transaction
    #     self.conn.commit()
    #
    #     # Close the cursor
    #     cur.close()
