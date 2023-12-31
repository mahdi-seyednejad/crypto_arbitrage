from src.exchange_arbitrage_pkg.utils.python_utils.data_structures import Stack


def process_sell_side_order_book(df_in, price_col, volume_col):
    df = df_in[[price_col, volume_col]].copy()
    sell_stack = Stack()
    sorted_df = df.sort_values(by=price_col, ascending=False)
    orders = sorted_df.to_dict('records')  # Convert rows to dictionaries
    for order in orders:
        sell_stack.push(order)
    return sell_stack


def process_buy_side_order_book(df_in, price_col, volume_col):
    df = df_in[[price_col, volume_col]].copy()
    buy_stack = Stack()
    sorted_df = df.sort_values(by=price_col, ascending=True)
    orders = sorted_df.to_dict('records')  # Convert rows to dictionaries
    for order in orders:
        buy_stack.push(order)
    return buy_stack


def update_withdrawal_fee_money(src_price,
                                current_trading_volume,
                                withdrawal_fee_money,
                                remaining_withdrawal_fee_amount):
    if remaining_withdrawal_fee_amount > 0:
        w_volume = min(current_trading_volume, remaining_withdrawal_fee_amount)
        withdrawal_fee_money += src_price * w_volume
        remaining_withdrawal_fee_amount -= w_volume
        return withdrawal_fee_money, remaining_withdrawal_fee_amount
    else:
        return withdrawal_fee_money, remaining_withdrawal_fee_amount


def compute_trade_volume_and_money(src_sell_order_book_df,
                                   dst_buy_order_book_df,
                                   price_col, volume_col, withdrawal_fee_amount):
    src_sell_stack = process_sell_side_order_book(src_sell_order_book_df, price_col, volume_col)
    dst_buy_stack = process_buy_side_order_book(dst_buy_order_book_df, price_col, volume_col)
    spent_money = 0
    cum_traded_volume = 0
    sold_money = 0
    rem_w_fee_amount = withdrawal_fee_amount
    withdrawal_fee_money = 0

    while not src_sell_stack.is_empty() and not dst_buy_stack.is_empty():
        src_order = src_sell_stack.pop()
        dst_order = dst_buy_stack.pop()

        # [The main operation]
        if dst_order['price'] <= src_order['price']:
            break

        # Calculate the min of possible trading volume
        current_trading_volume = min(src_order['volume'], dst_order['volume'])

        withdrawal_fee_money, rem_w_fee_amount = update_withdrawal_fee_money(src_order['price'],
                                                                             current_trading_volume,
                                                                             withdrawal_fee_money,
                                                                             rem_w_fee_amount)

        # Calculate amount bought and amount to be sold
        cum_traded_volume += current_trading_volume
        # Update the volumes in the orders
        src_order['volume'] -= current_trading_volume
        dst_order['volume'] -= current_trading_volume

        spent_money += current_trading_volume * src_order['price']
        sold_money += current_trading_volume * dst_order['price']

        # If there's remaining volume, put the order back to the stack
        if src_order['volume'] > 0:
            src_sell_stack.push(src_order)
        if dst_order['volume'] > 0:
            dst_buy_stack.push(dst_order)

    return cum_traded_volume, spent_money, sold_money, withdrawal_fee_money


def calculate_profit(spent_money,
                     sold_money,
                     withdrawal_fee_money,
                     src_transaction_fee_rate,
                     dst_transaction_fee_rate, ):
    # spent_money + (spent_money * src_transaction_fee_rate) = total_buy_cost
    total_buy_cost = spent_money * (1 + src_transaction_fee_rate)

    # sold_money - (sold_money * dst_transaction_fee_rate) - withdrawal_fee
    total_sell_gain = sold_money * (1 - dst_transaction_fee_rate) - withdrawal_fee_money
    profit = total_sell_gain - total_buy_cost
    return profit, total_buy_cost, total_sell_gain


def calculate_symbol_profit(order_book_df,
                            withdrawal_fee,
                            src_exchange_name,
                            dst_exchange_name,
                            src_transaction_fee_rate=0.001,
                            dst_transaction_fee_rate=0.001,
                            price_col='price',
                            volume_col='volume',
                            side_col='side',
                            exchange_name_col='exchange_name',
                            profit_col='profit',
                            spent_money_col='spent_money',
                            sold_money_col='sold_money',
                            trading_volume_col='trading_volume'):
    order_book_src_df = order_book_df[order_book_df[exchange_name_col] == src_exchange_name]
    order_book_src_df_sell = order_book_src_df[order_book_src_df[side_col] == 'sell']

    order_book_dst_df = order_book_df[order_book_df[exchange_name_col] == dst_exchange_name]
    order_book_dst_df_buy = order_book_dst_df[order_book_dst_df[side_col] == 'buy']

    cum_traded_volume, spent_money, sold_money, withdrawal_fee_money = \
        compute_trade_volume_and_money(src_sell_order_book_df=order_book_src_df_sell,
                                       dst_buy_order_book_df=order_book_dst_df_buy,
                                       price_col=price_col,
                                       volume_col=volume_col,
                                       withdrawal_fee_amount=withdrawal_fee)
    profit, total_buy_cost, total_sell_gain = \
        calculate_profit(spent_money=spent_money,
                         sold_money=sold_money,
                         withdrawal_fee_money=withdrawal_fee_money,
                         src_transaction_fee_rate=src_transaction_fee_rate,
                         dst_transaction_fee_rate=dst_transaction_fee_rate)
    return {profit_col: profit,
            spent_money_col: total_buy_cost,
            sold_money_col: total_sell_gain,
            trading_volume_col: cum_traded_volume}


def compute_symbol_eval_vector(order_book_df,
                               withdrawal_fee,
                               src_exchange_name,
                               dst_exchange_name,
                               src_transaction_fee_rate,
                               dst_transaction_fee_rate,
                               col_info):
    symbol_eval_dict = calculate_symbol_profit(order_book_df,
                                               withdrawal_fee,
                                               src_exchange_name,
                                               dst_exchange_name,
                                               src_transaction_fee_rate=src_transaction_fee_rate,
                                               dst_transaction_fee_rate=dst_transaction_fee_rate,
                                               price_col='price',
                                               volume_col='volume',
                                               side_col='side',
                                               exchange_name_col='exchange_name')
    symbol_eval_vector = [symbol_eval_dict[col] for col in col_info.order_book_col_obj.get_order_eval_out_cols()]
    return symbol_eval_vector
