# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone
import re
import calendar

import alfred


def parse_interval(interval_str):
    """
    Parse interval string and return timedelta.
    Format: "<number> <unit>" or "interval <number> <unit>"
    Supported units: second(s), minute(s), hour(s), day(s), week(s)
    """
    pattern = r'(?:interval\s+)?(\d+)\s+(second|seconds|minute|minutes|hour|hours|day|days|week|weeks)'
    match = re.search(pattern, interval_str, re.IGNORECASE)

    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2).lower()

    # Map units to timedelta kwargs
    unit_map = {
        'second': 'seconds',
        'seconds': 'seconds',
        'minute': 'minutes',
        'minutes': 'minutes',
        'hour': 'hours',
        'hours': 'hours',
        'day': 'days',
        'days': 'days',
        'week': 'weeks',
        'weeks': 'weeks',
    }

    timedelta_unit = unit_map.get(unit)
    if timedelta_unit:
        return timedelta(**{timedelta_unit: amount})

    return None


def parse_datetime_string(dt_str):
    """
    Parse a datetime string in various formats.
    Returns a timezone-aware datetime object in UTC.
    """
    # Remove trailing 'Z' timezone indicator if present (indicates UTC)
    dt_str = re.sub(r'Z$', '', dt_str)

    # Extract and remove trailing milliseconds if present (e.g., ".000" or ".709")
    milliseconds = 0
    ms_match = re.search(r'\.(\d+)$', dt_str)
    if ms_match:
        ms_str = ms_match.group(1)
        # Pad or truncate to 3 digits and convert to microseconds
        ms_str = ms_str.ljust(3, '0')[:3]
        milliseconds = int(ms_str)
        dt_str = re.sub(r'\.(\d+)$', '', dt_str)

    # Try common datetime formats
    formats = [
        '%Y-%m-%d %H:%M:%S',      # 2026-01-16 10:19:55
        '%Y-%m-%dT%H:%M:%S',      # 2026-01-16T10:19:55
        '%Y-%m-%d',               # 2026-01-16
        '%d %b %Y %H:%M:%S',      # 16 Jan 2026 10:19:55
        '%a, %d %b %Y %H:%M:%S',  # Fri, 16 Jan 2026 10:19:55
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(dt_str, fmt)
            # Add milliseconds as microseconds (milliseconds * 1000)
            dt = dt.replace(microsecond=milliseconds * 1000)
            # Make timezone aware (assume UTC if no timezone info)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    # If all formats fail, raise ValueError
    raise ValueError(f"Could not parse datetime string: {dt_str}")


def process(query_str):
    """Entry point for Alfred workflow."""
    value = parse_query_value(query_str)
    if value is not None:
        results = alfred_items_for_value(value)
        xml = alfred.xml(results)
        alfred.write(xml)


def parse_query_value(query_str):
    """
    Parse query string and return a datetime object.
    Returns a timezone-aware datetime in UTC.
    """
    try:
        query_str = str(query_str).strip('"\' ')

        # Check for interval expressions (e.g., "now - 1 day" or "2026-01-16 10:19:55 - 3 hours")
        interval_pattern = r'(.+?)\s*([+-])\s*(?:interval\s+)?(\d+\s+(?:second|seconds|minute|minutes|hour|hours|day|days|week|weeks))'
        interval_match = re.match(interval_pattern, query_str, re.IGNORECASE)

        if interval_match:
            base_str = interval_match.group(1).strip()
            operator = interval_match.group(2)
            interval_str = interval_match.group(3)

            # Parse base datetime
            if base_str == 'now':
                dt = datetime.now(timezone.utc)
            else:
                # Try parsing as timestamp first
                try:
                    if base_str.isdigit():
                        # Millisecond timestamp
                        if len(base_str) == 13:
                            timestamp = int(base_str) / 1000
                        else:
                            timestamp = float(base_str)
                        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    else:
                        # Try parsing as datetime string
                        dt = parse_datetime_string(base_str)
                except (ValueError, OSError):
                    # If timestamp parsing fails, try datetime string
                    dt = parse_datetime_string(base_str)

            # Parse and apply interval
            interval = parse_interval(interval_str)
            if interval:
                if operator == '-':
                    dt = dt - interval
                else:  # operator == '+'
                    dt = dt + interval

            return dt

        # Handle "now" keyword
        if query_str == 'now':
            return datetime.now(timezone.utc)

        # Try parsing as timestamp
        try:
            if query_str.isdigit():
                # Millisecond timestamp
                if len(query_str) == 13:
                    timestamp = int(query_str) / 1000
                else:
                    timestamp = float(query_str)
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, OSError):
            pass

        # Try parsing as datetime string
        return parse_datetime_string(query_str)

    except (TypeError, ValueError):
        return None


def alfred_items_for_value(dt):
    """
    Given a datetime object, return a list of Alfred items
    for each of the result formats.
    """
    index = 0
    results = []

    # UTC Timestamp (seconds)
    timestamp = int(dt.timestamp())
    results.append(alfred.Item(
        title=str(timestamp),
        subtitle='UTC Timestamp',
        attributes={
            'uid': alfred.uid(index),
            'arg': timestamp,
        },
        icon='icon.png',
    ))
    index += 1

    # UTC Millisecond Timestamp
    timestamp_ms = int(dt.timestamp() * 1000)
    results.append(alfred.Item(
        title=str(timestamp_ms),
        subtitle='UTC MilliSecond Timestamp',
        attributes={
            'uid': alfred.uid(index),
            'arg': timestamp_ms,
        },
        icon='icon.png',
    ))
    index += 1

    # Get milliseconds for formats that need them
    milliseconds = int(dt.microsecond / 1000)

    # Various datetime formats
    formats = [
        ('%Y-%m-%d %H:%M:%S', 'YYYY-MM-DD HH:MM:SS (UTC)'),
        ('%d %b %Y %H:%M:%S', 'DD Mon YYYY HH:MM:SS (UTC)'),
        ('%a, %d %b %Y %H:%M:%S', 'Day, DD Mon YYYY HH:MM:SS (UTC)'),
        ('%Y-%m-%dT%H:%M:%S', 'ISO 8601 (UTC)'),
        ('%Y-%m-%dT%H:%M:%S%z', 'ISO 8601 with timezone'),
    ]

    for fmt, description in formats:
        formatted = dt.strftime(fmt)
        results.append(alfred.Item(
            title=formatted,
            subtitle=description,
            attributes={
                'uid': alfred.uid(index),
                'arg': formatted,
            },
            icon='icon.png',
        ))
        index += 1

    # Formats with milliseconds
    ms_formats = [
        (f'%Y-%m-%d %H:%M:%S.{milliseconds:03d}', 'YYYY-MM-DD HH:MM:SS.mmm (UTC)'),
        (f'%Y-%m-%dT%H:%M:%S.{milliseconds:03d}Z', 'ISO 8601 with milliseconds (UTC)'),
    ]

    for fmt, description in ms_formats:
        formatted = dt.strftime(fmt)
        results.append(alfred.Item(
            title=formatted,
            subtitle=description,
            attributes={
                'uid': alfred.uid(index),
                'arg': formatted,
            },
            icon='icon.png',
        ))
        index += 1

    return results


if __name__ == "__main__":
    try:
        query_str = alfred.args()[0]
    except IndexError:
        query_str = None
    process(query_str)
