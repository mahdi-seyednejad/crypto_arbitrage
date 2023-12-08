from decimal import Decimal


def get_order_output_quantity(order, current_price):
    if order["success"]:
        # Check if 'base_size' is available
        if "base_size" in order["order_configuration"]["market_market_ioc"]:
            return Decimal(order["order_configuration"]["market_market_ioc"]["base_size"])
        # If 'base_size' is not available, use 'quote_size' and 'current_price'
        elif "quote_size" in order["order_configuration"]["market_market_ioc"]:
            quote_size = Decimal(order["order_configuration"]["market_market_ioc"]["quote_size"])
            current_price_decimal = Decimal(current_price)
            base_size = quote_size / current_price_decimal
            return base_size
        else:
            # Handle cases where neither 'base_size' nor 'quote_size' is available
            return "Unknown quantity"
    else:
        return -1
