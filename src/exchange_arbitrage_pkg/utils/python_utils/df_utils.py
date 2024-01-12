import pandas as pd
import numpy as np
import re

# def identify_column_types(df):
#     type_columns = {'float': [], 'int32': [], 'int64': [], 'object': []}
#
#     for col in df.columns:
#         if df[col].dtype == 'object':
#             # Attempt to convert object columns to numeric
#             # Replace empty strings with NaN
#             temp_col = df[col].replace('', np.nan)
#
#             # Attempt to convert object columns to numeric
#             numeric_series = pd.to_numeric(temp_col, errors='coerce')
#             # numeric_series = pd.to_numeric(df[col], errors='coerce')
#             non_null_count = numeric_series.notnull().sum()
#
#             # Check if a significant portion of the column is numeric
#             if non_null_count / len(df) > 0.8:  # Threshold can be adjusted
#                 # Convert to float to handle cases where integers are returned
#                 numeric_series_float = numeric_series.astype(float)
#                 if all(numeric_series_float.dropna().apply(lambda x: x.is_integer())):
#                     # If all non-null values are integers
#                     if numeric_series_float.max() <= 2147483647 and numeric_series_float.min() >= -2147483648:
#                         type_columns['int32'].append(col)
#                     else:
#                         type_columns['int64'].append(col)
#                 else:
#                     # If there are float values
#                     type_columns['float'].append(col)
#             else:
#                 type_columns['object'].append(col)
#         else:
#             pandas_type = str(df[col].dtype)
#             if pandas_type.startswith('float'):
#                 type_columns['float'].append(col)
#             elif pandas_type in ['int64', 'int32']:
#                 # Check if int64 column can be downcast to int32
#                 if df[col].max() <= 2147483647 and df[col].min() >= -2147483648:
#                     type_columns['int32'].append(col)
#                 else:
#                     type_columns['int64'].append(col)
#
#     return [(k, v) for k, v in type_columns.items() if v]


def identify_column_types(df):
    type_columns = {'float': [], 'int32': [], 'int64': [], 'object': []}

    for col in df.columns:
        if df[col].dtype == 'object':
            # Replace empty strings with NaN
            temp_col = df[col].replace('', np.nan)

            # Attempt to convert object columns to numeric
            numeric_series = pd.to_numeric(temp_col, errors='coerce')
            non_null_count = numeric_series.notnull().sum()

            # Check if a significant portion of the column is numeric
            if non_null_count / len(df) > 0.8:  # Threshold can be adjusted
                numeric_series_float = numeric_series.astype(float)
                if all(numeric_series_float.dropna().apply(lambda x: x.is_integer())):
                    # If all non-null values are integers
                    if numeric_series_float.max() <= 2147483647 and numeric_series_float.min() >= -2147483648:
                        type_columns['int32'].append(col)
                    else:
                        type_columns['int64'].append(col)
                else:
                    # If there are float values
                    type_columns['float'].append(col)
            else:
                type_columns['object'].append(col)
        else:
            pandas_type = str(df[col].dtype)
            if pandas_type.startswith('float'):
                type_columns['float'].append(col)
            elif pandas_type in ['int64', 'int32']:
                # Check if int64 column can be downcast to int32
                if df[col].max() <= 2147483647 and df[col].min() >= -2147483648:
                    type_columns['int32'].append(col)
                else:
                    type_columns['int64'].append(col)

    return [(k, v) for k, v in type_columns.items() if v]


def convert_column_types(df):
    column_types = identify_column_types(df)  # Assuming this function returns a list of tuples (type, column names)
    new_df = df.copy()

    for col_type, columns in column_types:
        for column in columns:
            # Replace empty strings with NaN
            new_df[column] = new_df[column].replace('', np.nan)

            try:
                if col_type == 'float':
                    new_df[column] = pd.to_numeric(new_df[column], errors='coerce')
                elif col_type == 'int32':
                    # Convert to float first to handle NaNs, then to int32
                    new_df[column] = pd.to_numeric(new_df[column], errors='coerce').astype('int32')
                elif col_type == 'int64':
                    # Convert to float first to handle NaNs, then to int64
                    new_df[column] = pd.to_numeric(new_df[column], errors='coerce').astype('int64')
            except Exception as e:
                print(f"Error converting column {column} to {col_type}: {e}")

    return new_df


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def is_convertible_to_numeric(series):
    # Check if the series contains complex data structures
    if any(isinstance(x, (list, dict, pd.Series)) for x in series):
        return False
    return True


def convert_column_types_and_case(df):
    column_types = identify_column_types(df)
    new_df = pd.DataFrame()

    for col_type, columns in column_types:
        print(col_type, columns)
        for column in columns:
            snake_case_column = camel_to_snake(column)
            # Replace empty strings with NaN in the snake_case column
            new_column = df[column].replace('', np.nan)

            if is_convertible_to_numeric(new_column):
                try:
                    if col_type == 'float':
                        new_column = pd.to_numeric(new_column, errors='coerce')
                    elif col_type == 'int32':
                        new_column = pd.to_numeric(new_column, errors='coerce').astype('int32')
                    elif col_type == 'int64':
                        new_column = pd.to_numeric(new_column, errors='coerce').astype('int64')
                except Exception as e:
                    print(f"Error converting column {column} to {col_type}: {e}")
            else:
                print(f"Column {column} contains complex data structures and cannot be converted to numeric.")

            # Add the processed column to the new DataFrame
            new_df[snake_case_column] = new_column

    return new_df

# def camel_to_snake(name):
#     # Convert camelCase to snake_case
#     s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
#     return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
#
# def is_convertible_to_numeric(series):
#     # Check if the series contains complex data structures
#     if any(isinstance(x, (list, dict, pd.Series)) for x in series):
#         return False
#     return True
#
# def convert_column_types_and_case(df):
#     column_types = identify_column_types(df)
#     new_df = df.copy()
#
#     for col_type, columns in column_types:
#         print(col_type, columns)
#         for column in columns:
#             snake_case_column = camel_to_snake(column)
#             # Replace empty strings with NaN in the snake_case column
#             if snake_case_column == 'binance_price_change_24h':
#                 print('here')
#             new_df[snake_case_column] = new_df[column].replace('', np.nan)
#             if is_convertible_to_numeric(new_df[snake_case_column]):
#                 try:
#                     if col_type == 'float':
#                         new_df[snake_case_column] = pd.to_numeric(new_df[snake_case_column], errors='coerce')
#                     elif col_type == 'int32':
#                         new_df[snake_case_column] = pd.to_numeric(new_df[snake_case_column], errors='coerce').astype('int32')
#                     elif col_type == 'int64':
#                         new_df[snake_case_column] = pd.to_numeric(new_df[snake_case_column], errors='coerce').astype('int64')
#                 except Exception as e:
#                     print(f"Error converting column {snake_case_column} to {col_type}: {e}")
#
#                 # Rename the original column to the snake_case name
#                 new_df.rename(columns={column: snake_case_column}, inplace=True)
#             else:
#                 print(
#                     f"Column {snake_case_column} contains complex data structures and cannot be converted to numeric.")
#
#     return new_df
# def convert_column_types(df):
#     column_types = identify_column_types(df)
#     new_df = df.copy()
#
#     for col_type, columns in column_types:
#         if col_type == 'float':
#             new_df[columns] = new_df[columns].astype(float)
#         elif col_type == 'int32':
#             new_df[columns] = new_df[columns].astype(float).astype('int32')
#         elif col_type == 'int64':
#             new_df[columns] = new_df[columns].astype(float).astype('int64')
#
#     return new_df

