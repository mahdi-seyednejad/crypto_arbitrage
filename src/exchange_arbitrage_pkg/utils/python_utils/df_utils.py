import pandas as pd


import pandas as pd

def identify_column_types(df):
    type_columns = {'float': [], 'int32': [], 'int64': [], 'object': []}

    for col in df.columns:
        if df[col].dtype == 'object':
            # Attempt to convert object columns to numeric
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            non_null_count = numeric_series.notnull().sum()

            # Check if a significant portion of the column is numeric
            if non_null_count / len(df) > 0.8:  # Threshold can be adjusted
                # Convert to float to handle cases where integers are returned
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
    column_types = identify_column_types(df)
    new_df = df.copy()

    for col_type, columns in column_types:
        if col_type == 'float':
            new_df[columns] = new_df[columns].astype(float)
        elif col_type == 'int32':
            new_df[columns] = new_df[columns].astype(float).astype('int32')
        elif col_type == 'int64':
            new_df[columns] = new_df[columns].astype(float).astype('int64')

    return new_df

