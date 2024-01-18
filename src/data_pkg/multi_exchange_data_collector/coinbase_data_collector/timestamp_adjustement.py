from datetime import datetime, timedelta, timezone
import time

class TimeAdjuster:
    def __init__(self, current_time, threshold_days=None):
        self.current_time = current_time # We read this from data
        self.threshold_days = threshold_days # How many day difference we consider to say it is old

    def _is_old_timestamp(self, entry_timestamp):
        if self.threshold_days is None:
            return entry_timestamp.startswith('1970-01-01T00:00:00Z')
        """ Check if the timestamp is older than the threshold. """
        try:
            timestamp_datetime = datetime.fromisoformat(entry_timestamp.rstrip('Z'))
            threshold_date = datetime.utcnow() - timedelta(days=self.threshold_days)
            return timestamp_datetime < threshold_date
        except ValueError:
            # If the timestamp is not in a valid format, consider it old.
            return True

    def _adjust_timestamp(self, entry_timestamp):
        truncated_timestamp = truncate_timestamp(self.current_time.rstrip('Z')) + '+00:00'
        root_timestamp = datetime.fromisoformat(truncated_timestamp)
        epoch_start = datetime(1970, 1, 1, tzinfo=timezone.utc)
        # Calculate the time difference from the epoch start
        data_time = datetime.fromisoformat(entry_timestamp.replace('Z', '+00:00'))
        time_diff = data_time - epoch_start
        # Adjust 'event_time' using the root 'timestamp'
        adjusted_time = root_timestamp + time_diff
        return adjusted_time.isoformat() #+ 'Z'

    def check_and_adjust_timestamp(self, entry_timestamp):
        """ Check if the timestamp is old and adjust it if necessary. """
        if self._is_old_timestamp(entry_timestamp):
            return self._adjust_timestamp(entry_timestamp)
        else:
            return entry_timestamp

def truncate_timestamp(timestamp):
    """ Truncate the fractional seconds in the timestamp to six decimal places. """
    if '.' in timestamp:
        main_part, fractional_part = timestamp.split('.')
        fractional_part = fractional_part[:6]  # Keep only six decimal places
        return f'{main_part}.{fractional_part}'
    return timestamp

def is_old_timestamp(entry_timestamp, threshold_days):
    """ Check if the timestamp is older than the threshold. """
    try:
        timestamp_datetime = datetime.fromisoformat(entry_timestamp.rstrip('Z'))
        threshold_date = datetime.utcnow() - timedelta(days=threshold_days)
        return timestamp_datetime < threshold_date
    except ValueError:
        # If the timestamp is not in a valid format, consider it old.
        return True


# def adjust_timestamp(data_timestamp, current_system_time):
#     """ Adjust the timestamp based on the current system time and the difference from '1970-01-01T00:00:00Z' """
#     if not isinstance(current_system_time, datetime):
#         raise ValueError("current_system_time must be a datetime object")
#
#     epoch_start = datetime(1970, 1, 1, tzinfo=timezone.utc)
#     data_time = datetime.fromisoformat(data_timestamp.replace('Z', '+00:00'))
#     time_diff = data_time - epoch_start
#     adjusted_time = current_system_time + time_diff
#
#     return adjusted_time.isoformat() + 'Z'

def adjust_timestamp(data_timestamp, current_system_time):
    """ Adjust the timestamp based on the current system time and the difference from '1970-01-01T00:00:00Z' """
    # If current_system_time is a string, try converting it to a datetime object
    if isinstance(current_system_time, str):
        try:
            # Attempt to convert from ISO format string
            current_system_time = datetime.fromisoformat(current_system_time.rstrip('Z'))
        except ValueError:
            # If not ISO format, it might be a UNIX timestamp
            try:
                current_system_time = datetime.fromtimestamp(int(current_system_time), tz=timezone.utc)
            except ValueError:
                raise ValueError("current_system_time must be a datetime object, a valid isoformat string, or a UNIX timestamp")

    # If current_system_time is an integer, treat it as a UNIX timestamp
    elif isinstance(current_system_time, int):
        current_system_time = datetime.fromtimestamp(current_system_time, tz=timezone.utc)

    # Check if current_system_time is now a datetime object
    if not isinstance(current_system_time, datetime):
        raise ValueError("current_system_time must be a datetime object, a valid isoformat string, or a UNIX timestamp")

    epoch_start = datetime(1970, 1, 1, tzinfo=timezone.utc)
    data_time = datetime.fromisoformat(data_timestamp.replace('Z', '+00:00'))
    time_diff = data_time - epoch_start
    adjusted_time = current_system_time + time_diff

    return adjusted_time.isoformat() + 'Z'

def adjust_event_times(data):
    """ Adjust 'event_time' in the data based on the provided 'timestamp'. """
    root_timestamp = datetime.fromisoformat(data['timestamp'].rstrip('Z') + '+00:00')
    epoch_start = datetime(1970, 1, 1, tzinfo=timezone.utc)

    for event in data.get('events', []):
        if event.get('type') == 'snapshot':
            for update in event.get('updates', []):
                event_time = update.get('event_time')
                if event_time.startswith('1970-01-01T00:00:00Z'):
                    # Calculate the time difference from the epoch start
                    data_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
                    time_diff = data_time - epoch_start
                    # Adjust 'event_time' using the root 'timestamp'
                    adjusted_time = root_timestamp + time_diff
                    update['event_time'] = adjusted_time.isoformat() + 'Z'

def check_and_adjust_timestamp(entry_timestamp, current_system_time, threshold_days):
    """ Check if the timestamp is old and adjust it if necessary. """
    if is_old_timestamp(entry_timestamp, threshold_days):
        return adjust_timestamp(entry_timestamp, current_system_time)
    else:
        return entry_timestamp
