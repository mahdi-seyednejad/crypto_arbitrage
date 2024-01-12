import json
from decimal import Decimal
from datetime import datetime
import pandas as pd

import numpy as np
from psycopg2._psycopg import AsIs
from psycopg2.extensions import register_adapter

# Define the mapping between Pandas data types and SQL data types
pandas_to_sql_types = {
    'int64': 'BIGINT',
    'int32': 'INTEGER',
    'int16': 'SMALLINT',
    'int8': 'SMALLINT',
    'float64': 'FLOAT',
    'float32': 'REAL',
    'bool': 'BOOLEAN',
    'object': 'TEXT',
    'string_': 'TEXT',
    'unicode_': 'TEXT',
    'datetime64': 'TIMESTAMP',
    'datetime64[ns]': 'TIMESTAMP',
    'datetime64[ns, UTC]': 'TIMESTAMP',
    'datetime': 'TIMESTAMP',
    'date': 'DATE',
    'time': 'TIME'
}


# Determine the SQL data types for each column
def get_col_types_sql(df):
    col_types = {}
    for col in df.columns:
        # print(f"Column: {col}")
        unique_types = df[col].apply(type).unique()
        # print(f"Unique types in the column: {unique_types}")
        pandas_type = str(df[col].dtype)
        col_types[col] = pandas_to_sql_types.get(pandas_type, 'TEXT')
        if "datetime" in str(pandas_type):
            col_types[col] = "TIMESTAMP"
    return col_types


def guess_type(value):
    if isinstance(value, int):
        return "INT"
    elif isinstance(value, float):
        return "FLOAT"
    elif isinstance(value, str):
        return "TEXT"
    elif isinstance(value, bool):
        return 'BOOLEAN'
    elif isinstance(value, datetime):
        return "TIMESTAMP"
    # ... You can add more type checks as needed.
    else:
        return "TEXT"  # default


def prepare_dataframe(df_in, time_column, date_as_index, need_dt_conversion):
    df = df_in.copy()

    if date_as_index:
        df = df.reset_index().rename(columns={'index': time_column})

    # Convert to datetime and then to string format
    if need_dt_conversion:
        df[time_column] = pd.to_datetime(df[time_column], errors='coerce')
        df[time_column] = df[time_column].dt.strftime('%Y-%m-%d %H:%M:%S')

    return df


def register_data_adapters():
    register_adapter(np.datetime64, AsIs)
    register_adapter(np.bool_, AsIs)
    register_adapter(np.int64, AsIs)
    register_adapter(np.int32, AsIs)


def convert_bool_columns(df):
    bool_cols = df.select_dtypes(include=[np.bool_]).columns
    df[bool_cols] = df[bool_cols].astype(str)
    return df


def handle_null_values(df):
    return df.where(pd.notnull(df), None)

def check_overflow_precision(df):
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        if df[col].max() > np.iinfo(np.int32).max or df[col].min() < np.iinfo(np.int32).min:
            print(f"Warning: Potential overflow in column {col}")

def convert_timezone(df, time_column, tz_to_convert='UTC'):
    df[time_column] = pd.to_datetime(df[time_column]).dt.tz_localize(tz_to_convert)
    return df

# def check_large_text_binary(df, threshold=65535):
#     for col in df.columns:
#         if df[col].dtype == 'object' and df[col].str.len().max() > threshold:
#             print(f"Warning: Column {col} contains large text data.")


def check_large_text_binary(df, threshold=65535):
    for col in df.columns:
        # Check if column contains string data
        if df[col].apply(lambda x: isinstance(x, str)).all():
            if df[col].str.len().max() > threshold:
                print(f"Warning: Column {col} contains large text data.")


def convert_to_decimal(df, decimal_cols):
    for col in decimal_cols:
        df[col] = df[col].apply(lambda x: Decimal(str(x)))
    return df

def serialize_complex_types(df):
    for col in df.columns:
        if isinstance(df[col].iloc[0], (list, dict)):
            df[col] = df[col].apply(json.dumps)
    return df

def check_data_integrity(df, unique_cols):
    for col in unique_cols:
        if df[col].duplicated().any():
            print(f"Warning: Duplicates found in column {col}")


def check_encoding(df):
    for col in df.select_dtypes(include=['object', 'string']):
        if not df[col].map(lambda x: isinstance(x, str)).all():
            print(f"Warning: Non-string values found in column {col}")


def update_existing_data(cur, table_name, df, primary_key_cols):
    for index, row in df.iterrows():
        query = f"UPDATE {table_name} SET " + ', '.join([f"{col} = %s" for col in df.columns if col not in primary_key_cols])
        query += " WHERE " + ' AND '.join([f"{col} = %s" for col in primary_key_cols])
        values = tuple(row[col] for col in df.columns if col not in primary_key_cols) + tuple(row[col] for col in primary_key_cols)
        cur.execute(query, values)
