import pandas as pd
import numpy as np
import re


def is_boolean_string_series(series):
    if series.dtype != object:
        return False

    # Ensure all non-NA values are strings before applying string methods
    string_series = series.dropna().apply(lambda x: str(x).lower() if not pd.isna(x) else x)
    unique_str_values = set(string_series.unique())

    return unique_str_values.issubset({'true', 'false', '1', '0'})


def identify_column_types(df):
    type_columns = {'float': [], 'int32': [], 'int64': [], 'object': []}

    for col in df.columns:
        if df[col].dtype == 'object':
            # Check for boolean-like strings first
            if is_boolean_string_series(df[col]):
                type_columns['object'].append(col)
                continue

            # Replace empty strings with NaN
            temp_col = df[col].replace('', np.nan)

            # Attempt to convert object columns to numeric
            numeric_series = pd.to_numeric(temp_col, errors='coerce')
            non_null_count = numeric_series.notnull().sum()

            # Check if a significant portion of the column is numeric
            if non_null_count / len(df) > 0.8:
                numeric_series_float = numeric_series.astype(float)
                if all(numeric_series_float.dropna().apply(lambda x: x.is_integer())):
                    if numeric_series_float.max() <= 2147483647 and numeric_series_float.min() >= -2147483648:
                        type_columns['int32'].append(col)
                    else:
                        type_columns['int64'].append(col)
                else:
                    type_columns['float'].append(col)
            else:
                type_columns['object'].append(col)
        else:
            pandas_type = str(df[col].dtype)
            if pandas_type.startswith('float'):
                type_columns['float'].append(col)
            elif pandas_type in ['int64', 'int32']:
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
            if is_convertible_to_numeric(new_df[column]):
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
            else:
                print(f"Column {column} contains complex data structures and cannot be converted to numeric.")

    return new_df


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def is_convertible_to_numeric(series):
    # If the series is entirely NaNs, it can be considered convertible
    if series.isnull().all():
        return True

    non_na_values = series.dropna()
    if non_na_values.empty:
        # All values are NaN
        return True

    unique_types = set(non_na_values.apply(type))
    if len(unique_types) > 1:
        # Mixed types (excluding NaN), not convertible
        return False

    # Special handling for strings that represent booleans
    if unique_types == {str}:
        unique_str_values = set(non_na_values.str.lower().unique())
        if unique_str_values.issubset({'true', 'false', '1', '0'}):
            # Series contains strings that can be interpreted as booleans
            return True

    if bool in unique_types:
        # Contains explicit boolean values
        return False

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

