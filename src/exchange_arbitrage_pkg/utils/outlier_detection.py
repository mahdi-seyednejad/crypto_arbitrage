import numpy as np


def remove_outliers(order_book, threshold=2.5):
    # Calculate z-scores for price column
    z_scores = np.abs((order_book['price'] - order_book['price'].mean()) / order_book['price'].std())

    # Filter out rows with z-score greater than a threshold
    filtered_order_book = order_book[z_scores < threshold]

    return filtered_order_book

