# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import re

import alfred
import calendar
from delorean import utcnow, parse, epoch

def get_timezone():
    tz = alfred.env_arg('timezone')
    if not tz:
        tz = 'UTC'
    return tz

def parse_interval(interval_str):
    """
    Parse interval string and return timedelta
    Format: "<number> <unit>" or "interval <number> <unit>"
    Supported units: second(s), minute(s), hour(s), day(s), week(s)
    """
    # Make "interval" keyword optional
    pattern = r'(?:interval\s+)?(\d+)\s+(second|seconds|minute|minutes|hour|hours|day|days|week|weeks)'
    match = re.search(pattern, interval_str, re.IGNORECASE)

    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2).lower()

    # Normalize unit to singular form and map to timedelta kwargs
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

def process(query_str):
    """ Entry point """
    value = parse_query_value(query_str)
    if value is not None:
        results = alfred_items_for_value(value)
        xml = alfred.xml(results) # compiles the XML answer
        alfred.write(xml) # writes the XML back to Alfred

def parse_query_value(query_str):
    """ Return value for the query string """
    try:
        query_str = str(query_str).strip('"\' ')

        # Check for interval expressions (e.g., "now - 1 day" or "now - interval 1 day")
        interval_pattern = r'(.+?)\s*([+-])\s*(?:interval\s+)?(\d+\s+(?:second|seconds|minute|minutes|hour|hours|day|days|week|weeks))'
        interval_match = re.match(interval_pattern, query_str, re.IGNORECASE)

        if interval_match:
            base_str = interval_match.group(1).strip()
            operator = interval_match.group(2)
            interval_str = interval_match.group(3)

            # Parse base datetime
            if base_str == 'now':
                d = utcnow()
            else:
                try:
                    if str(base_str).isdigit() and len(base_str) == 13:
                        base_str = int(base_str) / 1000
                    d = epoch(float(base_str))
                except ValueError:
                    d = parse(str(base_str), get_timezone())

            # Parse and apply interval
            interval = parse_interval(interval_str)
            if interval:
                if operator == '-':
                    d = d - interval
                else:  # operator == '+'
                    d = d + interval
        elif query_str == 'now':
            d = utcnow()
        else:
            # Parse datetime string or timestamp
            try:
                if str(query_str).isdigit() and len(query_str) == 13:
                    query_str = int(query_str) / 1000
                d = epoch(float(query_str))
            except ValueError:
                d = parse(str(query_str), get_timezone())
    except (TypeError, ValueError):
        d = None
    return d

def alfred_items_for_value(value):
    """
    Given a delorean datetime object, return a list of
    alfred items for each of the results
    """

    index = 0
    results = []

    # First item as timestamp
    item_value = calendar.timegm(value.datetime.utctimetuple())
    results.append(alfred.Item(
        title=str(item_value),
        subtitle=u'UTC Timestamp',
        attributes={
            'uid': alfred.uid(index),
            'arg': item_value,
        },
        icon='icon.png',
    ))
    index += 1

    item_value_ms = int(round(datetime.timestamp(value.datetime) * 1000))
    results.append(alfred.Item(
        title=str(item_value_ms),
        subtitle=u'UTC MilliSecond Timestamp',
        attributes={
            'uid': alfred.uid(index),
            'arg': item_value_ms,
        },
        icon='icon.png',
    ))
    index += 1

    # Various formats
    tz = get_timezone()
    formats = [
        # 1937-01-01 12:00:27
        ("%Y-%m-%d %H:%M:%S", tz),
        # 19 May 2002 15:21:36
        ("%d %b %Y %H:%M:%S", tz),
        # Sun, 19 May 2002 15:21:36
        ("%a, %d %b %Y %H:%M:%S", tz),
        # 1937-01-01T12:00:27
        ("%Y-%m-%dT%H:%M:%S", tz),
        # 1996-12-19T16:39:57-0800
        ("%Y-%m-%dT%H:%M:%S%z", tz),
    ]
    for format, description in formats:
        tz_value = value
        if description:
            tz_value = value.shift(description)
        item_value = tz_value.datetime.strftime(format)
        results.append(alfred.Item(
            title=str(item_value),
            subtitle=description,
            attributes={
                'uid': alfred.uid(index),
                'arg': item_value,
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
