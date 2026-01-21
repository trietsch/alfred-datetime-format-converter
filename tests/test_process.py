#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the datetime format converter workflow.
"""
import sys
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock

# Add workflow directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'workflow'))

# Mock the alfred module before importing process
mock_alfred = MagicMock()

# Mock alfred.Item class
class MockItem:
    def __init__(self, title, subtitle, attributes, icon=None):
        self.title = title
        self.subtitle = subtitle
        self.attributes = attributes
        self.icon = icon

mock_alfred.Item = MockItem
mock_alfred.uid = lambda x: f"uid-{x}"

sys.modules['alfred'] = mock_alfred

from process import parse_query_value, parse_interval, parse_datetime_string, alfred_items_for_value


# Interval parsing tests

def test_parse_interval_with_keyword():
    """Test parsing with 'interval' keyword."""
    result = parse_interval('interval 1 day')
    assert result is not None
    assert result.days == 1


def test_parse_interval_without_keyword():
    """Test parsing without 'interval' keyword."""
    result = parse_interval('2 hours')
    assert result is not None
    assert result.seconds == 7200


def test_parse_interval_plural_units():
    """Test parsing with plural units."""
    result = parse_interval('3 weeks')
    assert result is not None
    assert result.days == 21


def test_parse_interval_singular_units():
    """Test parsing with singular units."""
    result = parse_interval('1 second')
    assert result is not None
    assert result.seconds == 1


def test_parse_interval_invalid():
    """Test parsing invalid interval."""
    result = parse_interval('invalid')
    assert result is None


# Datetime string parsing tests

def test_parse_datetime_with_seconds():
    """Test parsing datetime with seconds."""
    result = parse_datetime_string('2026-01-16 10:19:55')
    assert result is not None
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 16
    assert result.hour == 10
    assert result.minute == 19
    assert result.second == 55
    assert result.tzinfo == timezone.utc


def test_parse_datetime_with_milliseconds():
    """Test parsing datetime with milliseconds (they should be preserved)."""
    result = parse_datetime_string('2026-01-16 10:19:55.000')
    assert result is not None
    assert result.year == 2026
    assert result.second == 55
    assert result.microsecond == 0


def test_parse_datetime_iso_format():
    """Test parsing ISO 8601 format."""
    result = parse_datetime_string('2026-01-16T10:19:55')
    assert result is not None
    assert result.year == 2026


def test_parse_datetime_iso_format_with_z():
    """Test parsing ISO 8601 format with milliseconds and Z suffix."""
    result = parse_datetime_string('2026-01-19T08:22:24.709Z')
    assert result is not None
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 19
    assert result.hour == 8
    assert result.minute == 22
    assert result.second == 24
    assert result.microsecond == 709000  # 709 milliseconds = 709000 microseconds
    assert result.tzinfo == timezone.utc


def test_parse_date_only():
    """Test parsing date without time."""
    result = parse_datetime_string('2026-01-16')
    assert result is not None
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 16
    assert result.hour == 0


def test_parse_datetime_invalid():
    """Test parsing invalid datetime string."""
    try:
        parse_datetime_string('invalid-date')
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


# Query value parsing tests

def test_parse_now_keyword():
    """Test parsing 'now' keyword."""
    result = parse_query_value('now')
    assert result is not None
    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc


def test_parse_unix_timestamp_seconds():
    """Test parsing Unix timestamp in seconds."""
    result = parse_query_value('1768558795')
    assert result is not None
    assert int(result.timestamp()) == 1768558795


def test_parse_unix_timestamp_milliseconds():
    """Test parsing Unix timestamp in milliseconds."""
    result = parse_query_value('1768558795000')
    assert result is not None
    assert int(result.timestamp()) == 1768558795


def test_parse_datetime_string():
    """Test parsing datetime string."""
    result = parse_query_value('2026-01-16 10:19:55')
    assert result is not None
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 16


def test_parse_datetime_with_milliseconds():
    """Test parsing datetime string with milliseconds."""
    result = parse_query_value('2026-01-16 10:19:55.000')
    assert result is not None
    assert result.year == 2026


def test_parse_date_only_query():
    """Test parsing date without time."""
    result = parse_query_value('2026-01-16')
    assert result is not None
    assert result.year == 2026


def test_parse_now_minus_interval():
    """Test parsing 'now' minus interval."""
    result = parse_query_value('now - 1 day')
    assert result is not None
    # Result should be approximately 24 hours before now
    now = datetime.now(timezone.utc)
    diff = now - result
    assert diff.days >= 0
    assert diff.days < 2  # Should be close to 1 day


def test_parse_now_plus_interval():
    """Test parsing 'now' plus interval."""
    result = parse_query_value('now + 2 weeks')
    assert result is not None
    # Result should be approximately 14 days after now
    now = datetime.now(timezone.utc)
    diff = result - now
    assert diff.days >= 13
    assert diff.days <= 14  # Should be close to 14 days


def test_parse_datetime_minus_interval():
    """Test parsing datetime string minus interval."""
    result = parse_query_value('2026-01-16 10:19:55 - 3 hours')
    assert result is not None
    assert result.year == 2026
    assert result.month == 1
    assert result.day == 16
    assert result.hour == 7  # 10 - 3 = 7
    assert result.minute == 19


def test_parse_timestamp_minus_interval():
    """Test parsing timestamp minus interval."""
    result = parse_query_value('1768558795 - 1 hour')
    assert result is not None
    # Should be 3600 seconds less
    assert int(result.timestamp()) == 1768558795 - 3600


def test_parse_invalid_input():
    """Test parsing invalid input."""
    result = parse_query_value('completely-invalid-garbage')
    assert result is None


# Alfred item generation tests

def test_generate_items_for_datetime():
    """Test generating Alfred items for a datetime."""
    dt = datetime(2026, 1, 16, 10, 19, 55, tzinfo=timezone.utc)
    items = alfred_items_for_value(dt)

    # Should generate 9 items (timestamp, ms timestamp, + 5 formats + 2 ms formats)
    assert len(items) == 9

    # First item should be UTC timestamp
    assert items[0].title == '1768558795'
    assert items[0].subtitle == 'UTC Timestamp'

    # Second item should be millisecond timestamp
    assert items[1].title == '1768558795000'
    assert items[1].subtitle == 'UTC MilliSecond Timestamp'

    # Check that formatted strings are present
    assert '2026-01-16 10:19:55' in items[2].title
    assert '16 Jan 2026' in items[3].title

    # Check that millisecond formats are present
    assert '2026-01-16 10:19:55.000' in items[7].title
    assert '2026-01-16T10:19:55.000Z' in items[8].title


def test_generate_items_with_milliseconds():
    """Test generating Alfred items with non-zero milliseconds."""
    # Create datetime with 709 milliseconds (709000 microseconds)
    dt = datetime(2026, 1, 19, 8, 22, 24, 709000, tzinfo=timezone.utc)
    items = alfred_items_for_value(dt)

    # Should generate 9 items
    assert len(items) == 9

    # Check that millisecond formats contain correct milliseconds
    assert '2026-01-19 08:22:24.709' in items[7].title
    assert '2026-01-19T08:22:24.709Z' in items[8].title


def test_items_have_required_attributes():
    """Test that all items have required attributes."""
    dt = datetime(2026, 1, 16, 10, 19, 55, tzinfo=timezone.utc)
    items = alfred_items_for_value(dt)

    for item in items:
        assert item.title is not None
        assert item.subtitle is not None
        assert item.attributes is not None
        assert 'uid' in item.attributes
        assert 'arg' in item.attributes


# End-to-end integration tests

def test_all_common_use_cases():
    """Test all common use cases work end-to-end."""
    test_cases = [
        'now',
        '1768558795',
        '1768558795000',
        '2026-01-16 10:19:55',
        '2026-01-16 10:19:55.000',
        '2026-01-16',
        '2026-01-19T08:22:24.709Z',
        'now - 1 day',
        'now + 2 weeks',
        '2026-01-16 10:19:55 - 3 hours',
    ]

    for test_input in test_cases:
        result = parse_query_value(test_input)
        assert result is not None, f"Failed to parse: {test_input}"
        items = alfred_items_for_value(result)
        assert len(items) > 0, f"No items generated for: {test_input}"
