# Alfred Datetime Format Converter

> Fork of [alexmerkel/alfred-datetime-format-converter](https://github.com/alexmerkel/alfred-datetime-format-converter) with additional functionality

Alfred workflow for converting between timestamps and formatted datetime strings with ease.

## Installation

Download the latest release from the [releases page](https://github.com/trietsch/alfred-datetime-format-converter/releases).

## Usage

Simply type `df` followed by:
- `now` - current timestamp
- A UTC unix timestamp (seconds or milliseconds)
- A formatted datetime string (with or without milliseconds, assumed UTC)
- ISO 8601 format with milliseconds and Z suffix (e.g., `2026-01-19T08:22:24.709Z`)
- **NEW:** `now - interval 1 day` - time arithmetic with intervals
- **NEW:** `now + 3 hours` - add or subtract time

This will present you with the parsed date in various formats ready to copy to your clipboard.

### Examples

```
df now
df 1364302555
df 1737379200000
df 2013-01-15 19:41:06
df 2026-01-16 10:19:55
df 2026-01-16 10:19:55.000
df 2026-01-19T08:22:24.709Z
df now - 1 day
df now - interval 3 hours
df now + 2 weeks
df 1364302555 - 1 hour
df 2026-01-16 10:19:55 - 2 days
```

### Timezone Configuration

You can define your timezone variable in Alfred workflow variables:
- **Name:** `timezone`
- **Value:** pytz timezone string (e.g., `US/Eastern`, `Europe/London`)

If the variable is not set, UTC is used by default.

## New Features in This Fork

- **ISO 8601 with milliseconds:** Full support for parsing and outputting ISO 8601 format with milliseconds (e.g., `2026-01-19T08:22:24.709Z`)
- **Millisecond precision:** Output formats now include millisecond precision timestamps and formatted strings
- **Interval arithmetic:** Add or subtract time from dates using natural language
  - Supported units: seconds, minutes, hours, days, weeks
  - Optional `interval` keyword: both `now - 1 day` and `now - interval 1 day` work
- **Millisecond timestamp copy fix:** The millisecond timestamp can now be properly copied to clipboard
- **Zero external dependencies:** Rewritten to use only Python standard library (no pytz, delorean, etc.)

## Development

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency management and pytest for testing.

### Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.8+

The workflow itself has zero runtime dependencies (only Python stdlib), but development requires pytest.

### Setup

```bash
# Install dependencies
uv sync

# Build the workflow
make workflow

# Install to Alfred (requires alfred_preferences environment variable)
make install
```

### Available Commands

- `make sync` - Install dependencies with uv
- `make vendor` - Vendor dependencies into workflow directory
- `make test` - Run the test suite
- `make workflow` - Build the .alfredworkflow file
- `make install` - Install to your Alfred preferences
- `make clean` - Clean build artifacts

### Testing

The project includes a comprehensive test suite with 25 tests covering:
- Interval parsing (with and without 'interval' keyword)
- Datetime string parsing (various formats including ISO 8601 with milliseconds)
- Unix timestamp parsing (seconds and milliseconds)
- Query value parsing with interval arithmetic
- Alfred item generation (including millisecond precision output)
- End-to-end integration tests

Run tests with:
```bash
make test
# or directly with uv
uv run pytest tests/ -v
```

Tests run automatically in CI before each release.

**Note:** pytest is a dev dependency only and is not included in the workflow bundle.

## Technical Details

This workflow uses only Python's standard library (datetime, timedelta, timezone, re, calendar) with no external dependencies. The workflow is extremely lightweight at ~11KB.

## Acknowledgments

This fork is based on the excellent work by:
- [Michael Waterfall](https://github.com/mwaterfall/alfred-datetime-format-converter) - Original workflow
- [Alex Merkel](https://github.com/alexmerkel/alfred-datetime-format-converter) - Python 3 compatibility

Uses [Alfred Python](https://github.com/nikipore/alfred-python) by Jan Müller (Apache 2.0 License)

## License

Copyright (c) 2013 Michael Waterfall, published under the MIT License

