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

- **Interval arithmetic:** Add or subtract time from dates using natural language
  - Supported units: seconds, minutes, hours, days, weeks
  - Optional `interval` keyword: both `now - 1 day` and `now - interval 1 day` work
- **Millisecond timestamp copy fix:** The millisecond timestamp can now be properly copied to clipboard

## Development

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency management.

### Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.8+

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
- `make workflow` - Build the .alfredworkflow file
- `make install` - Install to your Alfred preferences
- `make clean` - Clean build artifacts

## Acknowledgments

This fork is based on the excellent work by:
- [Michael Waterfall](https://github.com/mwaterfall/alfred-datetime-format-converter) - Original workflow
- [Alex Merkel](https://github.com/alexmerkel/alfred-datetime-format-converter) - Python 3 compatibility

## License

Copyright (c) 2013 Michael Waterfall, published under the MIT License

Includes packages:
* [pytz](https://pythonhosted.org/pytz/) - MIT License
* [tzlocal](https://github.com/regebro/tzlocal) - MIT License
* [alfred-python](https://github.com/nikipore/alfred-python) - Apache 2.0 License
* [delorean](https://github.com/myusuf3/delorean) - MIT License

