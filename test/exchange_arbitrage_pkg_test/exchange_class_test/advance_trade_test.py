from decimal import Decimal

from src.exchange_code_bases.exchange_class.advance_trade_exchange_tools.order_parser import \
    get_order_output_quantity

def create_example_order_response(order_conf):
    return {
        'success': True,
        'failure_reason': 'UNKNOWN_FAILURE_REASON',
        'order_id': '2f20ed21-b0e9-45e0-94f5-10482ea3e9f3',
        'success_response': {
            'order_id': '2f20ed21-b0e9-45e0-94f5-10482ea3e9f3',
            'product_id': 'VOXEL-USD',
            'side': 'BUY',
            'client_order_id': '1212'
        },
        'order_configuration': order_conf
    }

def test_get_order_output_quantity():
    order_conf_buy = {'market_market_ioc': {'quote_size': '2.11096800'}}

    # order = {
    #     'success': True,
    #     'failure_reason': 'UNKNOWN_FAILURE_REASON',
    #     'order_id': '2f20ed21-b0e9-45e0-94f5-10482ea3e9f3',
    #     'success_response': {
    #         'order_id': '2f20ed21-b0e9-45e0-94f5-10482ea3e9f3',
    #         'product_id': 'VOXEL-USD',
    #         'side': 'BUY',
    #         'client_order_id': '1212'
    #     },
    #     'order_configuration': order_conf_buy
    # }
    order_buy = create_example_order_response(order_conf_buy)
    current_price = "1.00"  # Example current price
    expected_base_size = Decimal('2.11096800')  # Expected base size
    assert get_order_output_quantity(order_buy, current_price) == expected_base_size

    order_conf_sell = {'market_market_ioc': {'base_size': '10.01'}}
    order_sell = create_example_order_response(order_conf_sell)
    expected_base_size = Decimal('10.01')  # Expected base size
    assert get_order_output_quantity(order_sell, current_price) == expected_base_size




# # Run the test
# if __name__ == "__main__":
#     pytest.main()
