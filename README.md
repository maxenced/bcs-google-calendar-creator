# BCS Calendar creator

## Getting started

Install [mise-en-place](https://mise.jdx.dev/) then run:
```bash
make install
```

Update tools:
```bash
make update
```

Update tooling configuration from [Copier](https://copier.readthedocs.io/en/stable/) template:
```bash
make update-tooling
```

## Usage

### Prerequisites

Before running the script, you need to:

1. **Set up Google Calendar API credentials:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/)
    - Create a new project or select an existing one
    - Enable the Google Calendar API
    - Create credentials (OAuth 2.0 Client ID) for a desktop application
    - Download the credentials file and save it in the project root directory (e.g. `credentials.json`), then reference it with the `credentials_file` key of your configuration file

2. **Install the project dependencies** with `make install` (see [Getting started](#getting-started)), or directly with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

3. **Run from the project root directory:** The script expects to find the credentials file and the configuration files in the current working directory.

### Running the script

Run the script using uv from the project root directory:

```bash
uv run bcs_calendar_creator
```

### Command line options

- `--debug`: Enable debug mode for verbose logging
- `--no-override`: Prevent overriding existing data. If set, overlapping events won't be deleted (default: false, meaning existing events will be overridden)
- `--target <category_key>`: Filter to only process one specific category instead of all categories
- `--prune <category_key>`: Prune all future events in one category
- `-c, --config-path <path>`: Path to the configuration file (default: `src/bcs_calendar_creator/configuration.yaml`)

Examples:
```bash
# Run with debug logging
uv run bcs_calendar_creator --debug

# Process only the "ateliers_level3" category
uv run bcs_calendar_creator --target ateliers_level3

# Run without overriding existing events
uv run bcs_calendar_creator --no-override

# Prune all future events from a specific category (under development)
uv run bcs_calendar_creator --prune ateliers_level3

# Use another configuration file
uv run bcs_calendar_creator -c src/bcs_calendar_creator/configuration.ayr.yaml

# Combine options
uv run bcs_calendar_creator --debug --target cours_n1_mardi --no-override
```

### Configuration format

The script uses [`configuration.yaml`](src/bcs_calendar_creator/configuration.yaml) by default to define calendar events. The configuration file has the following structure:

```yaml
credentials_file: credentials.json  # OAuth client credentials file
categories:
    category_name:
        calendar: "google_calendar_id@group.calendar.google.com"
        default:
            title: "Default event title"
            location: "Default location"
            duration: 60  # Duration in minutes
            start_time: "20h00"  # Format: HHhMM
            description: |
                Multi-line description
                with details about the event
        items:
            - start_day: "16/09/2025"  # Format: DD/MM/YYYY
            - start_day: "23/09/2025"
            title: "Override title for this specific event"
```

#### Categories

Each item in the `categories` dictionary is called a **category**. A category represents a group of related events (e.g., a weekly class, monthly workshops, etc.).

Each category must have:
    - `calendar`: The Google Calendar ID where events will be created
    - `items`: A list of events to create, each with at least a `start_day`

Each category can optionally have:
    - `default`: Default values that will be applied to all items in this category

#### IDs

Each event has a unique ID. This id is generated based on the category name and the calendar name, so script can be sure it only manages events created by it.

#### Event properties

Each event (in `items` or `default`) can have:
    - `title`: Event title (string)
    - `location`: Event location (string)
    - `duration`: Event duration in minutes (integer)
    - `start_time`: Start time in "HHhMM" format (string)
    - `start_day`: Event date in "DD/MM/YYYY" format (string, required for items)
    - `description`: Event description, supports multi-line text (string)

Properties defined in individual items override the corresponding properties from `default`.

### Authentication

On first run, the script will:
    1. Open your web browser for Google OAuth authentication
    2. Create a token file next to the credentials file to store your authentication tokens (e.g. `credentials.ayr.json` → `credentials.ayr.token.json`)
    3. Use the stored tokens for subsequent runs

The token file will be automatically refreshed when needed. Each credentials file has its own token file, so each configuration file can use a different Google account. To log in again with another account, delete the matching token file.

Once logged in, the script logs the Google account actually in use (`Logged in as <email>`), as reported by the Calendar API.
