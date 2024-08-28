class BestSymbolStructure:
    def __init__(self, symbol, price, withdraw_fee):
        self.symbol = symbol
        self.price = price
        self.withdraw_fee = withdraw_fee

    def __str__(self):
        return f'{self.symbol} {self.price} {self.withdraw_fee}'


# def get_sec_symbol_and_price(symbol_price_pair_list, backup_list):
#     if len(symbol_price_pair_list) == 0:
#         return BestSymbolStructure(None, None, None)
#     else:
#         if symbol_price_pair_list[-1][0] is None:
#             return backup_list[-1]
#         else:
#             return symbol_price_pair_list[-1]

def get_sec_symbol_and_price(symbol_price_pair_list, backup_list):
    if len(symbol_price_pair_list) == 0:
        return BestSymbolStructure(None, None, None)
    else:
        if symbol_price_pair_list[-1].symbol is None:
            return backup_list[-1]
        else:
            return symbol_price_pair_list[-1]

# def find_ranked_symbol_values(df_in, rank_col, rank_index, symbol_col, price_col):
#     # Rank the DataFrame based on the specified column
#     df_ranked = df_in.sort_values(by=rank_col, ascending=False, inplace=False)
#
#     # Find the ranked symbol and price for the specified rank
#     ranked_value = (df_ranked.iloc[rank_index][symbol_col],
#                     df_ranked.iloc[rank_index][price_col]) \
#         if len(df_ranked) > rank_index else (None, None)
#
#     return ranked_value
def find_ranked_symbol_values(df_in, rank_col, rank_index, symbol_col, price_col, withdraw_fee_col):
    # Rank the DataFrame based on the specified column
    df_ranked = df_in.sort_values(by=rank_col, ascending=False, inplace=False)

    # Find the ranked symbol and price for the specified rank
    if len(df_ranked) > rank_index:
        ranked_value = BestSymbolStructure(df_ranked.iloc[rank_index][symbol_col],
                                           df_ranked.iloc[rank_index][price_col],
                                           df_ranked.iloc[rank_index][withdraw_fee_col])
    else:
        ranked_value = BestSymbolStructure(None, None, None)
    return ranked_value


def find_best_backup_values(df_in, backup_rank_col, rank, symbol_col, price_col, price_diff_col, withdraw_fee_col):
    rank_index = rank - 1
    # Divide the DataFrame into positive and negative groups
    df_positive = df_in[df_in[price_diff_col] > 0]
    df_negative = df_in[df_in[price_diff_col] < 0]

    best_on_positive_diff = find_ranked_symbol_values(df_positive, backup_rank_col, rank_index, symbol_col, price_col,
                                                      withdraw_fee_col)
    best_on_negative_diff = find_ranked_symbol_values(df_negative, backup_rank_col, rank_index, symbol_col, price_col,
                                                      withdraw_fee_col)

    return best_on_positive_diff, best_on_negative_diff
