# Assuming your functions are in a file named `timestamp.py`
from datetime import datetime, timedelta
from datetime import timezone

from src.data_pkg.multi_exchange_data_collector.coinbase_data_collector.timestamp_adjustement import adjust_timestamp, \
    is_old_timestamp


def test_adjust_timestamp():
    # Test the adjust_timestamp function
    api_timestamp = "1970-01-01T00:01:02Z"
    current_time = datetime.now(timezone.utc)
    expected_time = current_time
    expected_time = expected_time.__add__(timedelta(seconds=62))
    adjusted = adjust_timestamp(api_timestamp, current_time)
    current_time_str = expected_time.strftime("%Y-%m-%dT%H:%M")
    adjusted_str = adjusted[:16]  # 'adjusted' is already a string in ISO format
    assert current_time_str == adjusted_str  # Comparing up to minutes


def test_is_old_timestamp_valid():
    # Test is_old_timestamp with a valid recent timestamp
    recent_timestamp = datetime.utcnow().isoformat() + 'Z'
    assert not is_old_timestamp(recent_timestamp, 1)


def test_is_old_timestamp_old():
    # Test is_old_timestamp with an old timestamp
    old_timestamp = "1970-01-01T00:00:00Z"
    assert is_old_timestamp(old_timestamp, 1)


def test_is_old_timestamp_invalid():
    # Test is_old_timestamp with an invalid timestamp
    invalid_timestamp = "invalid-timestamp"
    assert is_old_timestamp(invalid_timestamp, 1)


def test_is_old_timestamp_threshold():
    # Test is_old_timestamp with a timestamp just at the threshold
    threshold_days = 10
    threshold_timestamp = (datetime.utcnow() - timedelta(days=threshold_days)).isoformat() + 'Z'
    assert is_old_timestamp(threshold_timestamp, threshold_days=threshold_days)


def test_is_old_timestamp_above_threshold():
    #Test is_old_timestamp with a timestamp just above the threshold
    threshold_days = 10
    above_threshold_timestamp = (datetime.utcnow() - timedelta(days=threshold_days + 1)).isoformat() + 'Z'
    assert is_old_timestamp(above_threshold_timestamp, threshold_days=threshold_days)

