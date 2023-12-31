import pandas as pd


def update_data_df(original_df_in, new_df):
    if original_df_in is None or new_df is None:
        return new_df
    if len(original_df_in) == 0:
        return new_df

    # Keep only rows in original_df where the symbol is in new_df
    original_df = original_df_in[original_df_in['symbol'].isin(new_df['symbol'])].copy()

    # Decrease recency by one, ensuring it does not go below zero
    # original_df['recency'] = original_df['recency'].apply(lambda x: x - 1)
    original_df.loc[:, 'recency'] = original_df['recency'].apply(lambda x: x - 1)

    # Find new symbols in new_df not in original_df
    new_symbols = new_df[~new_df['symbol'].isin(original_df['symbol'])]

    # Concatenate new symbols to original_df
    original_df = pd.concat([original_df, new_symbols], ignore_index=True)

    # Update values from new_df, except for 'recency'
    # Create a temporary DataFrame with columns excluding 'recency'
    temp_new_df = new_df.drop(columns='recency', errors='ignore')
    original_df.update(temp_new_df)

    return original_df
