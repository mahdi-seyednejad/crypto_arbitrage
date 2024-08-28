import uuid
import datetime


def generate_unique_order_id(symbol, uuid_length=8):
    """
    Generates a unique order ID using a combination of timestamp and a shortened UUID.

    :param symbol: The symbol name for which the order ID is being generated.
    :param uuid_length: Length of the UUID segment to be used. Default is 8 characters.
    :return: A unique order ID.
    """
    # Current timestamp in YYYYMMDD_HHMMSS format
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate a UUID, convert it to a string, and take the first `uuid_length` characters
    unique_id = str(uuid.uuid4())[:uuid_length]

    # Combine symbol, timestamp, and shortened UUID to create a unique order ID
    order_id = f"{symbol}_{timestamp}_{unique_id}"

    return order_id
