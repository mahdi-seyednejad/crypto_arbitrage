import pandas as pd
import pytest

from src.exchange_arbitrage_pkg.utils.python_utils.df_utils import identify_column_types


def test_identify_column_types_with_mixed_types():
    # Create a sample dataframe
    df = pd.DataFrame({
        'float_col': [1.0, 2.5, 3.1, 4.2, 5.5],
        'int32_col': [1, 2, 3, 4, 5],
        'int64_col': [12345678901, 12345678902, 12345678903, 12345678904, 12345678905],
        'object_col': ['a', 'b', 'c', 'd', 'e'],
        'mixed_num_col': ['1.1', '2', '3.5', '4.4', '5']  # Mixed integers and floats
    })

    expected = [
        ('float', ['float_col', 'mixed_num_col']),
        ('int32', ['int32_col']),
        ('int64', ['int64_col']),
        ('object', ['object_col'])
    ]

    assert sorted(identify_column_types(df)) == sorted(expected)

def test_identify_column_types_with_all_numeric():
    # Create a dataframe with all numeric types
    df = pd.DataFrame({
        'float_col': [1.0, 2.5, 3.1, None, 5.5],
        'int32_col': [1, 2, 3, 4, 5],
        'int64_col': [12345678901, 12345678902, 12345678903, 12345678904, 12345678905]
    })

    expected = [
        ('float', ['float_col']),
        ('int32', ['int32_col']),
        ('int64', ['int64_col'])
    ]

    assert sorted(identify_column_types(df)) == sorted(expected)

def test_identify_column_types_with_all_object():
    # Create a dataframe with all object types
    df = pd.DataFrame({
        'str_col': ['a', 'b', 'c', 'd', 'e'],
        'numeric_str_col': ['1', '2', '3', '4', '5'],
        'mixed_col': ['1', '2', 'three', '4.0', '5'],
        'float_str_col': ['1.2', '2.2', '3.2', '4.0', '5']

    })

    expected = [
        ('float', ['float_str_col']),
        ('object', ['str_col', 'mixed_col']),
        ('int32', ['numeric_str_col'])
    ]

    assert sorted(identify_column_types(df)) == sorted(expected)

# Add more test cases as needed
